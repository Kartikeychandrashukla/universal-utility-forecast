"""
Simple Moving Average Forecasting Model

A basic but effective forecasting model that uses moving averages with trend
components. This model is fully compatible with Python 3.12 and requires no
external forecasting packages (statsmodels, prophet, etc.).

Perfect for:
- Quick baseline forecasts
- Short to medium-term predictions (30-365 days)
- Production environments where minimal dependencies are required
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple
from .base_forecaster import BaseForecaster


class SimpleMAForecaster(BaseForecaster):
    """
    Simple Moving Average forecasting model with trend component.

    This model:
    1. Calculates a moving average of recent prices
    2. Estimates the trend from recent data
    3. Projects forward using MA + trend * time_step
    4. Provides confidence intervals based on historical volatility

    Parameters:
        window_size (int): Number of periods for moving average calculation.
                          If None, uses adaptive window (25% of data length).
        trend_periods (int): Number of periods to calculate trend.
                            If None, uses same as window_size.
        confidence_level (float): Confidence level for prediction intervals (0-1).
        seasonality_periods (Optional[int]): If provided, adds seasonal component.
    """

    def __init__(
        self,
        window_size: Optional[int] = None,
        trend_periods: Optional[int] = None,
        confidence_level: float = 0.95,
        seasonality_periods: Optional[int] = None
    ):
        """Initialize the Simple MA forecaster."""
        super().__init__()
        self.window_size = window_size
        self.trend_periods = trend_periods
        self.confidence_level = confidence_level
        self.seasonality_periods = seasonality_periods

        # Model state (populated during fit)
        self.moving_avg = None
        self.trend = None
        self.std = None
        self.seasonal_component = None
        self.training_data = None

    def fit(self, data: pd.Series) -> None:
        """
        Fit the model to historical data.

        Args:
            data: Historical price series with datetime index
        """
        if len(data) < 10:
            raise ValueError("Need at least 10 data points to fit the model")

        self.training_data = data.copy()

        # Adaptive window size (25% of data, min 7, max 90)
        if self.window_size is None:
            self.window_size = max(7, min(90, len(data) // 4))

        # Trend calculation period
        if self.trend_periods is None:
            self.trend_periods = self.window_size

        # Calculate moving average from recent data
        self.moving_avg = data.rolling(window=self.window_size).mean().iloc[-1]

        # Calculate trend (linear slope over recent periods)
        recent_data = data.iloc[-self.trend_periods:]
        x = np.arange(len(recent_data))
        y = recent_data.values

        # Simple linear regression for trend
        trend_coef = np.polyfit(x, y, 1)
        self.trend = trend_coef[0]  # Slope

        # Calculate standard deviation for confidence intervals
        self.std = data.std()

        # Calculate seasonal component if requested
        if self.seasonality_periods is not None and len(data) >= self.seasonality_periods * 2:
            self._fit_seasonality(data)

        self.is_fitted = True

    def _fit_seasonality(self, data: pd.Series) -> None:
        """
        Extract seasonal component using simple averaging method.

        Args:
            data: Historical price series
        """
        period = self.seasonality_periods
        n_periods = len(data) // period

        if n_periods < 2:
            self.seasonal_component = None
            return

        # Reshape data into periods and calculate average pattern
        seasonal_data = []
        for i in range(period):
            values = data.iloc[i::period].values
            if len(values) > 0:
                seasonal_data.append(np.mean(values))

        if len(seasonal_data) == period:
            # Normalize so seasonal component averages to 0
            seasonal_array = np.array(seasonal_data)
            self.seasonal_component = seasonal_array - np.mean(seasonal_array)
        else:
            self.seasonal_component = None

    def predict(
        self,
        steps: int,
        start_date: Optional[pd.Timestamp] = None
    ) -> pd.DataFrame:
        """
        Generate forecast for specified number of steps.

        Args:
            steps: Number of periods to forecast
            start_date: Starting date for forecast (if None, continues from training data)

        Returns:
            DataFrame with columns: forecast, lower_bound, upper_bound
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")

        # Determine forecast dates
        if start_date is None:
            start_date = self.training_data.index[-1] + pd.Timedelta(days=1)

        # Generate date range based on training data frequency
        if len(self.training_data) > 1:
            freq = pd.infer_freq(self.training_data.index)
            if freq is None:
                freq = 'D'  # Default to daily
        else:
            freq = 'D'

        future_dates = pd.date_range(start=start_date, periods=steps, freq=freq)

        # Generate predictions
        predictions = []
        for i in range(1, steps + 1):
            # Base prediction: MA + trend * time_step
            pred = self.moving_avg + self.trend * i

            # Add seasonal component if available
            if self.seasonal_component is not None:
                season_idx = (len(self.training_data) + i - 1) % len(self.seasonal_component)
                pred += self.seasonal_component[season_idx]

            predictions.append(pred)

        # Calculate confidence intervals
        z_score = self._get_z_score(self.confidence_level)

        # Uncertainty increases with forecast horizon
        uncertainty_multiplier = np.sqrt(np.arange(1, steps + 1))
        lower_bounds = predictions - z_score * self.std * uncertainty_multiplier
        upper_bounds = predictions + z_score * self.std * uncertainty_multiplier

        # Create forecast dataframe
        forecast_df = pd.DataFrame({
            'forecast': predictions,
            'lower_bound': lower_bounds,
            'upper_bound': upper_bounds
        }, index=future_dates)

        return forecast_df

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

    def evaluate(self, test_data: pd.Series) -> Dict[str, float]:
        """
        Evaluate model performance on test data.

        Args:
            test_data: Test data series

        Returns:
            Dictionary of evaluation metrics
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before evaluation")

        # Generate predictions for test period
        forecast_df = self.predict(steps=len(test_data))
        predictions = forecast_df['forecast'].values
        actuals = test_data.values

        # Calculate metrics
        mae = np.mean(np.abs(actuals - predictions))
        mse = np.mean((actuals - predictions) ** 2)
        rmse = np.sqrt(mse)

        # MAPE (handle zero values)
        mape_values = np.abs((actuals - predictions) / np.where(actuals != 0, actuals, 1))
        mape = np.mean(mape_values) * 100

        # R-squared
        ss_res = np.sum((actuals - predictions) ** 2)
        ss_tot = np.sum((actuals - np.mean(actuals)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        return {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'mape': mape,
            'r2': r2
        }

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the fitted model.

        Returns:
            Dictionary with model parameters and statistics
        """
        if not self.is_fitted:
            return {'status': 'not_fitted'}

        return {
            'model_type': 'Simple Moving Average',
            'window_size': self.window_size,
            'trend_periods': self.trend_periods,
            'moving_average': float(self.moving_avg),
            'trend': float(self.trend),
            'std_dev': float(self.std),
            'confidence_level': self.confidence_level,
            'has_seasonality': self.seasonal_component is not None,
            'training_samples': len(self.training_data),
            'is_fitted': True
        }

    def save_state(self) -> Dict[str, Any]:
        """
        Save model state for persistence.

        Returns:
            Dictionary with model state
        """
        return {
            'window_size': self.window_size,
            'trend_periods': self.trend_periods,
            'confidence_level': self.confidence_level,
            'seasonality_periods': self.seasonality_periods,
            'moving_avg': float(self.moving_avg) if self.moving_avg is not None else None,
            'trend': float(self.trend) if self.trend is not None else None,
            'std': float(self.std) if self.std is not None else None,
            'seasonal_component': self.seasonal_component.tolist() if self.seasonal_component is not None else None,
            'training_data': self.training_data.to_dict() if self.training_data is not None else None,
            'is_fitted': self.is_fitted
        }

    def load_state(self, state: Dict[str, Any]) -> None:
        """
        Load model state from saved dictionary.

        Args:
            state: Dictionary with model state
        """
        self.window_size = state['window_size']
        self.trend_periods = state['trend_periods']
        self.confidence_level = state['confidence_level']
        self.seasonality_periods = state['seasonality_periods']
        self.moving_avg = state['moving_avg']
        self.trend = state['trend']
        self.std = state['std']

        if state['seasonal_component'] is not None:
            self.seasonal_component = np.array(state['seasonal_component'])
        else:
            self.seasonal_component = None

        if state['training_data'] is not None:
            self.training_data = pd.Series(state['training_data'])
        else:
            self.training_data = None

        self.is_fitted = state['is_fitted']
