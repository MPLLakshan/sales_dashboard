"""
Kaggle Dataset Converter

This script helps convert common Kaggle sales datasets to the format
required by the Sales Dashboard.

Usage:
    python convert_kaggle_data.py input_file.csv output_file.csv
"""

import pandas as pd
import sys
from pathlib import Path


def convert_superstore_dataset(df):
    """
    Convert Superstore dataset format to dashboard format.
    
    Common Superstore columns:
    - Order Date -> date
    - Product Name -> product
    - Region -> region
    - Sales -> revenue
    - Quantity -> quantity
    """
    mapping = {
        'Order Date': 'date',
        'order_date': 'date',
        'OrderDate': 'date',
        'Date': 'date',
        'date': 'date',
        
        'Product Name': 'product',
        'product_name': 'product',
        'Product': 'product',
        'product': 'product',
        'Item': 'product',
        'item': 'product',
        
        'Region': 'region',
        'region': 'region',
        'State': 'region',
        'state': 'region',
        'Country': 'region',
        'country': 'region',
        
        'Sales': 'revenue',
        'sales': 'revenue',
        'Revenue': 'revenue',
        'revenue': 'revenue',
        'Amount': 'revenue',
        'amount': 'revenue',
        'Total': 'revenue',
        'total': 'revenue',
        
        'Quantity': 'quantity',
        'quantity': 'quantity',
        'Qty': 'quantity',
        'qty': 'quantity',
        'Units': 'quantity',
        'units': 'quantity',
    }
    
    # Create new dataframe with renamed columns
    new_df = pd.DataFrame()
    
    # Try to map each required column
    for required_col in ['date', 'product', 'region', 'revenue', 'quantity']:
        found = False
        for original_col, target_col in mapping.items():
            if original_col in df.columns and target_col == required_col:
                new_df[required_col] = df[original_col]
                found = True
                print(f"✓ Mapped '{original_col}' → '{required_col}'")
                break
        
        if not found:
            print(f"✗ Warning: Could not find column for '{required_col}'")
            print(f"  Available columns: {list(df.columns)}")
            return None
    
    return new_df


def convert_date_format(df):
    """Convert date column to YYYY-MM-DD format."""
    if 'date' in df.columns:
        try:
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            print("✓ Date format converted to YYYY-MM-DD")
        except Exception as e:
            print(f"⚠ Warning: Could not convert date format: {e}")
            print("  Please ensure dates are in a recognizable format")
    return df


def clean_numeric_columns(df):
    """Clean revenue and quantity columns to ensure they're numeric."""
    for col in ['revenue', 'quantity']:
        if col in df.columns:
            # Remove currency symbols, commas, etc.
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace('$', '', regex=False)
                df[col] = df[col].str.replace(',', '', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
            print(f"✓ Cleaned '{col}' column")
    return df


def main():
    """Main conversion function."""
    if len(sys.argv) < 2:
        print("Usage: python convert_kaggle_data.py input_file.csv [output_file.csv]")
        print("\nExample:")
        print("  python convert_kaggle_data.py superstore.csv sales_data.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'converted_sales_data.csv'
    
    print(f"\n🔄 Converting Kaggle dataset...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}\n")
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"❌ Error: File '{input_file}' not found!")
        sys.exit(1)
    
    try:
        # Read the CSV file with encoding detection
        print("📖 Reading CSV file...")
        
        # Try multiple encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252', 'utf-16']
        df = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(input_file, encoding=encoding)
                used_encoding = encoding
                print(f"✓ Loaded with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                print(f"⚠ Error with {encoding}: {e}")
                continue
        
        if df is None:
            print("❌ Error: Could not read file with any standard encoding")
            print("   Please check if the file is a valid CSV file")
            sys.exit(1)
        
        print(f"✓ Loaded {len(df)} rows, {len(df.columns)} columns")
        print(f"  Columns: {list(df.columns)}\n")
        
        # Convert column names
        print("🔄 Converting column names...")
        df_converted = convert_superstore_dataset(df)
        
        if df_converted is None:
            print("\n❌ Conversion failed. Please check column names manually.")
            print("\n💡 Tip: You can manually rename columns in Excel/Google Sheets:")
            print("   - date: Transaction date")
            print("   - product: Product name")
            print("   - region: Sales region")
            print("   - revenue: Sales amount")
            print("   - quantity: Quantity sold")
            sys.exit(1)
        
        # Convert date format
        print("\n📅 Converting date format...")
        df_converted = convert_date_format(df_converted)
        
        # Clean numeric columns
        print("\n🧹 Cleaning numeric columns...")
        df_converted = clean_numeric_columns(df_converted)
        
        # Remove rows with missing critical data
        initial_rows = len(df_converted)
        df_converted = df_converted.dropna(subset=['date', 'revenue', 'quantity'])
        removed_rows = initial_rows - len(df_converted)
        
        if removed_rows > 0:
            print(f"⚠ Removed {removed_rows} rows with missing data")
        
        # Save converted file
        print(f"\n💾 Saving converted file...")
        df_converted.to_csv(output_file, index=False)
        print(f"✓ Successfully saved to '{output_file}'")
        print(f"  Final dataset: {len(df_converted)} rows, {len(df_converted.columns)} columns")
        
        # Show preview
        print("\n📊 Preview of converted data:")
        print(df_converted.head())
        
        print("\n✅ Conversion complete!")
        print(f"\n🚀 Next steps:")
        print(f"   1. Check the converted file: {output_file}")
        print(f"   2. Run the dashboard: python -m streamlit run app.py")
        print(f"   3. Upload '{output_file}' in the dashboard")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

