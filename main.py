"""
Sales Dashboard - Main Entry Point

This script integrates all modules to create a complete sales dashboard.
"""

import logging
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent / 'scripts'))

from scripts.data_loader import DataLoader
from scripts.data_cleaner import DataCleaner
from scripts.data_analyzer import DataAnalyzer
from scripts.visualizer import Visualizer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sales_dashboard.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class Dashboard:
    """
    Main Dashboard class that integrates all modules.
    
    Attributes:
        data_path (str): Path to the sales data CSV file
        include_profit (bool): Whether to include profit margin analysis
    """
    
    def __init__(self, data_path: str = 'data/sales_data.csv', include_profit: bool = False) -> None:
        """
        Initialize the Dashboard.
        
        Args:
            data_path: Path to the sales data CSV file
            include_profit: Whether to include profit margin analysis
        """
        self.data_path = data_path
        self.include_profit = include_profit
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.data_loader = None
        self.data_cleaner = DataCleaner()
        self.data_analyzer = None
        self.visualizer = Visualizer()
        
        # Data storage
        self.raw_data = None
        self.cleaned_data = None
    
    def load_data(self) -> None:
        """Load data from CSV file."""
        self.logger.info("=" * 60)
        self.logger.info("STEP 1: Loading Data")
        self.logger.info("=" * 60)
        
        try:
            self.data_loader = DataLoader(self.data_path)
            self.raw_data = self.data_loader.load_data()
            
            # Validate data
            is_valid, issues = self.data_loader.validate_data(self.raw_data)
            if not is_valid:
                self.logger.warning(f"Data validation found issues: {issues}")
                self.logger.warning("Proceeding with cleaning...")
            else:
                self.logger.info("Data validation passed")
            
            # Display data info
            info = self.data_loader.get_data_info(self.raw_data)
            self.logger.info(f"Dataset loaded: {info['total_rows']} rows, {info['total_columns']} columns")
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            raise
    
    def clean_data(self) -> None:
        """Clean and preprocess the data."""
        self.logger.info("=" * 60)
        self.logger.info("STEP 2: Cleaning Data")
        self.logger.info("=" * 60)
        
        try:
            self.cleaned_data = self.data_cleaner.clean_all(
                self.raw_data,
                handle_missing_strategy='fill'
            )
            self.logger.info(f"Data cleaning completed. Final dataset: {len(self.cleaned_data)} rows")
            
        except Exception as e:
            self.logger.error(f"Error cleaning data: {e}")
            raise
    
    def analyze_data(self) -> None:
        """Analyze the cleaned data and calculate KPIs."""
        self.logger.info("=" * 60)
        self.logger.info("STEP 3: Analyzing Data")
        self.logger.info("=" * 60)
        
        try:
            self.data_analyzer = DataAnalyzer(self.cleaned_data)
            
            # Calculate all KPIs
            self.total_revenue = self.data_analyzer.calculate_total_revenue()
            self.top_products = self.data_analyzer.get_top_products(n=10)
            self.region_revenue = self.data_analyzer.get_region_wise_revenue()
            self.monthly_growth = self.data_analyzer.calculate_monthly_growth_rate()
            
            if self.include_profit:
                self.profit_analysis = self.data_analyzer.calculate_profit_margin()
            
            self.summary_stats = self.data_analyzer.get_summary_statistics()
            
            self.logger.info("Data analysis completed")
            
        except Exception as e:
            self.logger.error(f"Error analyzing data: {e}")
            raise
    
    def visualize_data(self) -> None:
        """Generate visualizations for the analyzed data."""
        self.logger.info("=" * 60)
        self.logger.info("STEP 4: Generating Visualizations")
        self.logger.info("=" * 60)
        
        try:
            self.visualizer.generate_all_charts(
                self.data_analyzer,
                include_profit=self.include_profit
            )
            self.logger.info("Visualizations generated successfully")
            
        except Exception as e:
            self.logger.error(f"Error generating visualizations: {e}")
            raise
    
    def print_summary(self) -> None:
        """Print summary metrics to console."""
        self.logger.info("=" * 60)
        self.logger.info("DASHBOARD SUMMARY")
        self.logger.info("=" * 60)
        
        print("\n" + "=" * 60)
        print("SALES DASHBOARD - KEY METRICS")
        print("=" * 60)
        
        # Summary Statistics
        print("\n[SUMMARY STATISTICS]")
        print("-" * 60)
        print(f"Total Transactions: {self.summary_stats['total_transactions']:,}")
        print(f"Total Revenue: ${self.summary_stats['total_revenue']:,.2f}")
        print(f"Average Revenue per Transaction: ${self.summary_stats['average_revenue_per_transaction']:,.2f}")
        print(f"Unique Products: {self.summary_stats['unique_products']}")
        print(f"Unique Regions: {self.summary_stats['unique_regions']}")
        if self.summary_stats['date_range']['start']:
            print(f"Date Range: {self.summary_stats['date_range']['start']} to {self.summary_stats['date_range']['end']}")
        
        # Top Products
        print("\n[TOP 5 PRODUCTS BY REVENUE]")
        print("-" * 60)
        for idx, row in self.top_products.head(5).iterrows():
            print(f"{idx + 1}. {row['product']:30s} ${row['total_revenue']:>12,.2f}")
        
        # Region-wise Revenue
        print("\n[REGION-WISE REVENUE]")
        print("-" * 60)
        for idx, row in self.region_revenue.iterrows():
            percentage = (row['total_revenue'] / self.total_revenue) * 100
            print(f"{row['region']:20s} ${row['total_revenue']:>12,.2f} ({percentage:5.2f}%)")
        
        # Monthly Growth
        print("\n[MONTHLY REVENUE GROWTH]")
        print("-" * 60)
        for idx, row in self.monthly_growth.iterrows():
            growth_icon = "[UP]" if row['growth_rate'] >= 0 else "[DOWN]"
            print(f"{row['month']:15s} Revenue: ${row['revenue']:>12,.2f}  Growth: {growth_icon} {row['growth_rate']:>6.2f}%")
        
        # Profit Analysis (if included)
        if self.include_profit:
            print("\n[TOP 5 PRODUCTS BY PROFIT MARGIN]")
            print("-" * 60)
            for idx, row in self.profit_analysis.head(5).iterrows():
                print(f"{row['product']:30s} Profit: ${row['profit']:>10,.2f}  Margin: {row['profit_margin']:>5.2f}%")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Dashboard generation completed!")
        print("[INFO] Charts saved in 'output/' directory")
        print("=" * 60 + "\n")
    
    def run(self) -> None:
        """Run the complete dashboard pipeline."""
        try:
            self.load_data()
            self.clean_data()
            self.analyze_data()
            self.visualize_data()
            self.print_summary()
            
            self.logger.info("Dashboard pipeline completed successfully")
            
        except Exception as e:
            self.logger.error(f"Dashboard pipeline failed: {e}")
            raise


def main():
    """Main function to run the sales dashboard."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sales Dashboard - Analyze and visualize sales data')
    parser.add_argument(
        '--data',
        type=str,
        default='data/sales_data.csv',
        help='Path to the sales data CSV file (default: data/sales_data.csv)'
    )
    parser.add_argument(
        '--profit',
        action='store_true',
        help='Include profit margin analysis'
    )
    
    args = parser.parse_args()
    
    # Create and run dashboard
    dashboard = Dashboard(data_path=args.data, include_profit=args.profit)
    dashboard.run()


if __name__ == '__main__':
    main()

