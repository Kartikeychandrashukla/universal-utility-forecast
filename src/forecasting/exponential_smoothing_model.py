"""Exponential Smoothing forecasting model"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from src.forecasting.base_forecaster import BaseForecaster
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ExponentialSmoothingForecaster(BaseForecaster):
    """
    Exponential Smoothing (Holt-Winters) forecasting model.
    Handles trend and seasonality automatically.
    """

    def __init__(
        self,
        seasonal_periods: Optional[int] = None,
        trend: str = 'add',
        seasonal: Optional[str] = None,
        confidence_level: float = 0.95
    ):
        super().__init__()
        self.seasonal_periods = seasonal_periods
        self.trend = trend
        self.seasonal = seasonal
        self.confidence_level = confidence_level
        self.model = None
        self.fitted_model = None
        logger.info(f"ExponentialSmoothingForecaster initialized")

    def fit(self, data: pd.Series) -> None:
        """Fit the Exponential Smoothing model to historical data"""
        logger.info("Fitting Exponential Smoothing model...")

        self.training_data = data

        # Auto-detect seasonality if not specified
        if self.seasonal_periods is None:
            # Try to detect weekly seasonality (7 days)
            if len(data) >= 14:
                self.seasonal_periods = 7
            else:
                self.seasonal_periods = None

        # Determine if we should use seasonal component
        if self.seasonal is None:
            if self.seasonal_periods and len(data) >= 2 * self.seasonal_periods:
                self.seasonal = 'add'
            else:
                self.seasonal = None

        try:
            # Fit the model
            self.model = ExponentialSmoothing(
                data,
                trend=self.trend,
                seasonal=self.seasonal,
                seasonal_periods=self.seasonal_periods if self.seasonal else None
            )

            self.fitted_model = self.model.fit(optimized=True)

            # Calculate residuals for confidence intervals
            fitted_values = self.fitted_model.fittedvalues
            residuals = data - fitted_values
            self.residual_std = np.std(residuals)

            self.fitted = True
            logger.info(
                f"Exponential Smoothing model fitted successfully "
                f"(trend={self.trend}, seasonal={self.seasonal}, "
                f"periods={self.seasonal_periods})"
            )

        except Exception as e:
            logger.warning(f"Failed to fit with seasonal component: {e}")
            logger.info("Retrying without seasonality...")

            # Retry without seasonality
            self.seasonal = None
            self.model = ExponentialSmoothing(
                data,
                trend=self.trend,
                seasonal=None
            )

            self.fitted_model = self.model.fit(optimized=True)

            fitted_values = self.fitted_model.fittedvalues
            residuals = data - fitted_values
            self.residual_std = np.std(residuals)

            self.fitted = True
            logger.info(f"Exponential Smoothing model fitted successfully (trend only)")

    def predict(self, steps: int, start_date: Optional[pd.Timestamp] = None) -> pd.DataFrame:
        """Generate forecast with confidence intervals"""
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")

        logger.info(f"Predicting {steps} periods...")

        # Generate forecast
        forecast_result = self.fitted_model.forecast(steps=steps)

        if isinstance(forecast_result, pd.Series):
            predictions = forecast_result.values
        else:
            predictions = forecast_result

        # Calculate confidence intervals
        z_score = self._get_z_score(self.confidence_level)
        uncertainty_multiplier = np.sqrt(np.arange(1, steps + 1))
        lower_bounds = predictions - z_score * self.residual_std * uncertainty_multiplier
        upper_bounds = predictions + z_score * self.residual_std * uncertainty_multiplier

        # Create date index
        if start_date is None:
            start_date = self.training_data.index[-1] + pd.Timedelta(days=1)

        future_dates = pd.date_range(start=start_date, periods=steps, freq='D')

        return pd.DataFrame({
            'forecast': predictions,
            'lower_bound': lower_bounds,
            'upper_bound': upper_bounds
        }, index=future_dates)

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        if not self.fitted:
            return {"status": "not_fitted"}

        return {
            "model_type": "Exponential Smoothing (Holt-Winters)",
            "trend": self.trend,
            "seasonal": self.seasonal if self.seasonal else "None",
            "seasonal_periods": self.seasonal_periods if self.seasonal_periods else "None",
            "residual_std": float(self.residual_std),
            "training_samples": len(self.training_data)
        }
