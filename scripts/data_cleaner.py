"""
DataCleaner Module

This module provides functionality to clean and preprocess sales data.
"""

import pandas as pd
import numpy as np
import logging
from typing import Optional


class DataCleaner:
    """
    A class to clean and preprocess sales data.
    
    Attributes:
        logger (logging.Logger): Logger instance for tracking operations
    """
    
    def __init__(self) -> None:
        """Initialize the DataCleaner."""
        self.logger = logging.getLogger(__name__)
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate rows from the dataframe.
        
        Args:
            df: DataFrame to clean
            
        Returns:
            DataFrame with duplicates removed
        """
        initial_count = len(df)
        df_cleaned = df.drop_duplicates()
        removed_count = initial_count - len(df_cleaned)
        
        self.logger.info(f"Removed {removed_count} duplicate rows")
        return df_cleaned
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'fill') -> pd.DataFrame:
        """
        Handle missing values in the dataframe.
        
        Args:
            df: DataFrame to clean
            strategy: Strategy to handle missing values ('fill', 'drop', 'interpolate')
                     - 'fill': Fill numeric columns with median, categorical with mode
                     - 'drop': Drop rows with missing values
                     - 'interpolate': Interpolate missing values (for time series)
            
        Returns:
            DataFrame with missing values handled
        """
        initial_missing = df.isnull().sum().sum()
        
        if initial_missing == 0:
            self.logger.info("No missing values found")
            return df
        
        self.logger.info(f"Found {initial_missing} missing values, applying strategy: {strategy}")
        
        df_cleaned = df.copy()
        
        if strategy == 'drop':
            df_cleaned = df_cleaned.dropna()
            self.logger.info(f"Dropped rows with missing values")
            
        elif strategy == 'fill':
            # Fill numeric columns with median
            numeric_columns = df_cleaned.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if df_cleaned[col].isnull().any():
                    median_value = df_cleaned[col].median()
                    df_cleaned[col].fillna(median_value, inplace=True)
                    self.logger.info(f"Filled missing values in '{col}' with median: {median_value}")
            
            # Fill categorical columns with mode
            categorical_columns = df_cleaned.select_dtypes(include=['object']).columns
            for col in categorical_columns:
                if df_cleaned[col].isnull().any():
                    mode_value = df_cleaned[col].mode()[0] if not df_cleaned[col].mode().empty else 'Unknown'
                    df_cleaned[col].fillna(mode_value, inplace=True)
                    self.logger.info(f"Filled missing values in '{col}' with mode: {mode_value}")
        
        elif strategy == 'interpolate':
            # Interpolate for time series data
            numeric_columns = df_cleaned.select_dtypes(include=[np.number]).columns
            for col in numeric_columns:
                if df_cleaned[col].isnull().any():
                    df_cleaned[col].interpolate(method='linear', inplace=True)
                    self.logger.info(f"Interpolated missing values in '{col}'")
        
        remaining_missing = df_cleaned.isnull().sum().sum()
        self.logger.info(f"Remaining missing values: {remaining_missing}")
        
        return df_cleaned
    
    def fix_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fix data types for columns (date, numeric, etc.).
        
        Args:
            df: DataFrame to clean
            
        Returns:
            DataFrame with corrected data types
        """
        df_cleaned = df.copy()
        
        self.logger.info("Fixing data types...")
        
        # Convert date column to datetime
        if 'date' in df_cleaned.columns:
            df_cleaned['date'] = pd.to_datetime(df_cleaned['date'], errors='coerce')
            self.logger.info("Converted 'date' column to datetime")
        
        # Ensure numeric columns are numeric
        numeric_columns = ['revenue', 'quantity']
        for col in numeric_columns:
            if col in df_cleaned.columns:
                df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
                self.logger.info(f"Converted '{col}' column to numeric")
        
        # Ensure categorical columns are strings
        categorical_columns = ['product', 'region']
        for col in categorical_columns:
            if col in df_cleaned.columns:
                df_cleaned[col] = df_cleaned[col].astype(str)
                self.logger.info(f"Converted '{col}' column to string")
        
        return df_cleaned
    
    def remove_outliers(self, df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.DataFrame:
        """
        Remove outliers from a numeric column.
        
        Args:
            df: DataFrame to clean
            column: Column name to check for outliers
            method: Method to detect outliers ('iqr' or 'zscore')
            
        Returns:
            DataFrame with outliers removed
        """
        if column not in df.columns:
            self.logger.warning(f"Column '{column}' not found")
            return df
        
        initial_count = len(df)
        df_cleaned = df.copy()
        
        if method == 'iqr':
            Q1 = df_cleaned[column].quantile(0.25)
            Q3 = df_cleaned[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            df_cleaned = df_cleaned[(df_cleaned[column] >= lower_bound) & 
                                 (df_cleaned[column] <= upper_bound)]
        
        elif method == 'zscore':
            # Calculate z-scores using numpy (no scipy dependency)
            mean = df_cleaned[column].mean()
            std = df_cleaned[column].std()
            if std > 0:
                z_scores = np.abs((df_cleaned[column] - mean) / std)
                df_cleaned = df_cleaned[z_scores < 3]
            else:
                self.logger.warning(f"Cannot calculate z-scores: standard deviation is zero for column '{column}'")
        
        removed_count = initial_count - len(df_cleaned)
        self.logger.info(f"Removed {removed_count} outliers from '{column}' column")
        
        return df_cleaned
    
    def clean_all(self, df: pd.DataFrame, handle_missing_strategy: str = 'fill') -> pd.DataFrame:
        """
        Apply all cleaning operations in sequence.
        
        Args:
            df: DataFrame to clean
            handle_missing_strategy: Strategy for handling missing values
            
        Returns:
            Fully cleaned DataFrame
        """
        self.logger.info("Starting comprehensive data cleaning...")
        
        df_cleaned = df.copy()
        df_cleaned = self.remove_duplicates(df_cleaned)
        df_cleaned = self.fix_data_types(df_cleaned)
        df_cleaned = self.handle_missing_values(df_cleaned, strategy=handle_missing_strategy)
        
        self.logger.info("Data cleaning completed")
        return df_cleaned

