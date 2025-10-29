"""Prophet forecasting model"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

from src.forecasting.base_forecaster import BaseForecaster
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProphetForecaster(BaseForecaster):
    """
    Facebook Prophet forecaster
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        if not PROPHET_AVAILABLE:
            raise ImportError("prophet is required for Prophet forecasting")

        # Prophet parameters
        self.changepoint_prior_scale = self.config.get('changepoint_prior_scale', 0.05)
        self.seasonality_prior_scale = self.config.get('seasonality_prior_scale', 10.0)
        self.yearly_seasonality = self.config.get('yearly_seasonality', True)
        self.weekly_seasonality = self.config.get('weekly_seasonality', True)
        self.daily_seasonality = self.config.get('daily_seasonality', False)

    def fit(self, data: pd.Series) -> None:
        """Fit Prophet model"""
        logger.info("Fitting Prophet model...")

        self.train_data = data

        try:
            # Prepare data for Prophet (needs 'ds' and 'y' columns)
            df = pd.DataFrame({
                'ds': data.index,
                'y': data.values
            })

            # Initialize and fit model
            self.model = Prophet(
                changepoint_prior_scale=self.changepoint_prior_scale,
                seasonality_prior_scale=self.seasonality_prior_scale,
                yearly_seasonality=self.yearly_seasonality,
                weekly_seasonality=self.weekly_seasonality,
                daily_seasonality=self.daily_seasonality,
            )

            self.model.fit(df)
            self.fitted = True

            logger.info("Prophet model fitted successfully")

        except Exception as e:
            logger.error(f"Error fitting Prophet: {str(e)}")
            raise

    def predict(self, horizon: int) -> pd.DataFrame:
        """Make Prophet predictions"""
        if not self.fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        logger.info(f"Predicting {horizon} periods...")

        try:
            # Create future dataframe
            last_date = self.train_data.index[-1]
            freq = pd.infer_freq(self.train_data.index) or 'D'
            future_dates = pd.date_range(start=last_date, periods=horizon + 1, freq=freq)[1:]

            future_df = pd.DataFrame({'ds': future_dates})

            # Make forecast
            forecast = self.model.predict(future_df)

            # Create result dataframe
            result = pd.DataFrame({
                'forecast': forecast['yhat'].values,
                'lower_bound': forecast['yhat_lower'].values,
                'upper_bound': forecast['yhat_upper'].values
            }, index=future_dates)

            return result

        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        info = super().get_model_info()
        info['parameters'] = {
            'changepoint_prior_scale': self.changepoint_prior_scale,
            'seasonality_prior_scale': self.seasonality_prior_scale,
            'yearly_seasonality': self.yearly_seasonality,
            'weekly_seasonality': self.weekly_seasonality,
            'daily_seasonality': self.daily_seasonality,
        }

        return info
