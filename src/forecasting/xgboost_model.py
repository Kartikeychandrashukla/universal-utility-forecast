"""XGBoost-based forecasting model"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import xgboost as xgb
from sklearn.preprocessing import StandardScaler

from src.forecasting.base_forecaster import BaseForecaster
from src.utils.logger import get_logger

logger = get_logger(__name__)


class XGBoostForecaster(BaseForecaster):
    """
    XGBoost-based time series forecasting model.
    Uses gradient boosting with lag features for predictions.
    """

    def __init__(
        self,
        n_lags: int = 7,
        n_estimators: int = 100,
        learning_rate: float = 0.1,
        max_depth: int = 5,
        confidence_level: float = 0.95
    ):
        super().__init__()
        self.n_lags = n_lags
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.confidence_level = confidence_level
        self.model = None
        self.scaler = StandardScaler()
        logger.info(f"XGBoostForecaster initialized with {n_lags} lags")

    def _create_lag_features(self, data: pd.Series, n_lags: int) -> pd.DataFrame:
        """Create lagged features for time series"""
        df = pd.DataFrame({'value': data.values})

        # Create lag features
        for i in range(1, n_lags + 1):
            df[f'lag_{i}'] = df['value'].shift(i)

        # Add rolling statistics
        df['rolling_mean_3'] = df['value'].shift(1).rolling(window=3).mean()
        df['rolling_std_3'] = df['value'].shift(1).rolling(window=3).std()
        df['rolling_mean_7'] = df['value'].shift(1).rolling(window=7).mean()

        # Drop rows with NaN values
        df = df.dropna()

        return df

    def fit(self, data: pd.Series) -> None:
        """Fit the XGBoost model to historical data"""
        logger.info("Fitting XGBoost model...")

        self.training_data = data

        # Create lag features
        df = self._create_lag_features(data, self.n_lags)

        # Prepare X and y
        X = df.drop('value', axis=1)
        y = df['value']

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train XGBoost model
        self.model = xgb.XGBRegressor(
            n_estimators=self.n_estimators,
            learning_rate=self.learning_rate,
            max_depth=self.max_depth,
            random_state=42,
            objective='reg:squarederror'
        )

        self.model.fit(X_scaled, y)

        # Calculate residuals for confidence intervals
        predictions = self.model.predict(X_scaled)
        self.residual_std = np.std(y - predictions)

        self.fitted = True
        logger.info(f"XGBoost model fitted successfully (RMSE: {self.residual_std:.2f})")

    def predict(self, steps: int, start_date: Optional[pd.Timestamp] = None) -> pd.DataFrame:
        """Generate forecast with confidence intervals"""
        if not self.fitted:
            raise ValueError("Model must be fitted before prediction")

        logger.info(f"Predicting {steps} periods...")

        # Use the last n_lags values for prediction
        last_values = self.training_data.values[-self.n_lags:].tolist()
        predictions = []

        for i in range(steps):
            # Create features from last values
            features = []

            # Lag features
            for j in range(1, self.n_lags + 1):
                if len(last_values) >= j:
                    features.append(last_values[-j])
                else:
                    features.append(last_values[0])

            # Rolling statistics
            if len(last_values) >= 3:
                features.append(np.mean(last_values[-3:]))
                features.append(np.std(last_values[-3:]))
            else:
                features.append(np.mean(last_values))
                features.append(0)

            if len(last_values) >= 7:
                features.append(np.mean(last_values[-7:]))
            else:
                features.append(np.mean(last_values))

            # Scale and predict
            features_scaled = self.scaler.transform([features])
            pred = self.model.predict(features_scaled)[0]

            predictions.append(pred)
            last_values.append(pred)

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
            "model_type": "XGBoost",
            "n_lags": self.n_lags,
            "n_estimators": self.n_estimators,
            "learning_rate": self.learning_rate,
            "max_depth": self.max_depth,
            "residual_std": float(self.residual_std),
            "training_samples": len(self.training_data)
        }
