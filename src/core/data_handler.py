"""Universal data handler for any utility type"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union, Dict, Any, Optional, List
from datetime import datetime

from src.utils.logger import get_logger
from src.utils.helpers import (
    ensure_directory_exists,
    detect_frequency,
    fill_missing_values,
    remove_outliers,
)

logger = get_logger(__name__)


class DataHandler:
    """
    Universal data handler that works with any utility commodity CSV
    """

    REQUIRED_COLUMNS = ['date', 'price']
    OPTIONAL_COLUMNS = ['volume', 'demand', 'supply', 'temperature', 'storage_level', 'consumption']
    DATE_FORMATS = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%Y%m%d',
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize DataHandler

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.data: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}
        logger.info("DataHandler initialized")

    def load_csv(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Load data from CSV file

        Args:
            file_path: Path to CSV file

        Returns:
            Loaded DataFrame

        Raises:
            ValueError: If file cannot be loaded or validated
        """
        logger.info(f"Loading CSV file: {file_path}")

        try:
            # Try reading with different encodings
            for encoding in ['utf-8', 'latin1', 'iso-8859-1']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Could not read file with any supported encoding")

            # Normalize column names (lowercase, strip whitespace)
            df.columns = df.columns.str.lower().str.strip()

            # Validate required columns
            self._validate_columns(df)

            # Parse dates
            df = self._parse_dates(df)

            # Sort by date
            df = df.sort_values('date')

            # Set date as index
            df = df.set_index('date')

            # Store data
            self.data = df

            # Extract metadata
            self._extract_metadata()

            logger.info(f"Successfully loaded {len(df)} records")
            return df

        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            raise ValueError(f"Failed to load CSV: {str(e)}")

    def load_excel(self, file_path: Union[str, Path], sheet_name: Union[str, int] = 0) -> pd.DataFrame:
        """
        Load data from Excel file

        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name or index

        Returns:
            Loaded DataFrame
        """
        logger.info(f"Loading Excel file: {file_path}")

        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            df.columns = df.columns.str.lower().str.strip()

            self._validate_columns(df)
            df = self._parse_dates(df)
            df = df.sort_values('date')
            df = df.set_index('date')

            self.data = df
            self._extract_metadata()

            logger.info(f"Successfully loaded {len(df)} records from Excel")
            return df

        except Exception as e:
            logger.error(f"Error loading Excel: {str(e)}")
            raise ValueError(f"Failed to load Excel: {str(e)}")

    def _validate_columns(self, df: pd.DataFrame) -> None:
        """
        Validate DataFrame has required columns

        Args:
            df: DataFrame to validate

        Raises:
            ValueError: If required columns are missing
        """
        missing_columns = set(self.REQUIRED_COLUMNS) - set(df.columns)

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_columns)}. "
                f"Required columns are: {', '.join(self.REQUIRED_COLUMNS)}"
            )

    def _parse_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Parse date column

        Args:
            df: DataFrame with date column

        Returns:
            DataFrame with parsed dates

        Raises:
            ValueError: If dates cannot be parsed
        """
        if 'date' not in df.columns:
            raise ValueError("Date column not found")

        # Try parsing with different formats
        for date_format in self.DATE_FORMATS:
            try:
                df['date'] = pd.to_datetime(df['date'], format=date_format)
                logger.info(f"Successfully parsed dates with format: {date_format}")
                return df
            except (ValueError, TypeError):
                continue

        # If no format works, try pandas auto-detection
        try:
            df['date'] = pd.to_datetime(df['date'])
            logger.info("Successfully parsed dates with auto-detection")
            return df
        except Exception as e:
            raise ValueError(f"Could not parse dates: {str(e)}")

    def _extract_metadata(self) -> None:
        """Extract metadata from loaded data"""
        if self.data is None:
            return

        self.metadata = {
            'num_records': len(self.data),
            'start_date': self.data.index.min(),
            'end_date': self.data.index.max(),
            'date_range_days': (self.data.index.max() - self.data.index.min()).days,
            'frequency': detect_frequency(pd.Series(self.data.index)),
            'columns': list(self.data.columns),
            'price_stats': {
                'mean': self.data['price'].mean(),
                'std': self.data['price'].std(),
                'min': self.data['price'].min(),
                'max': self.data['price'].max(),
            },
            'missing_values': self.data.isnull().sum().to_dict(),
        }

        logger.info(f"Extracted metadata: {self.metadata['num_records']} records, "
                   f"{self.metadata['date_range_days']} days")

    def clean_data(
        self,
        remove_outliers_flag: bool = True,
        fill_missing: bool = True,
        outlier_method: str = 'iqr',
        fill_method: str = 'interpolate',
    ) -> pd.DataFrame:
        """
        Clean data by removing outliers and filling missing values

        Args:
            remove_outliers_flag: Whether to remove outliers
            fill_missing: Whether to fill missing values
            outlier_method: Method for outlier detection ('iqr' or 'zscore')
            fill_method: Method for filling missing values

        Returns:
            Cleaned DataFrame
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_csv() first.")

        logger.info("Cleaning data...")
        df = self.data.copy()

        # Remove outliers from price
        if remove_outliers_flag:
            original_count = len(df)
            df['price'] = remove_outliers(df['price'], method=outlier_method)
            outliers_removed = df['price'].isna().sum()
            logger.info(f"Removed {outliers_removed} outliers from price")

        # Fill missing values
        if fill_missing:
            for col in df.columns:
                if df[col].isna().any():
                    df[col] = fill_missing_values(df[col], method=fill_method)
                    logger.info(f"Filled missing values in {col}")

        self.data = df
        return df

    def get_summary(self) -> Dict[str, Any]:
        """
        Get data summary

        Returns:
            Dictionary containing data summary
        """
        if self.data is None:
            raise ValueError("No data loaded")

        summary = {
            'metadata': self.metadata,
            'statistics': {},
        }

        # Calculate statistics for numeric columns
        for col in self.data.select_dtypes(include=[np.number]).columns:
            summary['statistics'][col] = {
                'mean': float(self.data[col].mean()),
                'median': float(self.data[col].median()),
                'std': float(self.data[col].std()),
                'min': float(self.data[col].min()),
                'max': float(self.data[col].max()),
                'q25': float(self.data[col].quantile(0.25)),
                'q75': float(self.data[col].quantile(0.75)),
            }

        return summary

    def export_to_csv(self, output_path: Union[str, Path]) -> None:
        """
        Export data to CSV

        Args:
            output_path: Output file path
        """
        if self.data is None:
            raise ValueError("No data to export")

        ensure_directory_exists(Path(output_path).parent)
        self.data.to_csv(output_path)
        logger.info(f"Exported data to {output_path}")

    def get_data(self) -> pd.DataFrame:
        """
        Get loaded data

        Returns:
            DataFrame
        """
        if self.data is None:
            raise ValueError("No data loaded")
        return self.data.copy()

    def get_price_series(self) -> pd.Series:
        """
        Get price series

        Returns:
            Price series
        """
        if self.data is None:
            raise ValueError("No data loaded")
        return self.data['price'].copy()

    def split_train_test(
        self,
        test_size: float = 0.2
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data into train and test sets

        Args:
            test_size: Proportion of data for test set

        Returns:
            Tuple of (train_df, test_df)
        """
        if self.data is None:
            raise ValueError("No data loaded")

        split_idx = int(len(self.data) * (1 - test_size))
        train = self.data.iloc[:split_idx]
        test = self.data.iloc[split_idx:]

        logger.info(f"Split data: {len(train)} train, {len(test)} test")
        return train, test
