"""Model selection utilities (placeholder)"""

from typing import Dict, Any, Optional
import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ModelSelector:
    """
    Automatically select best forecasting model (placeholder)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        logger.info("ModelSelector initialized (placeholder)")

    def select_best_model(self, data: pd.Series) -> str:
        """Select best model for given data"""
        logger.info("Selecting best model...")

        # Simple heuristic: use Simple MA by default
        if len(data) < 100:
            return "Simple Moving Average"
        elif len(data) < 365:
            return "Regression"
        else:
            return "ARIMA"

    def evaluate_models(self, data: pd.Series) -> Dict[str, float]:
        """Evaluate all available models"""
        logger.info("Evaluating models...")

        # Placeholder scores
        return {
            "Simple Moving Average": 0.85,
            "Regression": 0.80,
            "ARIMA": 0.90,
            "Prophet": 0.88,
        }
