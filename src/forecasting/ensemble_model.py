"""Ensemble forecasting model (placeholder)"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any

from src.forecasting.base_forecaster import BaseForecaster
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EnsembleForecaster(BaseForecaster):
    """
    Ensemble forecaster combining multiple models (placeholder)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        logger.info("EnsembleForecaster initialized (placeholder)")

    def fit(self, data: pd.Series) -> None:
        """Fit ensemble model"""
        logger.info("Fitting Ensemble model...")
        self.train_data = data
        self.fitted = True

    def predict(self, horizon: int) -> pd.DataFrame:
        """Make ensemble predictions"""
        if not self.fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        logger.info(f"Predicting {horizon} periods...")

        # Simple average of last values
        window = min(30, len(self.train_data))
        mean_forecast = self.train_data.tail(window).mean()

        predictions = np.full(horizon, mean_forecast)

        # Generate dates
        last_date = self.train_data.index[-1]
        freq = pd.infer_freq(self.train_data.index) or 'D'
        future_dates = pd.date_range(start=last_date, periods=horizon + 1, freq=freq)[1:]

        std = self.train_data.std()

        result = pd.DataFrame({
            'forecast': predictions,
            'lower_bound': predictions - 1.96 * std,
            'upper_bound': predictions + 1.96 * std
        }, index=future_dates)

        return result
