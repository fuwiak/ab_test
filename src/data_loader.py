"""
Data Loading Module for A/B Testing Analysis
Gaming Company Premium Armor Campaign Analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path

class DataLoader:
    def __init__(self, data_path="./data"):
        self.data_path = Path(data_path)
        
    def load_all_data(self):
        """Load all CSV files and return as dictionary of DataFrames"""
        data = {}
        
        # Load each dataset
        print("Loading datasets...")
        data['abgroup'] = pd.read_csv(self.data_path / "ABgroup.csv")
        data['cash'] = pd.read_csv(self.data_path / "Cash.csv") 
        data['cheaters'] = pd.read_csv(self.data_path / "Cheaters.csv")
        data['money'] = pd.read_csv(self.data_path / "Money.csv")
        data['platforms'] = pd.read_csv(self.data_path / "Platforms.csv")
        
        print("✓ All datasets loaded successfully!")
        self.print_dataset_info(data)
        
        return data
    
    def print_dataset_info(self, data):
        """Print basic information about each dataset"""
        print("\n=== Dataset Information ===")
        for name, df in data.items():
            print(f"\n{name.upper()}:")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            if len(df.columns) <= 5:
                print(f"  Sample:\n{df.head(2)}")
    
    def get_sample_data(self, data, sample_size=1000):
        """Get sample of data for initial exploration"""
        sample_data = {}
        for name, df in data.items():
            if len(df) > sample_size:
                sample_data[name] = df.sample(n=sample_size, random_state=42)
            else:
                sample_data[name] = df.copy()
        return sample_data

if __name__ == "__main__":
    loader = DataLoader()
    data = loader.load_all_data() 