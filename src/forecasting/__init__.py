"""
Forecasting models for utility price prediction

Production-ready models compatible with Python 3.12+ and 3.13+
Optimized for Streamlit Cloud deployment
"""

# Core models - always available
from src.forecasting.base_forecaster import BaseForecaster
from src.forecasting.simple_ma_model import SimpleMAForecaster
from src.forecasting.xgboost_model import XGBoostForecaster
from src.forecasting.exponential_smoothing_model import ExponentialSmoothingForecaster

__all__ = [
    "BaseForecaster",
    "SimpleMAForecaster",
    "XGBoostForecaster",
    "ExponentialSmoothingForecaster",
]

# Optional advanced models
try:
    from src.forecasting.regression_model import RegressionForecaster
    __all__.append("RegressionForecaster")
except (ImportError, ModuleNotFoundError):
    pass

try:
    from src.forecasting.ensemble_model import EnsembleForecaster
    __all__.append("EnsembleForecaster")
except (ImportError, ModuleNotFoundError):
    pass

try:
    from src.forecasting.model_selector import ModelSelector
    __all__.append("ModelSelector")
except (ImportError, ModuleNotFoundError):
    pass
