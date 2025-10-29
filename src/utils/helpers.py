"""Helper utility functions"""

import os
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union, List


def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't

    Args:
        directory: Directory path

    Returns:
        Path object
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size(file_path: Union[str, Path]) -> float:
    """
    Get file size in MB

    Args:
        file_path: Path to file

    Returns:
        File size in megabytes
    """
    return os.path.getsize(file_path) / (1024 * 1024)


def format_number(number: float, decimals: int = 2, prefix: str = "", suffix: str = "") -> str:
    """
    Format number with prefix/suffix

    Args:
        number: Number to format
        decimals: Number of decimal places
        prefix: Prefix string (e.g., '$')
        suffix: Suffix string (e.g., '%')

    Returns:
        Formatted string
    """
    return f"{prefix}{number:,.{decimals}f}{suffix}"


def calculate_returns(prices: pd.Series, method: str = 'simple') -> pd.Series:
    """
    Calculate returns from price series

    Args:
        prices: Price series
        method: 'simple' or 'log'

    Returns:
        Returns series
    """
    if method == 'simple':
        return prices.pct_change()
    elif method == 'log':
        return np.log(prices / prices.shift(1))
    else:
        raise ValueError(f"Unknown method: {method}")


def detect_frequency(dates: pd.Series) -> str:
    """
    Detect data frequency from dates

    Args:
        dates: Series of dates

    Returns:
        Frequency string ('D' for daily, 'W' for weekly, 'M' for monthly)
    """
    dates = pd.to_datetime(dates)
    diff = dates.diff().mode()[0]

    if diff <= pd.Timedelta(days=1):
        return 'D'
    elif diff <= pd.Timedelta(days=7):
        return 'W'
    elif diff <= pd.Timedelta(days=31):
        return 'M'
    else:
        return 'D'  # Default to daily


def resample_data(df: pd.DataFrame, freq: str = 'D', price_col: str = 'price') -> pd.DataFrame:
    """
    Resample data to specified frequency

    Args:
        df: DataFrame with date index
        freq: Target frequency ('D', 'W', 'M')
        price_col: Name of price column

    Returns:
        Resampled DataFrame
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame must have DatetimeIndex")

    # Resample using mean for prices, sum for volumes
    resampled = df.resample(freq).agg({
        price_col: 'mean',
        **{col: 'sum' for col in df.columns if col != price_col and col in ['volume', 'demand', 'consumption']}
    })

    # Forward fill missing values
    resampled = resampled.fillna(method='ffill')

    return resampled


def remove_outliers(data: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> pd.Series:
    """
    Remove outliers from series

    Args:
        data: Data series
        method: 'iqr' or 'zscore'
        threshold: Threshold for outlier detection

    Returns:
        Series with outliers removed (replaced with NaN)
    """
    if method == 'iqr':
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - threshold * IQR
        upper = Q3 + threshold * IQR
        return data.where((data >= lower) & (data <= upper))

    elif method == 'zscore':
        z_scores = np.abs((data - data.mean()) / data.std())
        return data.where(z_scores < threshold)

    else:
        raise ValueError(f"Unknown method: {method}")


def fill_missing_values(data: pd.Series, method: str = 'interpolate') -> pd.Series:
    """
    Fill missing values

    Args:
        data: Data series
        method: 'interpolate', 'ffill', 'bfill', or 'mean'

    Returns:
        Series with missing values filled
    """
    if method == 'interpolate':
        return data.interpolate(method='linear')
    elif method == 'ffill':
        return data.fillna(method='ffill')
    elif method == 'bfill':
        return data.fillna(method='bfill')
    elif method == 'mean':
        return data.fillna(data.mean())
    else:
        raise ValueError(f"Unknown method: {method}")


def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> tuple:
    """
    Validate DataFrame has required columns

    Args:
        df: DataFrame to validate
        required_columns: List of required column names

    Returns:
        Tuple of (is_valid, error_message)
    """
    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        return False, f"Missing columns: {', '.join(missing_columns)}"

    return True, ""


def calculate_statistics(data: pd.Series) -> dict:
    """
    Calculate descriptive statistics

    Args:
        data: Data series

    Returns:
        Dictionary of statistics
    """
    return {
        'mean': data.mean(),
        'median': data.median(),
        'std': data.std(),
        'min': data.min(),
        'max': data.max(),
        'q25': data.quantile(0.25),
        'q75': data.quantile(0.75),
        'skew': data.skew(),
        'kurtosis': data.kurtosis(),
    }
