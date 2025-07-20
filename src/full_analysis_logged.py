"""
Complete A/B Testing Analysis with Comprehensive Logging
Gaming Company Premium Armor Campaign Analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path
from logger_config import setup_logging
from datetime import datetime

class FullABAnalysis:
    def __init__(self, data_path="./data"):
        self.data_path = Path(data_path)
        self.logger = setup_logging("../logs")
        self.results = {}
        
    def load_and_explore_data(self):
        """Load all data and perform initial exploration"""
        self.logger.info("="*80)
        self.logger.info("GAMING COMPANY A/B TEST ANALYSIS - FULL EXECUTION")
        self.logger.info(f"Analysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*80)
        
        # Load datasets
        datasets = {
            "abgroup": ("ABgroup.csv", "Player group assignments"),
            "cash": ("Cash.csv", "In-game currency spending"),
            "cheaters": ("Cheaters.csv", "Known cheaters"),
            "money": ("Money.csv", "Real money payments"),
            "platforms": ("Platforms.csv", "Gaming platforms")
        }
        
        data = {}
        for name, (filename, description) in datasets.items():
            self.logger.info(f"\nLoading {filename}...")
            df = pd.read_csv(self.data_path / filename)
            data[name] = df
            self.logger.info(f"✓ {description}: {len(df):,} rows, {df.shape[1]} columns")
        
        self.logger.info(f"\n✅ All datasets loaded: {sum(len(df) for df in data.values()):,} total rows")
        
        # Fix column naming inconsistency (user_id vs player_id)
        for name, df in data.items():
            if 'user_id' in df.columns and name != 'abgroup':
                df.rename(columns={'user_id': 'player_id'}, inplace=True)
                self.logger.info(f"Renamed user_id to player_id in {name}")
            elif 'user_id' in df.columns and name == 'abgroup':
                df.rename(columns={'user_id': 'player_id'}, inplace=True)
        
        return data
    
    def clean_and_filter_data(self, data):
        """Clean data and remove cheaters"""
        self.logger.info("\n" + "="*60)
        self.logger.info("DATA CLEANING AND CHEATER REMOVAL")
        self.logger.info("="*60)
        
        # Identify actual cheaters (where cheaters column = 1)
        actual_cheaters = data['cheaters'][data['cheaters']['cheaters'] == 1]
        cheater_ids = set(actual_cheaters['player_id'].unique())
        
        self.logger.info(f"Found {len(cheater_ids):,} actual cheaters (cheaters=1)")
        cheater_rate = len(cheater_ids) / len(data['cheaters']) * 100
        self.logger.info(f"Actual cheater rate: {cheater_rate:.3f}% of total players")
        
        # Remove cheaters from all datasets
        cleaned_data = {}
        for name, df in data.items():
            if name == 'cheaters':
                continue  # Don't need cheaters dataset after identification
                
            if 'player_id' in df.columns:
                before_count = len(df)
                df_clean = df[~df['player_id'].isin(cheater_ids)].copy()
                after_count = len(df_clean)
                removed = before_count - after_count
                
                self.logger.info(f"{name}: Removed {removed:,} records ({removed/before_count:.3f}%)")
                cleaned_data[name] = df_clean
            else:
                cleaned_data[name] = df.copy()
        
        # Additional outlier detection on cash spending
        cash_outliers = self._detect_cash_outliers(cleaned_data['cash'])
        
        # Remove cash outliers
        for name, df in cleaned_data.items():
            if 'player_id' in df.columns:
                before_count = len(df)
                df_clean = df[~df['player_id'].isin(cash_outliers)].copy()
                after_count = len(df_clean)
                removed = before_count - after_count
                
                if removed > 0:
                    self.logger.info(f"{name}: Removed {removed:,} additional outliers ({removed/before_count:.3f}%)")
                    cleaned_data[name] = df_clean
        
        return cleaned_data
    
    def _detect_cash_outliers(self, cash_data):
        """Detect statistical outliers in cash spending"""
        self.logger.info("\nDetecting cash spending outliers...")
        
        # Calculate total spending per player
        player_spending = cash_data.groupby('player_id')['cash'].sum()
        
        # Use IQR method for outlier detection
        Q1 = player_spending.quantile(0.25)
        Q3 = player_spending.quantile(0.75)
        IQR = Q3 - Q1
        
        # Define outlier threshold (3 * IQR)
        outlier_threshold = Q3 + 3 * IQR
        
        outliers = player_spending[player_spending > outlier_threshold].index.tolist()
        
        self.logger.info(f"Cash spending outlier threshold: {outlier_threshold:,.0f}")
        self.logger.info(f"Detected {len(outliers):,} spending outliers")
        
        return set(outliers)
    
    def analyze_ab_groups(self, cleaned_data):
        """Analyze A/B test groups and calculate key metrics"""
        self.logger.info("\n" + "="*60)
        self.logger.info("A/B TESTING ANALYSIS - KEY METRICS")
        self.logger.info("="*60)
        
        # Validate group distribution
        group_dist = cleaned_data['abgroup']['group'].value_counts()
        self.logger.info("A/B Group Distribution (after cleaning):")
        for group, count in group_dist.items():
            percentage = count / len(cleaned_data['abgroup']) * 100
            self.logger.info(f"  {group}: {count:,} players ({percentage:.1f}%)")
        
        # Calculate ARPU (Average Revenue Per User)
        arpu_results = self._calculate_arpu(cleaned_data)
        
        # Calculate ARPPU (Average Revenue Per Paying User)  
        arppu_results = self._calculate_arppu(cleaned_data)
        
        # Calculate Cash Spending Analysis
        cash_results = self._calculate_cash_metrics(cleaned_data)
        
        # Platform Analysis
        platform_results = self._analyze_by_platform(cleaned_data)
        
        return {
            'group_distribution': group_dist,
            'arpu': arpu_results,
            'arppu': arppu_results,
            'cash': cash_results,
            'platform': platform_results
        }
    
    def _calculate_arpu(self, data):
        """Calculate Average Revenue Per User"""
        self.logger.info("\n--- ARPU Analysis ---")
        
        # Aggregate revenue per player
        player_revenue = data['money'].groupby('player_id')['money'].sum().reset_index()
        
        # Merge with A/B groups
        arpu_data = pd.merge(data['abgroup'], player_revenue, on='player_id', how='left')
        arpu_data['money'] = arpu_data['money'].fillna(0)
        
        # Calculate ARPU by group
        arpu_by_group = arpu_data.groupby('group')['money'].agg([
            'count', 'mean', 'std', 'median'
        ]).round(4)
        
        self.logger.info("ARPU by Group:")
        self.logger.info(str(arpu_by_group))
        
        # Statistical significance test
        control_revenue = arpu_data[arpu_data['group'] == 'control']['money']
        test_revenue = arpu_data[arpu_data['group'] == 'test']['money']
        
        from scipy import stats
        t_stat, p_value = stats.ttest_ind(control_revenue, test_revenue)
        
        self.logger.info(f"\nARPU Statistical Test:")
        self.logger.info(f"  T-statistic: {t_stat:.4f}")
        self.logger.info(f"  P-value: {p_value:.6f}")
        self.logger.info(f"  Significant (p<0.05): {'Yes' if p_value < 0.05 else 'No'}")
        
        return {
            'summary': arpu_by_group,
            'raw_data': arpu_data,
            'test_results': {'t_stat': t_stat, 'p_value': p_value}
        }
    
    def _calculate_arppu(self, data):
        """Calculate Average Revenue Per Paying User"""
        self.logger.info("\n--- ARPPU Analysis ---")
        
        # Get only paying users (money > 0)
        paying_users = data['money'][data['money']['money'] > 0]
        player_revenue = paying_users.groupby('player_id')['money'].sum().reset_index()
        
        # Merge with A/B groups
        arppu_data = pd.merge(data['abgroup'], player_revenue, on='player_id', how='inner')
        
        # Calculate ARPPU by group
        arppu_by_group = arppu_data.groupby('group')['money'].agg([
            'count', 'mean', 'std', 'median'
        ]).round(4)
        
        self.logger.info("ARPPU by Group:")
        self.logger.info(str(arppu_by_group))
        
        # Statistical significance test
        control_revenue = arppu_data[arppu_data['group'] == 'control']['money']
        test_revenue = arppu_data[arppu_data['group'] == 'test']['money']
        
        from scipy import stats
        t_stat, p_value = stats.ttest_ind(control_revenue, test_revenue)
        
        self.logger.info(f"\nARPPU Statistical Test:")
        self.logger.info(f"  T-statistic: {t_stat:.4f}")
        self.logger.info(f"  P-value: {p_value:.6f}")
        self.logger.info(f"  Significant (p<0.05): {'Yes' if p_value < 0.05 else 'No'}")
        
        return {
            'summary': arppu_by_group,
            'raw_data': arppu_data,
            'test_results': {'t_stat': t_stat, 'p_value': p_value}
        }
    
    def _calculate_cash_metrics(self, data):
        """Calculate in-game currency spending metrics"""
        self.logger.info("\n--- Cash Spending Analysis ---")
        
        # Aggregate cash spending per player
        player_cash = data['cash'].groupby('player_id')['cash'].sum().reset_index()
        
        # Merge with A/B groups
        cash_data = pd.merge(data['abgroup'], player_cash, on='player_id', how='left')
        cash_data['cash'] = cash_data['cash'].fillna(0)
        
        # Calculate cash metrics by group
        cash_by_group = cash_data.groupby('group')['cash'].agg([
            'count', 'mean', 'std', 'median'
        ]).round(2)
        
        self.logger.info("Cash Spending by Group:")
        self.logger.info(str(cash_by_group))
        
        # Statistical significance test
        control_cash = cash_data[cash_data['group'] == 'control']['cash']
        test_cash = cash_data[cash_data['group'] == 'test']['cash']
        
        from scipy import stats
        t_stat, p_value = stats.ttest_ind(control_cash, test_cash)
        
        self.logger.info(f"\nCash Spending Statistical Test:")
        self.logger.info(f"  T-statistic: {t_stat:.4f}")
        self.logger.info(f"  P-value: {p_value:.6f}")
        self.logger.info(f"  Significant (p<0.05): {'Yes' if p_value < 0.05 else 'No'}")
        
        return {
            'summary': cash_by_group,
            'raw_data': cash_data,
            'test_results': {'t_stat': t_stat, 'p_value': p_value}
        }
    
    def _analyze_by_platform(self, data):
        """Analyze metrics by platform"""
        self.logger.info("\n--- Platform Analysis ---")
        
        # Platform distribution
        platform_dist = data['platforms']['platform'].value_counts()
        self.logger.info("Platform Distribution:")
        for platform, count in platform_dist.items():
            percentage = count / len(data['platforms']) * 100
            self.logger.info(f"  {platform}: {count:,} players ({percentage:.1f}%)")
        
        # ARPU by platform and group
        player_revenue = data['money'].groupby('player_id')['money'].sum().reset_index()
        platform_data = pd.merge(data['abgroup'], data['platforms'], on='player_id')
        platform_data = pd.merge(platform_data, player_revenue, on='player_id', how='left')
        platform_data['money'] = platform_data['money'].fillna(0)
        
        arpu_by_platform_group = platform_data.groupby(['platform', 'group'])['money'].agg([
            'count', 'mean', 'std'
        ]).round(4)
        
        self.logger.info("\nARPU by Platform and Group:")
        self.logger.info(str(arpu_by_platform_group))
        
        return {
            'distribution': platform_dist,
            'arpu_by_platform_group': arpu_by_platform_group,
            'raw_data': platform_data
        }
    
    def generate_final_report(self, results):
        """Generate final business report and recommendations"""
        self.logger.info("\n" + "="*80)
        self.logger.info("FINAL BUSINESS REPORT AND RECOMMENDATIONS")
        self.logger.info("="*80)
        
        # Extract key metrics
        arpu_control = results['arpu']['summary'].loc['control', 'mean']
        arpu_test = results['arpu']['summary'].loc['test', 'mean']
        arpu_p_value = results['arpu']['test_results']['p_value']
        
        arppu_control = results['arppu']['summary'].loc['control', 'mean']
        arppu_test = results['arppu']['summary'].loc['test', 'mean']
        arppu_p_value = results['arppu']['test_results']['p_value']
        
        cash_control = results['cash']['summary'].loc['control', 'mean']
        cash_test = results['cash']['summary'].loc['test', 'mean']
        cash_p_value = results['cash']['test_results']['p_value']
        
        # Calculate improvements
        arpu_improvement = ((arpu_test - arpu_control) / arpu_control) * 100
        arppu_improvement = ((arppu_test - arppu_control) / arppu_control) * 100
        cash_improvement = ((cash_test - cash_control) / cash_control) * 100
        
        self.logger.info("KEY FINDINGS:")
        self.logger.info("-" * 40)
        self.logger.info(f"ARPU:")
        self.logger.info(f"  Control: ${arpu_control:.4f}")
        self.logger.info(f"  Test: ${arpu_test:.4f}")
        self.logger.info(f"  Improvement: {arpu_improvement:+.2f}%")
        self.logger.info(f"  Statistically Significant: {'Yes' if arpu_p_value < 0.05 else 'No'} (p={arpu_p_value:.6f})")
        
        self.logger.info(f"\nARPPU:")
        self.logger.info(f"  Control: ${arppu_control:.4f}")
        self.logger.info(f"  Test: ${arppu_test:.4f}")
        self.logger.info(f"  Improvement: {arppu_improvement:+.2f}%")
        self.logger.info(f"  Statistically Significant: {'Yes' if arppu_p_value < 0.05 else 'No'} (p={arppu_p_value:.6f})")
        
        self.logger.info(f"\nCash Spending:")
        self.logger.info(f"  Control: {cash_control:.2f} coins")
        self.logger.info(f"  Test: {cash_test:.2f} coins")
        self.logger.info(f"  Improvement: {cash_improvement:+.2f}%")
        self.logger.info(f"  Statistically Significant: {'Yes' if cash_p_value < 0.05 else 'No'} (p={cash_p_value:.6f})")
        
        # Business recommendation
        self.logger.info("\n" + "="*60)
        self.logger.info("BUSINESS RECOMMENDATION")
        self.logger.info("="*60)
        
        significant_metrics = sum([
            arpu_p_value < 0.05,
            arppu_p_value < 0.05,
            cash_p_value < 0.05
        ])
        
        positive_improvements = sum([
            arpu_improvement > 0,
            arppu_improvement > 0,
            cash_improvement > 0
        ])
        
        if significant_metrics >= 2 and positive_improvements >= 2:
            recommendation = "IMPLEMENT CAMPAIGN PERMANENTLY"
            self.logger.info(f"✅ RECOMMENDATION: {recommendation}")
            self.logger.info("The premium armor discount campaign shows statistically significant")
            self.logger.info("positive impact on key revenue metrics and should be rolled out to all players.")
        elif significant_metrics >= 1 and positive_improvements >= 2:
            recommendation = "IMPLEMENT WITH MODIFICATIONS"
            self.logger.info(f"⚠️  RECOMMENDATION: {recommendation}")
            self.logger.info("The campaign shows promise but may benefit from optimization")
            self.logger.info("before full rollout. Consider adjusting discount levels or targeting.")
        else:
            recommendation = "DO NOT IMPLEMENT"
            self.logger.info(f"❌ RECOMMENDATION: {recommendation}")
            self.logger.info("The campaign does not show sufficient positive impact")
            self.logger.info("to justify permanent implementation.")
        
        return {
            'metrics_summary': {
                'arpu_improvement': arpu_improvement,
                'arppu_improvement': arppu_improvement,
                'cash_improvement': cash_improvement,
                'significant_metrics': significant_metrics
            },
            'recommendation': recommendation
        }
    
    def export_results(self, results):
        """Export results to Excel and log files"""
        self.logger.info("\n" + "="*60)
        self.logger.info("EXPORTING RESULTS")
        self.logger.info("="*60)
        
        # Export to Excel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"../reports/ab_test_results_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_filename) as writer:
            # ARPU results
            results['arpu']['summary'].to_excel(writer, sheet_name='ARPU_Summary')
            
            # ARPPU results
            results['arppu']['summary'].to_excel(writer, sheet_name='ARPPU_Summary')
            
            # Cash results
            results['cash']['summary'].to_excel(writer, sheet_name='Cash_Summary')
            
            # Platform analysis
            results['platform']['arpu_by_platform_group'].to_excel(writer, sheet_name='Platform_Analysis')
        
        self.logger.info(f"✅ Excel results exported to: {excel_filename}")
        
        # Save to structured results file
        self.logger.save_results_to_file(results)
        
        log_files = self.logger.get_log_files()
        self.logger.info(f"📄 Detailed logs saved to: {log_files['detailed_log']}")
        self.logger.info(f"📄 Console output saved to: {log_files['console_log']}")
        
        return excel_filename

def run_complete_analysis():
    """Run the complete A/B testing analysis"""
    analyzer = FullABAnalysis()
    
    # Load and explore data
    data = analyzer.load_and_explore_data()
    
    # Clean data
    cleaned_data = analyzer.clean_and_filter_data(data)
    
    # Run A/B analysis
    results = analyzer.analyze_ab_groups(cleaned_data)
    
    # Generate final report
    final_report = analyzer.generate_final_report(results)
    results['final_report'] = final_report
    
    # Export results
    excel_file = analyzer.export_results(results)
    
    analyzer.logger.info("\n" + "="*80)
    analyzer.logger.info("ANALYSIS COMPLETE!")
    analyzer.logger.info(f"Final recommendation: {final_report['recommendation']}")
    analyzer.logger.info("="*80)
    
    return results, excel_file

if __name__ == "__main__":
    results, excel_file = run_complete_analysis() 