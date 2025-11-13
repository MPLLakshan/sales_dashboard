"""
DataLoader Module

This module provides functionality to load and validate sales data from CSV files.
"""

import pandas as pd
import logging
from typing import Optional, Tuple
from pathlib import Path


class DataLoader:
    """
    A class to load and validate sales data from CSV files.
    
    Attributes:
        file_path (Path): Path to the CSV file
        logger (logging.Logger): Logger instance for tracking operations
    """
    
    def __init__(self, file_path: str) -> None:
        """
        Initialize the DataLoader with a file path.
        
        Args:
            file_path: Path to the CSV file containing sales data
        """
        self.file_path = Path(file_path)
        self.logger = logging.getLogger(__name__)
        
    def load_data(self, encoding: Optional[str] = None) -> pd.DataFrame:
        """
        Load data from CSV file with automatic encoding detection.
        
        Args:
            encoding: Optional encoding to use. If None, will try multiple encodings automatically.
        
        Returns:
            DataFrame containing the loaded sales data
            
        Raises:
            FileNotFoundError: If the CSV file does not exist
            pd.errors.EmptyDataError: If the CSV file is empty
            pd.errors.ParserError: If the CSV file cannot be parsed
        """
        try:
            if not self.file_path.exists():
                raise FileNotFoundError(f"File not found: {self.file_path}")
            
            self.logger.info(f"Loading data from {self.file_path}")
            
            # List of encodings to try (most common first)
            encodings_to_try = [encoding] if encoding else ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252', 'utf-16']
            
            last_error = None
            for enc in encodings_to_try:
                try:
                    df = pd.read_csv(self.file_path, encoding=enc)
                    
                    if df.empty:
                        raise pd.errors.EmptyDataError("CSV file is empty")
                    
                    self.logger.info(f"Successfully loaded {len(df)} rows using {enc} encoding")
                    return df
                    
                except UnicodeDecodeError as e:
                    last_error = e
                    self.logger.debug(f"Failed to decode with {enc} encoding, trying next...")
                    continue
                except pd.errors.EmptyDataError as e:
                    self.logger.error(f"Empty data error: {e}")
                    raise
                except pd.errors.ParserError as e:
                    # Parser errors are not encoding-related, so raise immediately
                    self.logger.error(f"Parser error: {e}")
                    raise
            
            # If all encodings failed
            raise UnicodeDecodeError(
                'utf-8',
                b'',
                0,
                1,
                f"Could not decode file with any of the tried encodings: {encodings_to_try}. Last error: {last_error}"
            )
            
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {e}")
            raise
        except UnicodeDecodeError as e:
            self.logger.error(f"Encoding error: {e}")
            raise
        except pd.errors.EmptyDataError as e:
            self.logger.error(f"Empty data error: {e}")
            raise
        except pd.errors.ParserError as e:
            self.logger.error(f"Parser error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error loading data: {e}")
            raise
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, list]:
        """
        Validate the loaded data for required columns and basic data quality.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        required_columns = ['date', 'product', 'region', 'revenue', 'quantity']
        
        self.logger.info("Validating data structure...")
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            issues.append(f"Missing required columns: {missing_columns}")
        
        # Check for empty dataframe
        if df.empty:
            issues.append("DataFrame is empty")
        
        # Check for date column format
        if 'date' in df.columns:
            try:
                pd.to_datetime(df['date'])
            except Exception:
                issues.append("Date column cannot be converted to datetime")
        
        # Check for numeric columns
        numeric_columns = ['revenue', 'quantity']
        for col in numeric_columns:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    issues.append(f"Column '{col}' should be numeric")
        
        is_valid = len(issues) == 0
        
        if is_valid:
            self.logger.info("Data validation passed")
        else:
            self.logger.warning(f"Data validation found {len(issues)} issues")
        
        return is_valid, issues
    
    def get_data_info(self, df: pd.DataFrame) -> dict:
        """
        Get basic information about the loaded dataset.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary containing dataset information
        """
        info = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns': list(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'dtypes': df.dtypes.to_dict()
        }
        
        self.logger.info(f"Dataset info: {info['total_rows']} rows, {info['total_columns']} columns")
        return info

