"""
Streamlit Sales Dashboard Application

A modern, interactive web application for analyzing sales data.
Integrates with the existing OOP-based sales dashboard modules.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent / 'scripts'))

from scripts.data_loader import DataLoader
from scripts.data_cleaner import DataCleaner
from scripts.data_analyzer import DataAnalyzer
from scripts.visualizer import Visualizer

# Page configuration
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #666;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data_from_upload(uploaded_file):
    """
    Load data from uploaded CSV file with automatic encoding detection.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        DataFrame containing the loaded data
    """
    # List of encodings to try (most common first)
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252', 'utf-16']
    
    for encoding in encodings:
        try:
            # Reset file pointer to beginning
            uploaded_file.seek(0)
            # Try to read with current encoding
            df = pd.read_csv(uploaded_file, encoding=encoding)
            return df, None
        except UnicodeDecodeError:
            # Try next encoding
            continue
        except Exception as e:
            # Other errors (like parsing issues) - return the error
            return None, f"Error reading file with {encoding} encoding: {str(e)}"
    
    # If all encodings failed
    return None, "Could not decode file. Please ensure the file is a valid CSV file."


def map_column_names(df):
    """
    Automatically map common column name variations to required column names.
    
    Args:
        df: DataFrame with original column names
        
    Returns:
        Tuple of (mapped DataFrame, column mapping dictionary)
    """
    # Column mapping dictionary
    column_mapping = {}
    df_columns = list(df.columns)
    
    # Date column mappings (check for date-related keywords)
    date_keywords = ['date']
    for col in df_columns:
        col_lower = col.lower().strip()
        # Look for columns with 'date' in the name
        if 'date' in col_lower:
            # Prefer 'order date' over 'ship date'
            if 'order' in col_lower or 'transaction' in col_lower or 'sale' in col_lower:
                column_mapping[col] = 'date'
                break
            elif 'date' in col_lower and 'date' not in [m for m in column_mapping.values()]:
                column_mapping[col] = 'date'
                break
    
    # Product column mappings - look for 'Product Name' specifically
    for col in df_columns:
        col_lower = col.lower().strip()
        if 'product' in col_lower and 'name' in col_lower:
            column_mapping[col] = 'product'
            break
        elif 'product' in col_lower and 'product' not in [m for m in column_mapping.values()]:
            column_mapping[col] = 'product'
            break
        elif ('item' in col_lower or 'name' in col_lower) and 'product' not in [m for m in column_mapping.values()]:
            column_mapping[col] = 'product'
            break
    
    # Region column mappings - prioritize 'Region' exactly
    # Check all columns and find the best match
    region_found = False
    for col in df_columns:
        col_lower = col.lower().strip()
        # Exact match first
        if col_lower == 'region':
            column_mapping[col] = 'region'
            region_found = True
            break
    
    # If exact match not found, try partial matches
    if not region_found:
        for col in df_columns:
            col_lower = col.lower().strip()
            if 'region' in col_lower:
                column_mapping[col] = 'region'
                region_found = True
                break
    
    # Last resort: use State or Country if Region not found
    if not region_found:
        for col in df_columns:
            col_lower = col.lower().strip()
            if col_lower in ['state', 'country']:
                column_mapping[col] = 'region'
                break
    
    # Revenue column mappings - prioritize 'Sales'
    for col in df_columns:
        col_lower = col.lower().strip()
        if col_lower == 'sales':
            column_mapping[col] = 'revenue'
            break
        elif 'sales' in col_lower and 'revenue' not in [m for m in column_mapping.values()]:
            column_mapping[col] = 'revenue'
            break
        elif col_lower in ['revenue', 'amount', 'total'] and 'revenue' not in [m for m in column_mapping.values()]:
            column_mapping[col] = 'revenue'
            break
    
    # Quantity column mappings
    for col in df_columns:
        col_lower = col.lower().strip()
        if col_lower == 'quantity':
            column_mapping[col] = 'quantity'
            break
        elif 'quantity' in col_lower or col_lower in ['qty', 'units']:
            column_mapping[col] = 'quantity'
            break
    
    # Apply mapping
    if column_mapping:
        df_mapped = df.rename(columns=column_mapping)
        return df_mapped, column_mapping
    else:
        return df, {}


@st.cache_data
def process_data(df):
    """
    Process and clean the data using existing OOP classes.
    
    Args:
        df: Raw DataFrame
        
    Returns:
        Tuple of (cleaned_df, analyzer, error_message, column_mapping_info)
    """
    try:
        # First, try to map column names automatically
        df_mapped, column_mapping = map_column_names(df)
        
        # Check if we have all required columns
        required_columns = ['date', 'product', 'region', 'revenue', 'quantity']
        missing_columns = [col for col in required_columns if col not in df_mapped.columns]
        
        if missing_columns:
            available_columns = list(df.columns)
            mapped_columns = list(df_mapped.columns)
            
            # Show what was attempted to be mapped
            mapping_info = ""
            if column_mapping:
                mapping_info = f"\n\nColumns that were mapped: {column_mapping}\n"
                mapping_info += f"Columns after mapping: {mapped_columns}\n"
            
            error_msg = (
                f"Missing required columns: {missing_columns}\n\n"
                f"Available columns in your file: {available_columns}\n"
                f"{mapping_info}\n"
                f"Please rename your columns to match:\n"
                f"- date (for transaction date) - found: {[c for c in df.columns if 'date' in c.lower()]}\n"
                f"- product (for product name) - found: {[c for c in df.columns if 'product' in c.lower()]}\n"
                f"- region (for sales region) - found: {[c for c in df.columns if 'region' in c.lower()]}\n"
                f"- revenue (for sales amount) - found: {[c for c in df.columns if 'sales' in c.lower() or 'revenue' in c.lower()]}\n"
                f"- quantity (for quantity sold) - found: {[c for c in df.columns if 'quantity' in c.lower()]}\n\n"
                f"Or use the converter script: python convert_kaggle_data.py your_file.csv"
            )
            return None, None, error_msg, None
        
        # Clean data
        cleaner = DataCleaner()
        cleaned_df = cleaner.clean_all(df_mapped, handle_missing_strategy='fill')
        
        # Create analyzer
        analyzer = DataAnalyzer(cleaned_df)
        
        return cleaned_df, analyzer, None, column_mapping
        
    except Exception as e:
        return None, None, str(e), None


def create_region_chart(region_data):
    """Create region-wise revenue bar chart."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax = sns.barplot(
        data=region_data,
        x='region',
        y='total_revenue',
        hue='region',
        palette='viridis',
        legend=False,
        ax=ax
    )
    
    ax.set_title('Region-wise Revenue', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Region', fontsize=12)
    ax.set_ylabel('Total Revenue ($)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    
    # Add value labels on bars
    for container in ax.containers:
        ax.bar_label(container, fmt='$%.0f', rotation=90, padding=3)
    
    plt.tight_layout()
    return fig


def create_top_products_chart(products_data, n=5):
    """Create top products horizontal bar chart."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    top_n = products_data.head(n)
    
    ax = sns.barplot(
        data=top_n,
        y='product',
        x='total_revenue',
        hue='product',
        palette='coolwarm',
        legend=False,
        ax=ax
    )
    
    ax.set_title(f'Top {n} Products by Total Sales', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Total Revenue ($)', fontsize=12)
    ax.set_ylabel('Product', fontsize=12)
    
    # Add value labels
    for i, v in enumerate(top_n['total_revenue']):
        ax.text(v + max(top_n['total_revenue']) * 0.01, i, f'${v:,.0f}',
               va='center', fontsize=9)
    
    plt.tight_layout()
    return fig


def create_monthly_growth_chart(monthly_data):
    """Create monthly revenue growth line chart."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot revenue trend
    ax1.plot(monthly_data['month'], monthly_data['revenue'],
            marker='o', linewidth=2, markersize=8, color='#2E86AB')
    ax1.fill_between(monthly_data['month'], monthly_data['revenue'],
                     alpha=0.3, color='#2E86AB')
    ax1.set_title('Monthly Revenue Trend', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Month', fontsize=11)
    ax1.set_ylabel('Revenue ($)', fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Add value labels
    for i, (month, revenue) in enumerate(zip(monthly_data['month'], monthly_data['revenue'])):
        ax1.annotate(f'${revenue:,.0f}',
                    (i, revenue),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha='center', fontsize=8)
    
    # Plot growth rate
    colors = ['green' if x >= 0 else 'red' for x in monthly_data['growth_rate']]
    ax2.bar(monthly_data['month'], monthly_data['growth_rate'],
           color=colors, alpha=0.7, edgecolor='black', linewidth=1)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    ax2.set_title('Monthly Growth Rate (%)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Month', fontsize=11)
    ax2.set_ylabel('Growth Rate (%)', fontsize=11)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.tick_params(axis='x', rotation=45)
    
    # Add value labels
    for i, (month, growth) in enumerate(zip(monthly_data['month'], monthly_data['growth_rate'])):
        ax2.text(i, growth + (1 if growth >= 0 else -2), f'{growth:.1f}%',
                ha='center', va='bottom' if growth >= 0 else 'top', fontsize=8)
    
    plt.tight_layout()
    return fig


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Sales Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Data Upload")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload your sales data CSV file",
            type=['csv'],
            help="Upload a CSV file with columns: date, product, region, revenue, quantity"
        )
        
        st.markdown("---")
        
        # Filters section (will be populated after data is loaded)
        st.header("🔍 Filters")
        
        # Use default data if no file uploaded
        use_default = st.checkbox("Use sample data", value=False, 
                                 help="Check this to use the default sample data file (data/sales_data.csv)")
        
        # Filter options (will be set after data loads)
        filter_enabled = st.checkbox("Enable filters", value=False,
                                    help="Enable interactive filters for region, date range, and products")
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info("""
        This dashboard analyzes sales data and provides:
        - Total revenue metrics
        - Region-wise analysis
        - Top products by sales
        - Monthly growth trends
        """)
    
    # Initialize session state
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'cleaned_data' not in st.session_state:
        st.session_state.cleaned_data = None
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = None
    
    # Load data
    if uploaded_file is not None:
        # Load from uploaded file
        df, error = load_data_from_upload(uploaded_file)
        
        if error:
            st.error(f"Error loading file: {error}")
            st.stop()
        
        st.session_state.data_loaded = True
        
    elif use_default:
        # Load default sample data
        default_path = Path('data/sales_data.csv')
        if default_path.exists():
            try:
                loader = DataLoader(str(default_path))
                df = loader.load_data()
                st.session_state.data_loaded = True
            except Exception as e:
                st.error(f"Error loading default data: {e}")
                st.stop()
        else:
            st.warning("No file uploaded and default data not found. Please upload a CSV file.")
            st.stop()
    else:
        st.info("👆 **Please upload your CSV file** using the file uploader in the sidebar, or check 'Use sample data' to try the demo.")
        st.markdown("""
        ### 📋 Required CSV Format
        
        Your CSV file must have these columns:
        - `date` - Transaction date (YYYY-MM-DD format)
        - `product` - Product name
        - `region` - Sales region
        - `revenue` - Revenue amount (numeric)
        - `quantity` - Quantity sold (numeric)
        
        See `HOW_TO_USE_YOUR_DATA.md` for detailed instructions.
        """)
        st.stop()
    
    # Process data
    if st.session_state.data_loaded and df is not None:
        cleaned_df, analyzer, error, column_mapping = process_data(df)
        
        if error:
            st.error("❌ **Error processing data**")
            st.error(error)
            
            # Show helpful information
            with st.expander("📋 How to fix this", expanded=True):
                st.markdown("""
                **Option 1: Use the automatic converter script**
                ```bash
                python convert_kaggle_data.py your_file.csv converted_file.csv
                ```
                Then upload the converted file.
                
                **Option 2: Rename columns manually**
                1. Open your CSV file in Excel or Google Sheets
                2. Rename the header row to match exactly:
                   - `date` (for transaction date)
                   - `product` (for product name)
                   - `region` (for sales region)
                   - `revenue` (for sales amount)
                   - `quantity` (for quantity sold)
                3. Save and upload again
                """)
            st.stop()
        
        # Show column mapping info if columns were automatically mapped
        if column_mapping:
            with st.sidebar:
                st.success("✅ Columns automatically mapped!")
                with st.expander("View column mapping"):
                    for original, mapped in column_mapping.items():
                        st.text(f"{original} → {mapped}")
        
        st.session_state.cleaned_data = cleaned_df
        st.session_state.analyzer = analyzer
    
    # Main content
    if st.session_state.data_loaded and st.session_state.analyzer is not None:
        analyzer = st.session_state.analyzer
        cleaned_df = st.session_state.cleaned_data
        
        # Apply filters if enabled
        filtered_df = cleaned_df.copy()
        
        if filter_enabled:
            with st.sidebar:
                st.markdown("### Filter Options")
                
                # Region filter
                if 'region' in cleaned_df.columns:
                    regions = ['All'] + sorted(cleaned_df['region'].unique().tolist())
                    selected_region = st.selectbox("Select Region", regions)
                    if selected_region != 'All':
                        filtered_df = filtered_df[filtered_df['region'] == selected_region]
                
                # Date range filter
                if 'date' in cleaned_df.columns:
                    cleaned_df['date'] = pd.to_datetime(cleaned_df['date'])
                    filtered_df['date'] = pd.to_datetime(filtered_df['date'])
                    min_date = cleaned_df['date'].min().date()
                    max_date = cleaned_df['date'].max().date()
                    
                    date_range = st.date_input(
                        "Select Date Range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )
                    
                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        filtered_df = filtered_df[
                            (filtered_df['date'].dt.date >= start_date) &
                            (filtered_df['date'].dt.date <= end_date)
                        ]
                
                # Product filter
                if 'product' in cleaned_df.columns:
                    products = ['All'] + sorted(cleaned_df['product'].unique().tolist())
                    selected_products = st.multiselect("Select Products", products, default=['All'])
                    if 'All' not in selected_products and selected_products:
                        filtered_df = filtered_df[filtered_df['product'].isin(selected_products)]
                
                # Update analyzer with filtered data
                if len(filtered_df) > 0:
                    analyzer = DataAnalyzer(filtered_df)
                    st.success(f"Filters applied: {len(filtered_df)} rows")
                else:
                    st.warning("No data matches the selected filters.")
                    st.stop()
        
        # Project description
        with st.expander("ℹ️ About This Dashboard", expanded=False):
            st.markdown("""
            **Sales Dashboard** is a comprehensive analytics tool that provides insights into your sales performance.
            
            **Features:**
            - 📈 Real-time data analysis and visualization
            - 🎯 Key Performance Indicators (KPIs)
            - 📊 Interactive charts and graphs
            - 🔍 Data filtering and exploration
            
            **Data Requirements:**
            Your CSV file should contain the following columns:
            - `date`: Transaction date (YYYY-MM-DD format)
            - `product`: Product name
            - `region`: Sales region
            - `revenue`: Revenue amount (numeric)
            - `quantity`: Quantity sold (numeric)
            """)
        
        st.markdown("---")
        
        # Data Preview Section
        st.header("📋 Data Preview")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.dataframe(cleaned_df.head(10), use_container_width=True)
        
        with col2:
            st.metric("Total Rows", f"{len(cleaned_df):,}")
            st.metric("Total Columns", len(cleaned_df.columns))
        
        st.markdown("---")
        
        # Summary Statistics Section
        st.header("📊 Summary Statistics")
        summary_stats = analyzer.get_summary_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Revenue",
                f"${summary_stats['total_revenue']:,.2f}",
                help="Sum of all revenue from transactions"
            )
        
        with col2:
            st.metric(
                "Total Transactions",
                f"{summary_stats['total_transactions']:,}",
                help="Total number of sales transactions"
            )
        
        with col3:
            st.metric(
                "Avg Revenue/Transaction",
                f"${summary_stats['average_revenue_per_transaction']:,.2f}",
                help="Average revenue per transaction"
            )
        
        with col4:
            st.metric(
                "Unique Products",
                summary_stats['unique_products'],
                help="Number of unique products"
            )
        
        # Additional stats
        col5, col6, col7 = st.columns(3)
        
        with col5:
            st.metric("Unique Regions", summary_stats['unique_regions'])
        
        with col6:
            if summary_stats['date_range']['start']:
                start_date = pd.to_datetime(summary_stats['date_range']['start']).strftime('%Y-%m-%d')
                st.metric("Start Date", start_date)
        
        with col7:
            if summary_stats['date_range']['end']:
                end_date = pd.to_datetime(summary_stats['date_range']['end']).strftime('%Y-%m-%d')
                st.metric("End Date", end_date)
        
        st.markdown("---")
        
        # Visualizations Section
        st.header("📈 Visualizations")
        
        # Region-wise Revenue
        st.subheader("🌍 Region-wise Revenue")
        try:
            region_data = analyzer.get_region_wise_revenue()
            fig_region = create_region_chart(region_data)
            st.pyplot(fig_region)
            plt.close(fig_region)
        except Exception as e:
            st.error(f"Error creating region chart: {e}")
        
        st.markdown("---")
        
        # Top Products
        st.subheader("🏆 Top Products by Sales")
        try:
            top_products = analyzer.get_top_products(n=10)
            fig_products = create_top_products_chart(top_products, n=5)
            st.pyplot(fig_products)
            plt.close(fig_products)
            
            # Display top products table
            with st.expander("View Top 10 Products Table"):
                st.dataframe(top_products, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating products chart: {e}")
        
        st.markdown("---")
        
        # Monthly Growth Trend
        st.subheader("📈 Monthly Revenue Growth Trend")
        try:
            monthly_data = analyzer.calculate_monthly_growth_rate()
            fig_monthly = create_monthly_growth_chart(monthly_data)
            st.pyplot(fig_monthly)
            plt.close(fig_monthly)
            
            # Display monthly data table
            with st.expander("View Monthly Data Table"):
                st.dataframe(monthly_data, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating monthly chart: {e}")
        
        st.markdown("---")
        
        # Additional Analysis Section
        st.header("🔍 Additional Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Region Breakdown")
            try:
                region_data = analyzer.get_region_wise_revenue()
                total_revenue = analyzer.calculate_total_revenue()
                
                # Create pie chart for regions
                fig_pie, ax = plt.subplots(figsize=(8, 8))
                ax.pie(region_data['total_revenue'], 
                      labels=region_data['region'],
                      autopct='%1.1f%%',
                      startangle=90,
                      colors=sns.color_palette('viridis', len(region_data)))
                ax.set_title('Revenue Distribution by Region', fontsize=14, fontweight='bold')
                st.pyplot(fig_pie)
                plt.close(fig_pie)
            except Exception as e:
                st.error(f"Error creating pie chart: {e}")
        
        with col2:
            st.subheader("Product Performance")
            try:
                top_products = analyzer.get_top_products(n=5)
                
                # Display as table with formatting
                display_df = top_products.copy()
                display_df['total_revenue'] = display_df['total_revenue'].apply(lambda x: f"${x:,.2f}")
                display_df.columns = ['Product', 'Total Revenue']
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Error displaying product performance: {e}")
        
        st.markdown("---")
        
        # Footer
        st.markdown("---")
        st.markdown(
            '<div class="footer">Developed by <strong>Gihan Sanjula</strong> | Sales Dashboard v1.0</div>',
            unsafe_allow_html=True
        )
    
    else:
        st.info("Please upload a CSV file to begin analysis.")


if __name__ == "__main__":
    main()

