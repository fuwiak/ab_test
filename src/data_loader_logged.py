"""
Data Loading Module with Logging for A/B Testing Analysis
Gaming Company Premium Armor Campaign Analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path
from logger_config import setup_logging

class DataLoaderLogged:
    def __init__(self, data_path="./data"):
        self.data_path = Path(data_path)
        self.logger = setup_logging("../logs")
        
    def load_all_data(self):
        """Load all CSV files and return as dictionary of DataFrames"""
        self.logger.info("="*60)
        self.logger.info("STARTING A/B TESTING DATA ANALYSIS")
        self.logger.info("="*60)
        
        data = {}
        
        # Load each dataset
        self.logger.info("Loading datasets...")
        
        datasets = [
            ("abgroup", "ABgroup.csv", "Player group assignments"),
            ("cash", "Cash.csv", "In-game currency spending"),
            ("cheaters", "Cheaters.csv", "Known cheaters"),
            ("money", "Money.csv", "Real money payments"),
            ("platforms", "Platforms.csv", "Gaming platforms")
        ]
        
        for name, filename, description in datasets:
            self.logger.info(f"\nLoading {filename} ({description})...")
            file_path = self.data_path / filename
            
            if not file_path.exists():
                self.logger.error(f"File not found: {file_path}")
                continue
                
            try:
                df = pd.read_csv(file_path)
                data[name] = df
                self.logger.info(f"✓ Loaded {filename}: {df.shape[0]:,} rows, {df.shape[1]} columns")
                
                # Log detailed information about each dataset
                self.logger.log_dataframe(df, f"{name.upper()} ({description})", sample_rows=5)
                
            except Exception as e:
                self.logger.error(f"Error loading {filename}: {str(e)}")
        
        self.logger.info(f"\n✓ All datasets loaded successfully!")
        self.logger.info(f"Total datasets: {len(data)}")
        
        # Log overall data summary
        self._log_data_summary(data)
        
        return data
    
    def _log_data_summary(self, data):
        """Log summary statistics about all datasets"""
        self.logger.info("\n" + "="*50)
        self.logger.info("DATA SUMMARY")
        self.logger.info("="*50)
        
        total_rows = sum(len(df) for df in data.values())
        total_memory = sum(df.memory_usage(deep=True).sum() for df in data.values()) / 1024**2
        
        self.logger.info(f"Total rows across all datasets: {total_rows:,}")
        self.logger.info(f"Total memory usage: {total_memory:.1f} MB")
        
        for name, df in data.items():
            self.logger.info(f"\n{name.upper()}:")
            self.logger.info(f"  - Rows: {len(df):,}")
            self.logger.info(f"  - Columns: {df.shape[1]}")
            self.logger.info(f"  - Memory: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
            
            # Check for common ID columns
            if 'player_id' in df.columns:
                unique_players = df['player_id'].nunique()
                self.logger.info(f"  - Unique players: {unique_players:,}")
                
            # Check for missing values
            missing = df.isnull().sum().sum()
            if missing > 0:
                self.logger.info(f"  - Missing values: {missing:,}")
    
    def validate_data_integrity(self, data):
        """Validate data integrity and relationships"""
        self.logger.info("\n" + "="*50)
        self.logger.info("DATA INTEGRITY VALIDATION")
        self.logger.info("="*50)
        
        # Check player_id consistency across datasets
        datasets_with_players = ['abgroup', 'cash', 'money', 'platforms']
        player_counts = {}
        
        for name in datasets_with_players:
            if name in data and 'player_id' in data[name].columns:
                player_counts[name] = set(data[name]['player_id'].unique())
                self.logger.info(f"{name}: {len(player_counts[name]):,} unique players")
        
        # Find overlaps and differences
        if len(player_counts) > 1:
            all_players = set.union(*player_counts.values())
            self.logger.info(f"\nTotal unique players across all datasets: {len(all_players):,}")
            
            # Check for players in each dataset
            for name, players in player_counts.items():
                coverage = len(players) / len(all_players) * 100
                self.logger.info(f"{name} coverage: {coverage:.1f}% of all players")
        
        # Validate group assignments
        if 'abgroup' in data:
            group_dist = data['abgroup']['group'].value_counts()
            self.logger.info(f"\nA/B Group Distribution:")
            for group, count in group_dist.items():
                percentage = count / len(data['abgroup']) * 100
                self.logger.info(f"  {group}: {count:,} players ({percentage:.1f}%)")
        
        # Validate cheaters
        if 'cheaters' in data:
            cheater_count = len(data['cheaters'])
            self.logger.info(f"\nKnown cheaters: {cheater_count:,}")
            
            if 'abgroup' in data:
                total_players = len(data['abgroup'])
                cheater_percentage = cheater_count / total_players * 100
                self.logger.info(f"Cheater rate: {cheater_percentage:.2f}% of total players")

if __name__ == "__main__":
    loader = DataLoaderLogged()
    data = loader.load_all_data()
    loader.validate_data_integrity(data) 