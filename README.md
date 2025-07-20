# A/B Testing Analysis - Gaming Premium Armor Campaign

## Project Overview
Analysis of A/B test results for a premium armor discount campaign in a team-based online shooter game. The goal is to determine if the discount campaign should be implemented permanently based on its impact on key revenue metrics.

## Project Structure
```
AB_test/
├── data/                   # CSV data files
│   ├── ABgroup.csv        # Player group assignments
│   ├── Cash.csv           # In-game currency spending
│   ├── Cheaters.csv       # Known cheaters
│   ├── Money.csv          # Real money payments
│   └── Platforms.csv      # Gaming platforms (PC, PS4, Xbox)
├── src/                   # Source code
│   ├── data_loader.py     # Data loading utilities
│   ├── data_cleaner.py    # Data cleaning and cheater removal
│   └── ab_analysis.py     # Main A/B testing analysis
├── notebooks/             # Jupyter notebooks for exploration
├── reports/               # Analysis reports and results
└── requirements.txt       # Python dependencies
```

## Key Metrics to Analyze
- **ARPU** (Average Revenue Per User): Total revenue / Total users
- **ARPPU** (Average Revenue Per Paying User): Total revenue / Paying users only
- **In-game Currency Spending**: Virtual currency usage patterns

## Analysis Steps

### 1. Data Loading
```python
from src.data_loader import DataLoader
loader = DataLoader()
data = loader.load_all_data()
```

### 2. Data Cleaning
- Remove known cheaters from cheaters.csv
- Detect potential unidentified cheaters using statistical outlier detection
- Validate A/B group distributions

```python
from src.data_cleaner import DataCleaner
cleaner = DataCleaner(data)
cleaned_data = cleaner.remove_known_cheaters()
potential_cheaters = cleaner.detect_potential_cheaters(cleaned_data['cash'])
final_data = cleaner.remove_potential_cheaters(potential_cheaters)
```

### 3. A/B Testing Analysis
- Calculate ARPU, ARPPU, and cash spending by group and platform
- Generate 95% confidence intervals
- Perform statistical significance testing

```python
from src.ab_analysis import ABTestAnalyzer
analyzer = ABTestAnalyzer(final_data)
analyzer.calculate_arpu(final_data['money'], final_data['abgroup'], final_data['platforms'])
analyzer.calculate_arppu(final_data['money'], final_data['abgroup'], final_data['platforms'])
analyzer.calculate_cash_spending(final_data['cash'], final_data['abgroup'], final_data['platforms'])
```

### 4. Results Export
- Excel summary tables with ARPU by groups and platforms
- Statistical test results
- Confidence interval analysis

## Installation

1. Create and activate virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Running the Analysis

### Option 1: Run Complete Analysis
```bash
cd src
python ab_analysis.py
```

### Option 2: Step by Step
```bash
cd src
python data_loader.py      # Load and inspect data
python data_cleaner.py     # Clean data and remove cheaters
python ab_analysis.py      # Run full A/B analysis
```

### Option 3: Interactive Analysis
Use the Jupyter notebooks in the `notebooks/` directory for interactive exploration.

## Expected Deliverables

1. **Statistical Analysis Report** with:
   - ARPU/ARPPU comparisons between test and control groups
   - 95% confidence intervals for all metrics
   - Platform-specific analysis (PC, PS4, Xbox)
   - Statistical significance testing results

2. **Excel Summary Tables** showing:
   - ARPU by groups and platforms
   - Detailed metrics breakdown
   - Sample sizes and statistical power

3. **Visualizations** including:
   - Daily metric trends
   - Group comparisons
   - Platform performance differences

4. **Recommendations** on whether to:
   - Implement the discount campaign permanently
   - Modify the campaign structure
   - Discontinue the campaign

## Key Questions to Answer

1. Did the premium armor discount significantly increase ARPU?
2. How did ARPPU change between test and control groups?
3. Did in-game currency spending patterns change?
4. Are there platform-specific differences in campaign effectiveness?
5. Are the observed differences statistically significant?
6. Should this campaign be rolled out to all players?

## Notes
- All cheater detection and removal methods are documented in the cleaning module
- Confidence intervals help determine if differences are statistically meaningful
- Platform analysis may reveal important segment-specific insights
- Sample sizes and statistical power should be considered in final recommendations 