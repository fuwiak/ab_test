"""
Data Cleaning Module for A/B Testing Analysis
Focus on removing cheaters and preparing clean datasets
"""

import pandas as pd
import numpy as np
from scipy import stats

class DataCleaner:
    def __init__(self, data):
        self.data = data
        self.cleaned_data = {}
        
    def remove_known_cheaters(self):
        """Remove players identified in the cheaters dataset"""
        print("=== Removing Known Cheaters ===")
        
        # Get list of known cheater IDs
        cheater_ids = set(self.data['cheaters']['player_id'].unique())
        print(f"Found {len(cheater_ids)} known cheaters")
        
        # Remove cheaters from each dataset
        for name, df in self.data.items():
            if name == 'cheaters':
                continue
                
            if 'player_id' in df.columns:
                before_count = len(df)
                df_clean = df[~df['player_id'].isin(cheater_ids)]
                after_count = len(df_clean)
                removed = before_count - after_count
                
                print(f"  {name}: Removed {removed} records ({removed/before_count:.2%})")
                self.cleaned_data[name] = df_clean
            else:
                self.cleaned_data[name] = df.copy()
        
        return self.cleaned_data
    
    def detect_potential_cheaters(self, cash_data, threshold_multiplier=3):
        """
        Detect potential unidentified cheaters based on spending patterns
        Using statistical outlier detection on cash spending
        """
        print(f"\n=== Detecting Potential Cheaters ===")
        
        # Calculate spending per player
        player_spending = cash_data.groupby('player_id')['cash_amount'].agg([
            'sum', 'mean', 'count'
        ]).reset_index()
        
        # Use IQR method to find outliers
        Q1 = player_spending['sum'].quantile(0.25)
        Q3 = player_spending['sum'].quantile(0.75)
        IQR = Q3 - Q1
        
        # Define outlier threshold
        outlier_threshold = Q3 + threshold_multiplier * IQR
        
        potential_cheaters = player_spending[
            player_spending['sum'] > outlier_threshold
        ]['player_id'].tolist()
        
        print(f"Detected {len(potential_cheaters)} potential cheaters")
        print(f"Outlier threshold (total spending): {outlier_threshold:,.0f}")
        
        return potential_cheaters
    
    def remove_potential_cheaters(self, potential_cheaters):
        """Remove potential cheaters from cleaned datasets"""
        print(f"\n=== Removing Potential Cheaters ===")
        
        for name, df in self.cleaned_data.items():
            if 'player_id' in df.columns:
                before_count = len(df)
                df_clean = df[~df['player_id'].isin(potential_cheaters)]
                after_count = len(df_clean)
                removed = before_count - after_count
                
                print(f"  {name}: Removed {removed} additional records ({removed/before_count:.2%})")
                self.cleaned_data[name] = df_clean
        
        return self.cleaned_data
    
    def validate_ab_groups(self):
        """Validate A/B group assignments and distribution"""
        print(f"\n=== Validating A/B Groups ===")
        
        ab_data = self.cleaned_data['abgroup']
        group_dist = ab_data['group'].value_counts()
        
        print("Group distribution:")
        for group, count in group_dist.items():
            print(f"  {group}: {count:,} players ({count/len(ab_data):.1%})")
        
        return group_dist
    
    def get_final_datasets(self):
        """Return final cleaned datasets ready for analysis"""
        return self.cleaned_data

if __name__ == "__main__":
    from data_loader import DataLoader
    
    # Load data
    loader = DataLoader()
    data = loader.load_all_data()
    
    # Clean data
    cleaner = DataCleaner(data)
    cleaned_data = cleaner.remove_known_cheaters()
    
    # Detect and remove potential cheaters
    potential_cheaters = cleaner.detect_potential_cheaters(cleaned_data['cash'])
    final_data = cleaner.remove_potential_cheaters(potential_cheaters)
    
    # Validate results
    cleaner.validate_ab_groups() 