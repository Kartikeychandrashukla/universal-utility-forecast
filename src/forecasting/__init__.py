"""Forecasting models for utility price prediction"""

# Always available
from src.forecasting.base_forecaster import BaseForecaster
from src.forecasting.simple_ma_model import SimpleMAForecaster

# Optional models - gracefully handle missing dependencies
__all__ = ["BaseForecaster", "SimpleMAForecaster"]

try:
    from src.forecasting.arima_model import ARIMAForecaster
    __all__.append("ARIMAForecaster")
except (ImportError, ModuleNotFoundError):
    pass

try:
    from src.forecasting.prophet_model import ProphetForecaster
    __all__.append("ProphetForecaster")
except (ImportError, ModuleNotFoundError):
    pass

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
