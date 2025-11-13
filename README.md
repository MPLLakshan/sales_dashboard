# Sales Dashboard

A professional, production-level Sales Dashboard built with Python for analyzing sales data and generating comprehensive visualizations.

## Features

- **Data Loading & Validation**: Robust CSV data loading with validation
- **Data Cleaning**: Automated handling of missing values, duplicates, and data type corrections
- **KPI Analysis**: 
  - Total revenue calculation
  - Top-selling products analysis
  - Region-wise sales breakdown
  - Monthly revenue growth trends
  - Optional profit margin analysis
- **Professional Visualizations**: Clean, publication-ready charts using matplotlib and seaborn
- **Modular OOP Design**: Well-structured, maintainable codebase following best practices

## Project Structure

```
sales_dashboard/
│
├── data/
│   └── sales_data.csv          # Sample sales data
│
├── scripts/
│   ├── data_loader.py          # DataLoader class for CSV loading
│   ├── data_cleaner.py         # DataCleaner class for data preprocessing
│   ├── data_analyzer.py        # DataAnalyzer class for KPI calculations
│   └── visualizer.py           # Visualizer class for chart generation
│
├── app.py                      # Streamlit web application (NEW!)
├── main.py                     # Command-line dashboard entry point
├── README.md                   # Project documentation
└── requirements.txt            # Python dependencies
```

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Streamlit Web App (Recommended)

Run the interactive web dashboard:
```bash
python -m streamlit run app.py
```

**Note**: On Windows, if `streamlit` command is not recognized, use `python -m streamlit` instead.

The app will open in your default web browser. Features include:
- 📁 File upload support
- 🔍 Interactive filters (region, date range, products)
- 📊 Real-time visualizations
- 📈 Interactive charts and metrics

### Option 2: Command Line Interface

Run the dashboard with default settings:
```bash
python main.py
```

Run with custom data file:
```bash
python main.py --data path/to/your/data.csv
```

Include profit margin analysis:
```bash
python main.py --profit
```

Combine both options:
```bash
python main.py --data data/sales_data.csv --profit
```

## Data Format

The CSV file should contain the following columns:

- `date`: Transaction date (YYYY-MM-DD format)
- `product`: Product name
- `region`: Sales region
- `revenue`: Revenue amount (numeric)
- `quantity`: Quantity sold (numeric)

### Example CSV Format

```csv
date,product,region,revenue,quantity
2024-01-15,Product A,North,12500.50,25
2024-01-20,Product B,South,8500.75,17
...
```

## Output

The dashboard generates:

1. **Console Output**: Summary metrics and KPIs printed to console
2. **Visualizations**: Professional charts saved in the `output/` directory:
   - `region_wise_revenue.png` - Bar chart of revenue by region
   - `top_products.png` - Horizontal bar chart of top products
   - `monthly_growth_trend.png` - Line chart showing monthly revenue and growth
   - `profit_margin_analysis.png` - Profit analysis charts (if `--profit` flag is used)
3. **Log File**: `sales_dashboard.log` - Detailed execution log

## Module Documentation

### DataLoader

Loads and validates CSV data files.

**Methods:**
- `load_data()`: Load data from CSV file
- `validate_data(df)`: Validate data structure and quality
- `get_data_info(df)`: Get dataset information

### DataCleaner

Cleans and preprocesses sales data.

**Methods:**
- `remove_duplicates(df)`: Remove duplicate rows
- `handle_missing_values(df, strategy)`: Handle missing values (fill/drop/interpolate)
- `fix_data_types(df)`: Fix data types (date, numeric, categorical)
- `remove_outliers(df, column, method)`: Remove outliers using IQR or Z-score
- `clean_all(df)`: Apply all cleaning operations

### DataAnalyzer

Analyzes data and calculates KPIs.

**Methods:**
- `calculate_total_revenue()`: Calculate total revenue
- `get_top_products(n)`: Get top N products by revenue
- `get_region_wise_revenue()`: Calculate revenue by region
- `calculate_monthly_growth_rate()`: Calculate monthly revenue growth
- `calculate_profit_margin(cost_column)`: Calculate profit margin analysis
- `get_summary_statistics()`: Get comprehensive summary statistics

### Visualizer

Generates professional visualizations.

**Methods:**
- `plot_region_wise_revenue(region_data)`: Bar chart for region revenue
- `plot_top_products(products_data, n)`: Horizontal bar chart for top products
- `plot_monthly_growth_trend(monthly_data)`: Line chart for monthly trends
- `plot_profit_margin_analysis(profit_data)`: Profit margin visualization
- `generate_all_charts(analyzer, include_profit)`: Generate all charts

## Code Quality

- **PEP8 Compliance**: Code follows Python style guidelines
- **Type Hints**: All methods include type annotations
- **Docstrings**: Comprehensive documentation for all classes and methods
- **Exception Handling**: Robust error handling throughout
- **Logging**: Detailed logging for debugging and monitoring

## Requirements

See `requirements.txt` for full list of dependencies:

- pandas >= 1.3.0
- numpy >= 1.21.0
- matplotlib >= 3.4.0
- seaborn >= 0.11.0
- streamlit >= 1.28.0 (for web app)

## Example Output

```
============================================================
SALES DASHBOARD - KEY METRICS
============================================================

📊 SUMMARY STATISTICS
------------------------------------------------------------
Total Transactions: 60
Total Revenue: $852,402.00
Average Revenue per Transaction: $14,206.70
Unique Products: 5
Unique Regions: 4
Date Range: 2024-01-15 to 2024-12-28

🏆 TOP 5 PRODUCTS BY REVENUE
------------------------------------------------------------
1. Product C                    $240,000.00
2. Product A                    $218,000.00
3. Product B                    $172,000.00
...

🌍 REGION-WISE REVENUE
------------------------------------------------------------
East                  $213,000.00 (25.00%)
North                 $213,000.00 (25.00%)
...
```

## Contributing

This is a production-level project following best practices:
- Modular design for easy maintenance
- Comprehensive error handling
- Detailed logging
- Type hints for better code clarity
- Professional documentation

## License

This project is provided as-is for educational and professional use.

## Author

Built with best practices for production-level Python development.

