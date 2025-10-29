"""Data validation utilities"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataValidator:
    """
    Validate data quality and completeness
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize DataValidator

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.min_history_days = self.config.get('forecasting', {}).get('min_history_days', 365)
        self.max_missing_pct = 0.05  # 5% max missing values
        logger.info("DataValidator initialized")

    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive data validation

        Args:
            data: DataFrame to validate

        Returns:
            Dictionary with validation results
        """
        logger.info("Performing data validation...")

        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'checks': {},
        }

        # Run all validation checks
        checks = [
            self._check_required_columns,
            self._check_data_types,
            self._check_missing_values,
            self._check_date_range,
            self._check_date_gaps,
            self._check_duplicates,
            self._check_outliers,
            self._check_negative_values,
            self._check_data_sufficiency,
        ]

        for check in checks:
            check_name = check.__name__.replace('_check_', '')
            try:
                passed, message = check(data)
                results['checks'][check_name] = {
                    'passed': passed,
                    'message': message,
                }

                if not passed:
                    if 'error' in message.lower() or check_name in ['required_columns', 'data_types']:
                        results['errors'].append(message)
                        results['is_valid'] = False
                    else:
                        results['warnings'].append(message)

            except Exception as e:
                logger.error(f"Error in check {check_name}: {str(e)}")
                results['errors'].append(f"Validation check failed: {check_name}")
                results['is_valid'] = False

        logger.info(f"Validation complete: {'PASSED' if results['is_valid'] else 'FAILED'}")
        return results

    def _check_required_columns(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Check if required columns are present"""
        required = ['price']  # date is expected to be index

        if not isinstance(data.index, pd.DatetimeIndex):
            return False, "Date must be set as index with datetime type"

        missing = set(required) - set(data.columns)
        if missing:
            return False, f"Missing required columns: {', '.join(missing)}"

        return True, "All required columns present"

    def _check_data_types(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Check data types are correct"""
        if not pd.api.types.is_numeric_dtype(data['price']):
            return False, "Price column must be numeric"

        return True, "Data types are correct"

    def _check_missing_values(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Check for missing values"""
        missing = data.isnull().sum()
        total = len(data)

        missing_pct = (missing / total * 100).to_dict()

        # Check price column specifically
        if missing['price'] > 0:
            pct = missing_pct['price']
            if pct > self.max_missing_pct * 100:
                return False, f"Price column has {pct:.1f}% missing values (max {self.max_missing_pct*100}%)"
            else:
                return True, f"Warning: Price column has {pct:.1f}% missing values"

        # Check other columns
        high_missing = {col: pct for col, pct in missing_pct.items() if pct > 10}
        if high_missing:
            cols_str = ', '.join([f"{col} ({pct:.1f}%)" for col, pct in high_missing.items()])
            return True, f"Warning: High missing values in: {cols_str}"

        return True, "No significant missing values"

    def _check_date_range(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Check date range"""
        date_range = (data.index.max() - data.index.min()).days

        if date_range < self.min_history_days:
            return False, f"Insufficient history: {date_range} days (minimum {self.min_history_days} days required)"

        return True, f"Date range: {date_range} days ({data.index.min().date()} to {data.index.max().date()})"

    def _check_date_gaps(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Check for large gaps in dates"""
        date_diffs = data.index.to_series().diff()
        median_diff = date_diffs.median()

        # Find gaps larger than 3x median
        large_gaps = date_diffs[date_diffs > median_diff * 3]

        if len(large_gaps) > 0:
            max_gap = large_gaps.max()
            return True, f"Warning: Found {len(large_gaps)} date gaps, largest: {max_gap.days} days"

        return True, "No significant date gaps"

    def _check_duplicates(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Check for duplicate dates"""
        duplicates = data.index.duplicated().sum()

        if duplicates > 0:
            return False, f"Found {duplicates} duplicate dates"

        return True, "No duplicate dates"

    def _check_outliers(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Check for outliers in price"""
        Q1 = data['price'].quantile(0.25)
        Q3 = data['price'].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR

        outliers = ((data['price'] < lower_bound) | (data['price'] > upper_bound)).sum()
        outlier_pct = outliers / len(data) * 100

        if outlier_pct > 5:
            return True, f"Warning: Found {outliers} potential outliers ({outlier_pct:.1f}%)"

        return True, f"Found {outliers} potential outliers ({outlier_pct:.1f}%)"

    def _check_negative_values(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Check for negative prices"""
        negative = (data['price'] < 0).sum()

        if negative > 0:
            return True, f"Warning: Found {negative} negative prices"

        return True, "No negative prices"

    def _check_data_sufficiency(self, data: pd.DataFrame) -> Tuple[bool, str]:
        """Check if data is sufficient for analysis"""
        n_records = len(data)
        n_unique = data['price'].nunique()

        if n_records < 100:
            return False, f"Insufficient data: only {n_records} records (minimum 100 required)"

        if n_unique < n_records * 0.5:
            return True, f"Warning: Low price variability ({n_unique} unique values in {n_records} records)"

        return True, f"Sufficient data: {n_records} records with {n_unique} unique prices"

    def get_data_quality_score(self, validation_results: Dict[str, Any]) -> float:
        """
        Calculate overall data quality score (0-100)

        Args:
            validation_results: Results from validate()

        Returns:
            Quality score between 0 and 100
        """
        if not validation_results['is_valid']:
            return 0.0

        total_checks = len(validation_results['checks'])
        passed_checks = sum(1 for check in validation_results['checks'].values() if check['passed'])

        base_score = (passed_checks / total_checks) * 100

        # Reduce score for warnings
        n_warnings = len(validation_results['warnings'])
        warning_penalty = min(n_warnings * 5, 20)  # Max 20 point penalty

        final_score = max(base_score - warning_penalty, 0)

        return round(final_score, 1)
