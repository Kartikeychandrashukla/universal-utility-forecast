"""Base class for all forecasting models"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseForecaster(ABC):
    """
    Abstract base class for forecasting models
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize forecaster

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.model = None
        self.fitted = False
        self.train_data = None
        self.forecast_result = None
        logger.info(f"{self.__class__.__name__} initialized")

    @abstractmethod
    def fit(self, data: pd.Series) -> None:
        """
        Fit the model to training data

        Args:
            data: Time series data
        """
        pass

    @abstractmethod
    def predict(self, horizon: int) -> pd.DataFrame:
        """
        Make predictions

        Args:
            horizon: Number of periods to forecast

        Returns:
            DataFrame with predictions
        """
        pass

    def forecast(self, data: pd.Series, horizon: int) -> pd.DataFrame:
        """
        Fit model and make forecast

        Args:
            data: Time series data
            horizon: Number of periods to forecast

        Returns:
            DataFrame with forecast
        """
        logger.info(f"Forecasting {horizon} periods with {self.__class__.__name__}")

        self.fit(data)
        forecast = self.predict(horizon)

        self.forecast_result = forecast
        return forecast

    def evaluate(self, actual: pd.Series, predicted: pd.Series) -> Dict[str, float]:
        """
        Evaluate forecast accuracy

        Args:
            actual: Actual values
            predicted: Predicted values

        Returns:
            Dictionary of metrics
        """
        # Align series
        common_idx = actual.index.intersection(predicted.index)
        actual_aligned = actual.loc[common_idx]
        predicted_aligned = predicted.loc[common_idx]

        if len(actual_aligned) == 0:
            logger.warning("No overlapping data for evaluation")
            return {}

        # Calculate metrics
        mse = mean_squared_error(actual_aligned, predicted_aligned)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(actual_aligned, predicted_aligned)
        mape = np.mean(np.abs((actual_aligned - predicted_aligned) / actual_aligned)) * 100
        r2 = r2_score(actual_aligned, predicted_aligned)

        metrics = {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'mape': mape,
            'r2': r2,
        }

        logger.info(f"Evaluation metrics: RMSE={rmse:.2f}, MAE={mae:.2f}, MAPE={mape:.2f}%")
        return metrics

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information

        Returns:
            Dictionary with model info
        """
        return {
            'name': self.__class__.__name__,
            'fitted': self.fitted,
            'config': self.config,
        }

    def _create_forecast_dataframe(
        self,
        dates: pd.DatetimeIndex,
        predictions: np.ndarray,
        lower_bound: Optional[np.ndarray] = None,
        upper_bound: Optional[np.ndarray] = None,
    ) -> pd.DataFrame:
        """
        Create forecast DataFrame

        Args:
            dates: Future dates
            predictions: Predicted values
            lower_bound: Lower confidence bound
            upper_bound: Upper confidence bound

        Returns:
            DataFrame with forecast
        """
        df = pd.DataFrame({
            'date': dates,
            'forecast': predictions,
        })

        if lower_bound is not None:
            df['lower_bound'] = lower_bound
        if upper_bound is not None:
            df['upper_bound'] = upper_bound

        df = df.set_index('date')
        return df

    def _generate_future_dates(
        self,
        start_date: pd.Timestamp,
        horizon: int,
        freq: str = 'D'
    ) -> pd.DatetimeIndex:
        """
        Generate future dates

        Args:
            start_date: Starting date
            horizon: Number of periods
            freq: Frequency ('D', 'W', 'M')

        Returns:
            DatetimeIndex
        """
        return pd.date_range(start=start_date, periods=horizon, freq=freq)

    def _calculate_confidence_interval(
        self,
        predictions: np.ndarray,
        std_error: float,
        confidence: float = 0.95
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate confidence intervals

        Args:
            predictions: Point predictions
            std_error: Standard error
            confidence: Confidence level

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        from scipy import stats

        z_score = stats.norm.ppf((1 + confidence) / 2)
        margin = z_score * std_error

        lower_bound = predictions - margin
        upper_bound = predictions + margin

        return lower_bound, upper_bound

    def _get_z_score(self, confidence_level: float) -> float:
        """
        Get z-score for given confidence level.

        Args:
            confidence_level: Confidence level (0-1)

        Returns:
            Z-score value
        """
        # Common z-scores for confidence intervals
        z_scores = {
            0.90: 1.645,
            0.95: 1.960,
            0.99: 2.576
        }

        return z_scores.get(confidence_level, 1.960)
