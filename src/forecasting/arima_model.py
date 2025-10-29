"""ARIMA forecasting model"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')

try:
    from statsmodels.tsa.arima.model import ARIMA
    from pmdarima import auto_arima
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False

from src.forecasting.base_forecaster import BaseForecaster
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ARIMAForecaster(BaseForecaster):
    """
    ARIMA (AutoRegressive Integrated Moving Average) forecaster
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        if not ARIMA_AVAILABLE:
            raise ImportError("statsmodels and pmdarima are required for ARIMA forecasting")

        self.order = self.config.get('order', None)
        self.auto_select = self.config.get('auto_select_order', True)

    def fit(self, data: pd.Series) -> None:
        """Fit ARIMA model"""
        logger.info("Fitting ARIMA model...")

        self.train_data = data

        try:
            if self.auto_select:
                # Use auto_arima to find best parameters
                logger.info("Auto-selecting ARIMA order...")
                auto_model = auto_arima(
                    data,
                    seasonal=False,
                    stepwise=True,
                    suppress_warnings=True,
                    error_action='ignore',
                    max_p=5,
                    max_q=5,
                    max_d=2,
                    trace=False
                )
                self.order = auto_model.order
                logger.info(f"Selected ARIMA order: {self.order}")

            # Fit ARIMA model
            self.model = ARIMA(data, order=self.order)
            self.model = self.model.fit()
            self.fitted = True

            logger.info(f"ARIMA model fitted successfully with order {self.order}")

        except Exception as e:
            logger.error(f"Error fitting ARIMA: {str(e)}")
            raise

    def predict(self, horizon: int) -> pd.DataFrame:
        """Make ARIMA predictions"""
        if not self.fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        logger.info(f"Predicting {horizon} periods...")

        try:
            # Get forecast
            forecast_result = self.model.forecast(steps=horizon)

            # Get confidence intervals
            forecast_df = self.model.get_forecast(steps=horizon)
            conf_int = forecast_df.conf_int()

            # Create future dates
            last_date = self.train_data.index[-1]
            freq = pd.infer_freq(self.train_data.index) or 'D'
            future_dates = pd.date_range(start=last_date, periods=horizon + 1, freq=freq)[1:]

            # Create result dataframe
            result = pd.DataFrame({
                'forecast': forecast_result,
                'lower_bound': conf_int.iloc[:, 0],
                'upper_bound': conf_int.iloc[:, 1]
            }, index=future_dates)

            return result

        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        info = super().get_model_info()
        info['order'] = self.order

        if self.fitted and self.model is not None:
            info['aic'] = self.model.aic
            info['bic'] = self.model.bic

        return info
