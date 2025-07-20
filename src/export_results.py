"""
Quick export of A/B test results to Excel for codex documentation
"""
import pandas as pd
from datetime import datetime

# Create summary results
results_summary = {
    'Metric': ['ARPU', 'ARPPU', 'Cash Spending'],
    'Control_Group': [5.8295, 5.8311, 5800.71],
    'Test_Group': [6.1622, 6.1631, 6229.57], 
    'Improvement_Percent': [5.71, 5.69, 7.39],
    'P_Value': ['< 0.000001', '< 0.000001', '< 0.000001'],
    'Statistically_Significant': ['Yes', 'Yes', 'Yes']
}

summary_df = pd.DataFrame(results_summary)

# Platform distribution
platform_summary = {
    'Platform': ['PC', 'PS4', 'Xbox'],
    'Player_Count': [2876408, 2873744, 2884256],
    'Percentage': [33.3, 33.3, 33.4]
}

platform_df = pd.DataFrame(platform_summary)

# Export to Excel
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
excel_filename = f"../reports/ab_test_final_results_{timestamp}.xlsx"

with pd.ExcelWriter(excel_filename) as writer:
    summary_df.to_excel(writer, sheet_name='Key_Metrics_Summary', index=False)
    platform_df.to_excel(writer, sheet_name='Platform_Distribution', index=False)
    
    # Add business recommendation
    recommendation_data = {
        'Analysis_Date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        'Recommendation': ['IMPLEMENT CAMPAIGN PERMANENTLY'],
        'Confidence_Level': ['High - All metrics statistically significant'],
        'Expected_Revenue_Increase': ['5.7% across all key metrics'],
        'Sample_Size': ['8.63M players (4.32M control, 4.31M test)'],
        'Risk_Assessment': ['Low - Validated with p < 0.000001']
    }
    
    recommendation_df = pd.DataFrame(recommendation_data)
    recommendation_df.to_excel(writer, sheet_name='Business_Recommendation', index=False)

print(f"✅ Excel results exported to: {excel_filename}")
print(f"📊 Summary: Premium armor discount campaign should be implemented permanently")
print(f"💰 Expected revenue increase: 5.7% across ARPU/ARPPU")
print(f"🎮 In-game spending increase: 7.4%") 