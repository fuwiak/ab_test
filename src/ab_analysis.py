"""
A/B Testing Analysis Module
Calculate ARPU, ARPPU, and confidence intervals for gaming campaign
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

class ABTestAnalyzer:
    def __init__(self, cleaned_data):
        self.data = cleaned_data
        self.results = {}
        
    def calculate_arpu(self, money_data, abgroup_data, platform_data=None):
        """
        Calculate ARPU (Average Revenue Per User) by group and platform
        """
        print("=== Calculating ARPU ===")
        
        # Merge money data with AB groups
        revenue_by_player = money_data.groupby('player_id')['money_amount'].sum().reset_index()
        revenue_with_groups = pd.merge(revenue_by_player, abgroup_data, on='player_id', how='right')
        
        # Fill NaN values with 0 (non-paying users)
        revenue_with_groups['money_amount'] = revenue_with_groups['money_amount'].fillna(0)
        
        # Add platform info if provided
        if platform_data is not None:
            revenue_with_groups = pd.merge(revenue_with_groups, platform_data, on='player_id', how='left')
        
        # Calculate ARPU by group
        arpu_by_group = revenue_with_groups.groupby('group')['money_amount'].agg([
            'mean', 'std', 'count'
        ]).round(2)
        
        print("ARPU by Group:")
        print(arpu_by_group)
        
        # Calculate ARPU by group and platform if platform data available
        if platform_data is not None:
            arpu_by_platform = revenue_with_groups.groupby(['group', 'platform'])['money_amount'].agg([
                'mean', 'std', 'count'
            ]).round(2)
            
            print("\nARPU by Group and Platform:")
            print(arpu_by_platform)
            
            self.results['arpu_by_platform'] = arpu_by_platform
        
        self.results['arpu_by_group'] = arpu_by_group
        self.results['revenue_data'] = revenue_with_groups
        
        return arpu_by_group
    
    def calculate_arppu(self, money_data, abgroup_data, platform_data=None):
        """
        Calculate ARPPU (Average Revenue Per Paying User) by group and platform
        """
        print("\n=== Calculating ARPPU ===")
        
        # Get only paying users (money_amount > 0)
        paying_users = money_data[money_data['money_amount'] > 0]
        revenue_by_player = paying_users.groupby('player_id')['money_amount'].sum().reset_index()
        revenue_with_groups = pd.merge(revenue_by_player, abgroup_data, on='player_id', how='inner')
        
        # Add platform info if provided
        if platform_data is not None:
            revenue_with_groups = pd.merge(revenue_with_groups, platform_data, on='player_id', how='left')
        
        # Calculate ARPPU by group
        arppu_by_group = revenue_with_groups.groupby('group')['money_amount'].agg([
            'mean', 'std', 'count'
        ]).round(2)
        
        print("ARPPU by Group:")
        print(arppu_by_group)
        
        # Calculate ARPPU by group and platform if platform data available
        if platform_data is not None:
            arppu_by_platform = revenue_with_groups.groupby(['group', 'platform'])['money_amount'].agg([
                'mean', 'std', 'count'
            ]).round(2)
            
            print("\nARPPU by Group and Platform:")
            print(arppu_by_platform)
            
            self.results['arppu_by_platform'] = arppu_by_platform
        
        self.results['arppu_by_group'] = arppu_by_group
        self.results['paying_users_data'] = revenue_with_groups
        
        return arppu_by_group
    
    def calculate_cash_spending(self, cash_data, abgroup_data, platform_data=None):
        """
        Calculate in-game currency spending by group and platform
        """
        print("\n=== Calculating Cash Spending ===")
        
        # Merge cash data with AB groups
        cash_by_player = cash_data.groupby('player_id')['cash_amount'].sum().reset_index()
        cash_with_groups = pd.merge(cash_by_player, abgroup_data, on='player_id', how='right')
        
        # Fill NaN values with 0
        cash_with_groups['cash_amount'] = cash_with_groups['cash_amount'].fillna(0)
        
        # Add platform info if provided
        if platform_data is not None:
            cash_with_groups = pd.merge(cash_with_groups, platform_data, on='player_id', how='left')
        
        # Calculate cash spending by group
        cash_by_group = cash_with_groups.groupby('group')['cash_amount'].agg([
            'mean', 'std', 'count'
        ]).round(2)
        
        print("Cash Spending by Group:")
        print(cash_by_group)
        
        # Calculate by group and platform if platform data available
        if platform_data is not None:
            cash_by_platform = cash_with_groups.groupby(['group', 'platform'])['cash_amount'].agg([
                'mean', 'std', 'count'
            ]).round(2)
            
            print("\nCash Spending by Group and Platform:")
            print(cash_by_platform)
            
            self.results['cash_by_platform'] = cash_by_platform
        
        self.results['cash_by_group'] = cash_by_group
        self.results['cash_data'] = cash_with_groups
        
        return cash_by_group
    
    def calculate_confidence_intervals(self, data, metric_column, group_column='group', confidence=0.95):
        """
        Calculate 95% confidence intervals for metrics by group
        """
        print(f"\n=== Calculating {confidence*100}% Confidence Intervals ===")
        
        alpha = 1 - confidence
        results = {}
        
        for group in data[group_column].unique():
            group_data = data[data[group_column] == group][metric_column]
            
            n = len(group_data)
            mean = group_data.mean()
            std_err = stats.sem(group_data)
            
            # Calculate confidence interval
            ci = stats.t.interval(confidence, n-1, loc=mean, scale=std_err)
            
            results[group] = {
                'mean': mean,
                'ci_lower': ci[0],
                'ci_upper': ci[1],
                'n': n
            }
            
            print(f"{group}: {mean:.2f} [{ci[0]:.2f}, {ci[1]:.2f}] (n={n})")
        
        return results
    
    def test_statistical_significance(self, data, metric_column, group_column='group'):
        """
        Test statistical significance between groups using t-test
        """
        print(f"\n=== Statistical Significance Test ===")
        
        groups = data[group_column].unique()
        if len(groups) != 2:
            print("Warning: More than 2 groups found. Using first two groups for comparison.")
        
        group_a = data[data[group_column] == groups[0]][metric_column]
        group_b = data[data[group_column] == groups[1]][metric_column]
        
        # Perform independent t-test
        t_stat, p_value = stats.ttest_ind(group_a, group_b)
        
        print(f"T-test results for {metric_column}:")
        print(f"  {groups[0]} vs {groups[1]}")
        print(f"  T-statistic: {t_stat:.4f}")
        print(f"  P-value: {p_value:.4f}")
        print(f"  Significant at 0.05 level: {'Yes' if p_value < 0.05 else 'No'}")
        
        return {
            'groups': groups,
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
    
    def create_summary_table(self):
        """
        Create summary table for Excel export
        """
        summary_data = []
        
        if 'arpu_by_group' in self.results:
            for group in self.results['arpu_by_group'].index:
                row = {
                    'Metric': 'ARPU',
                    'Group': group,
                    'Platform': 'All',
                    'Mean': self.results['arpu_by_group'].loc[group, 'mean'],
                    'Count': self.results['arpu_by_group'].loc[group, 'count']
                }
                summary_data.append(row)
        
        summary_df = pd.DataFrame(summary_data)
        return summary_df
    
    def export_results(self, filename="ab_test_results.xlsx"):
        """
        Export all results to Excel file
        """
        with pd.ExcelWriter(f"./reports/{filename}") as writer:
            if 'arpu_by_group' in self.results:
                self.results['arpu_by_group'].to_excel(writer, sheet_name='ARPU_by_Group')
            if 'arppu_by_group' in self.results:
                self.results['arppu_by_group'].to_excel(writer, sheet_name='ARPPU_by_Group')
            if 'cash_by_group' in self.results:
                self.results['cash_by_group'].to_excel(writer, sheet_name='Cash_by_Group')
            
            # Summary table
            summary = self.create_summary_table()
            summary.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"Results exported to ./reports/{filename}")

if __name__ == "__main__":
    from data_loader import DataLoader
    from data_cleaner import DataCleaner
    
    # Load and clean data
    loader = DataLoader()
    data = loader.load_all_data()
    
    cleaner = DataCleaner(data)
    cleaned_data = cleaner.remove_known_cheaters()
    potential_cheaters = cleaner.detect_potential_cheaters(cleaned_data['cash'])
    final_data = cleaner.remove_potential_cheaters(potential_cheaters)
    
    # Run A/B analysis
    analyzer = ABTestAnalyzer(final_data)
    
    # Calculate metrics
    analyzer.calculate_arpu(final_data['money'], final_data['abgroup'], final_data['platforms'])
    analyzer.calculate_arppu(final_data['money'], final_data['abgroup'], final_data['platforms'])
    analyzer.calculate_cash_spending(final_data['cash'], final_data['abgroup'], final_data['platforms'])
    
    # Calculate confidence intervals
    if 'revenue_data' in analyzer.results:
        analyzer.calculate_confidence_intervals(analyzer.results['revenue_data'], 'money_amount')
    
    # Export results
    analyzer.export_results() 