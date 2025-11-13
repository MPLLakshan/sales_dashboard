"""
Visualizer Module

This module provides functionality to create professional visualizations for sales data.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import logging
from typing import Optional
from pathlib import Path


class Visualizer:
    """
    A class to generate professional visualizations for sales data.
    
    Attributes:
        output_dir (Path): Directory to save generated charts
        logger (logging.Logger): Logger instance for tracking operations
    """
    
    def __init__(self, output_dir: str = 'output') -> None:
        """
        Initialize the Visualizer with an output directory.
        
        Args:
            output_dir: Directory path to save generated charts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 10
    
    def plot_region_wise_revenue(self, region_data: pd.DataFrame, save: bool = True) -> None:
        """
        Create a bar chart for region-wise revenue.
        
        Args:
            region_data: DataFrame with 'region' and 'total_revenue' columns
            save: Whether to save the chart to file
        """
        plt.figure(figsize=(10, 6))
        
        ax = sns.barplot(
            data=region_data,
            x='region',
            y='total_revenue',
            hue='region',
            palette='viridis',
            legend=False
        )
        
        plt.title('Region-wise Revenue', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Region', fontsize=12)
        plt.ylabel('Total Revenue ($)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for container in ax.containers:
            ax.bar_label(container, fmt='$%.0f', rotation=90, padding=3)
        
        plt.tight_layout()
        
        if save:
            filepath = self.output_dir / 'region_wise_revenue.png'
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved chart to {filepath}")
        
        plt.show()
    
    def plot_top_products(self, products_data: pd.DataFrame, n: int = 10, save: bool = True) -> None:
        """
        Create a horizontal bar chart for top products by sales.
        
        Args:
            products_data: DataFrame with 'product' and 'total_revenue' columns
            n: Number of top products to display
            save: Whether to save the chart to file
        """
        plt.figure(figsize=(10, 8))
        
        top_n = products_data.head(n)
        
        ax = sns.barplot(
            data=top_n,
            y='product',
            x='total_revenue',
            hue='product',
            palette='coolwarm',
            legend=False
        )
        
        plt.title(f'Top {n} Products by Total Sales', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Total Revenue ($)', fontsize=12)
        plt.ylabel('Product', fontsize=12)
        
        # Add value labels on bars
        for i, v in enumerate(top_n['total_revenue']):
            ax.text(v + max(top_n['total_revenue']) * 0.01, i, f'${v:,.0f}', 
                   va='center', fontsize=9)
        
        plt.tight_layout()
        
        if save:
            filepath = self.output_dir / 'top_products.png'
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved chart to {filepath}")
        
        plt.show()
    
    def plot_monthly_growth_trend(self, monthly_data: pd.DataFrame, save: bool = True) -> None:
        """
        Create a line chart showing monthly revenue growth trends.
        
        Args:
            monthly_data: DataFrame with 'month', 'revenue', and 'growth_rate' columns
            save: Whether to save the chart to file
        """
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
                        xytext=(0,10), 
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
        
        if save:
            filepath = self.output_dir / 'monthly_growth_trend.png'
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved chart to {filepath}")
        
        plt.show()
    
    def plot_profit_margin_analysis(self, profit_data: pd.DataFrame, n: int = 10, save: bool = True) -> None:
        """
        Create a visualization for profit margin analysis.
        
        Args:
            profit_data: DataFrame with profit margin analysis
            n: Number of top products to display
            save: Whether to save the chart to file
        """
        top_n = profit_data.head(n)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Plot profit by product
        ax1.barh(top_n['product'], top_n['profit'], color='#06A77D', alpha=0.8)
        ax1.set_title('Top Products by Profit', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Profit ($)', fontsize=11)
        ax1.set_ylabel('Product', fontsize=11)
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, v in enumerate(top_n['profit']):
            ax1.text(v + max(top_n['profit']) * 0.01, i, f'${v:,.0f}',
                    va='center', fontsize=9)
        
        # Plot profit margin by product
        colors = ['green' if x >= 30 else 'orange' if x >= 20 else 'red' 
                 for x in top_n['profit_margin']]
        ax2.barh(top_n['product'], top_n['profit_margin'], color=colors, alpha=0.8)
        ax2.set_title('Profit Margin by Product (%)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Profit Margin (%)', fontsize=11)
        ax2.set_ylabel('Product', fontsize=11)
        ax2.axvline(x=20, color='red', linestyle='--', linewidth=1, label='20% Threshold')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, v in enumerate(top_n['profit_margin']):
            ax2.text(v + 1, i, f'{v:.1f}%',
                    va='center', fontsize=9)
        
        plt.tight_layout()
        
        if save:
            filepath = self.output_dir / 'profit_margin_analysis.png'
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            self.logger.info(f"Saved chart to {filepath}")
        
        plt.show()
    
    def generate_all_charts(self, analyzer, include_profit: bool = False) -> None:
        """
        Generate all standard charts for the sales dashboard.
        
        Args:
            analyzer: DataAnalyzer instance with analyzed data
            include_profit: Whether to include profit margin analysis
        """
        self.logger.info("Generating all charts...")
        
        # Region-wise revenue
        region_data = analyzer.get_region_wise_revenue()
        self.plot_region_wise_revenue(region_data, save=True)
        
        # Top products
        products_data = analyzer.get_top_products()
        self.plot_top_products(products_data, save=True)
        
        # Monthly growth trend
        monthly_data = analyzer.calculate_monthly_growth_rate()
        self.plot_monthly_growth_trend(monthly_data, save=True)
        
        # Profit margin (optional)
        if include_profit:
            try:
                profit_data = analyzer.calculate_profit_margin()
                self.plot_profit_margin_analysis(profit_data, save=True)
            except Exception as e:
                self.logger.warning(f"Could not generate profit margin chart: {e}")
        
        self.logger.info("All charts generated successfully")

