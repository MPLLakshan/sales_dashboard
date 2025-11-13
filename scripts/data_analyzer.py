"""
DataAnalyzer Module

This module provides functionality to analyze sales data and calculate KPIs.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional


class DataAnalyzer:
    """
    A class to analyze sales data and calculate key performance indicators.
    
    Attributes:
        df (pd.DataFrame): Cleaned sales data
        logger (logging.Logger): Logger instance for tracking operations
    """
    
    def __init__(self, df: pd.DataFrame) -> None:
        """
        Initialize the DataAnalyzer with a dataframe.
        
        Args:
            df: Cleaned DataFrame containing sales data
        """
        self.df = df.copy()
        self.logger = logging.getLogger(__name__)
    
    def calculate_total_revenue(self) -> float:
        """
        Calculate total revenue from all sales.
        
        Returns:
            Total revenue as a float
        """
        if 'revenue' not in self.df.columns:
            raise ValueError("'revenue' column not found in dataframe")
        
        total_revenue = self.df['revenue'].sum()
        self.logger.info(f"Total revenue calculated: ${total_revenue:,.2f}")
        return total_revenue
    
    def get_top_products(self, n: int = 10) -> pd.DataFrame:
        """
        Get top N products by total sales (revenue).
        
        Args:
            n: Number of top products to return
            
        Returns:
            DataFrame with top products and their total revenue
        """
        if 'product' not in self.df.columns or 'revenue' not in self.df.columns:
            raise ValueError("Required columns 'product' and 'revenue' not found")
        
        top_products = (
            self.df.groupby('product')['revenue']
            .sum()
            .sort_values(ascending=False)
            .head(n)
            .reset_index()
        )
        top_products.columns = ['product', 'total_revenue']
        
        self.logger.info(f"Top {n} products calculated")
        return top_products
    
    def get_region_wise_revenue(self) -> pd.DataFrame:
        """
        Calculate revenue by region.
        
        Returns:
            DataFrame with regions and their total revenue
        """
        if 'region' not in self.df.columns or 'revenue' not in self.df.columns:
            raise ValueError("Required columns 'region' and 'revenue' not found")
        
        region_revenue = (
            self.df.groupby('region')['revenue']
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        region_revenue.columns = ['region', 'total_revenue']
        
        self.logger.info("Region-wise revenue calculated")
        return region_revenue
    
    def calculate_monthly_growth_rate(self) -> pd.DataFrame:
        """
        Calculate monthly revenue growth rate.
        
        Returns:
            DataFrame with monthly revenue and growth rate
        """
        if 'date' not in self.df.columns or 'revenue' not in self.df.columns:
            raise ValueError("Required columns 'date' and 'revenue' not found")
        
        # Ensure date is datetime
        df_temp = self.df.copy()
        df_temp['date'] = pd.to_datetime(df_temp['date'])
        
        # Group by month
        df_temp['year_month'] = df_temp['date'].dt.to_period('M')
        monthly_revenue = (
            df_temp.groupby('year_month')['revenue']
            .sum()
            .reset_index()
        )
        monthly_revenue.columns = ['month', 'revenue']
        monthly_revenue['month'] = monthly_revenue['month'].astype(str)
        
        # Calculate growth rate
        monthly_revenue['growth_rate'] = monthly_revenue['revenue'].pct_change() * 100
        monthly_revenue['growth_rate'] = monthly_revenue['growth_rate'].fillna(0)
        
        self.logger.info("Monthly growth rate calculated")
        return monthly_revenue
    
    def calculate_profit_margin(self, cost_column: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate profit margin analysis.
        
        Args:
            cost_column: Name of the cost column. If None, estimates cost as 60% of revenue.
            
        Returns:
            DataFrame with profit margin analysis
        """
        if 'revenue' not in self.df.columns:
            raise ValueError("'revenue' column not found")
        
        df_temp = self.df.copy()
        
        if cost_column and cost_column in df_temp.columns:
            df_temp['cost'] = df_temp[cost_column]
        else:
            # Estimate cost as 60% of revenue if cost column not available
            df_temp['cost'] = df_temp['revenue'] * 0.6
            self.logger.info("Cost column not found, estimating cost as 60% of revenue")
        
        df_temp['profit'] = df_temp['revenue'] - df_temp['cost']
        df_temp['profit_margin'] = (df_temp['profit'] / df_temp['revenue']) * 100
        
        # Aggregate by product
        profit_analysis = (
            df_temp.groupby('product').agg({
                'revenue': 'sum',
                'cost': 'sum',
                'profit': 'sum',
                'profit_margin': 'mean'
            }).reset_index()
        )
        
        profit_analysis = profit_analysis.sort_values('profit', ascending=False)
        
        self.logger.info("Profit margin analysis completed")
        return profit_analysis
    
    def get_summary_statistics(self) -> Dict:
        """
        Get summary statistics for the sales data.
        
        Returns:
            Dictionary containing summary statistics
        """
        stats = {
            'total_transactions': len(self.df),
            'total_revenue': self.calculate_total_revenue(),
            'average_revenue_per_transaction': self.df['revenue'].mean() if 'revenue' in self.df.columns else 0,
            'unique_products': self.df['product'].nunique() if 'product' in self.df.columns else 0,
            'unique_regions': self.df['region'].nunique() if 'region' in self.df.columns else 0,
            'date_range': {
                'start': str(self.df['date'].min()) if 'date' in self.df.columns else None,
                'end': str(self.df['date'].max()) if 'date' in self.df.columns else None
            }
        }
        
        self.logger.info("Summary statistics calculated")
        return stats

