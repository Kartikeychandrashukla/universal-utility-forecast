"""Auto-detect utility type from data patterns"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from scipy import stats

from src.utils.logger import get_logger

logger = get_logger(__name__)


class UtilityDetector:
    """
    Automatically detect utility type based on data characteristics
    """

    # Price ranges for different utilities (indicative)
    PRICE_RANGES = {
        'natural_gas': (1.5, 15.0),  # $/MMBtu
        'electricity': (20.0, 200.0),  # $/MWh
        'crude_oil': (30.0, 150.0),  # $/barrel
        'water': (0.5, 5.0),  # $/1000 gallons
        'coal': (30.0, 200.0),  # $/ton
        'propane': (0.5, 3.0),  # $/gallon
    }

    # Keywords for detection
    KEYWORDS = {
        'natural_gas': ['gas', 'natural_gas', 'naturalgas', 'ng', 'henry hub', 'mmbtu', 'henry'],
        'electricity': ['electricity', 'electric', 'power', 'mwh', 'kwh', 'energy', 'elec'],
        'crude_oil': ['oil', 'crude', 'crude_oil', 'crudeoil', 'wti', 'brent', 'petroleum', 'barrel'],
        'water': ['water', 'h2o', 'aqua'],
        'coal': ['coal'],
        'propane': ['propane', 'lpg'],
    }

    # Seasonality patterns
    SEASONALITY_PATTERNS = {
        'winter_peak': 'natural_gas',
        'summer_peak': 'electricity',
        'low': 'crude_oil',
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize UtilityDetector

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        logger.info("UtilityDetector initialized")

    def detect(
        self,
        data: pd.DataFrame,
        filename: Optional[str] = None,
        columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Detect utility type from data

        Args:
            data: DataFrame with price data
            filename: Original filename (for keyword detection)
            columns: Column names (for keyword detection)

        Returns:
            Dictionary with detection results
        """
        logger.info("Detecting utility type...")

        # Initialize scores
        scores = {utility: 0.0 for utility in self.PRICE_RANGES.keys()}

        # Method 1: Check filename and columns for keywords
        if filename or columns:
            keyword_scores = self._detect_from_keywords(filename, columns)
            for utility, score in keyword_scores.items():
                scores[utility] += score * 5.0  # Very high weight for keywords (filename is most reliable)

        # Method 2: Check price range
        price_scores = self._detect_from_price_range(data)
        for utility, score in price_scores.items():
            scores[utility] += score * 1.0

        # Method 3: Check seasonality pattern
        seasonality_scores = self._detect_from_seasonality(data)
        for utility, score in seasonality_scores.items():
            scores[utility] += score * 1.5

        # Method 4: Check volatility
        volatility_scores = self._detect_from_volatility(data)
        for utility, score in volatility_scores.items():
            scores[utility] += score * 0.5

        # Normalize scores
        total_score = sum(scores.values())
        if total_score > 0:
            scores = {k: v/total_score for k, v in scores.items()}

        # Get best match
        detected_utility = max(scores, key=scores.get)
        confidence = scores[detected_utility]

        result = {
            'utility_type': detected_utility,
            'confidence': confidence,
            'scores': scores,
            'characteristics': self._get_characteristics(data, detected_utility),
        }

        logger.info(f"Detected utility: {detected_utility} (confidence: {confidence:.2%})")
        return result

    def _detect_from_keywords(
        self,
        filename: Optional[str],
        columns: Optional[List[str]]
    ) -> Dict[str, float]:
        """Detect utility from keywords in filename and columns"""
        scores = {utility: 0.0 for utility in self.KEYWORDS.keys()}

        text = ""
        if filename:
            text += filename.lower() + " "
        if columns:
            text += " ".join(columns).lower()

        if not text:
            return scores

        for utility, keywords in self.KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[utility] += 1.0

        return scores

    def _detect_from_price_range(self, data: pd.DataFrame) -> Dict[str, float]:
        """Detect utility from price range"""
        scores = {utility: 0.0 for utility in self.PRICE_RANGES.keys()}

        mean_price = data['price'].mean()
        median_price = data['price'].median()

        for utility, (low, high) in self.PRICE_RANGES.items():
            # Check if mean and median are within range
            if low <= mean_price <= high:
                scores[utility] += 0.5
            if low <= median_price <= high:
                scores[utility] += 0.5

            # Check overlap percentage
            in_range = ((data['price'] >= low) & (data['price'] <= high)).sum()
            overlap_pct = in_range / len(data)
            scores[utility] += overlap_pct

        return scores

    def _detect_from_seasonality(self, data: pd.DataFrame) -> Dict[str, float]:
        """Detect utility from seasonality pattern"""
        scores = {utility: 0.0 for utility in self.PRICE_RANGES.keys()}

        if len(data) < 365:  # Need at least 1 year
            return scores

        try:
            # Extract month from index
            data_copy = data.copy()
            data_copy['month'] = data_copy.index.month

            # Calculate average price by month
            monthly_avg = data_copy.groupby('month')['price'].mean()

            # Identify peak months
            top_months = monthly_avg.nlargest(3).index.tolist()

            # Winter peak (Dec, Jan, Feb)
            if any(m in [12, 1, 2] for m in top_months):
                scores['natural_gas'] += 1.0

            # Summer peak (Jun, Jul, Aug)
            if any(m in [6, 7, 8] for m in top_months):
                scores['electricity'] += 1.0
                scores['water'] += 0.5

            # Calculate seasonality strength
            seasonality_strength = (monthly_avg.max() - monthly_avg.min()) / monthly_avg.mean()

            if seasonality_strength < 0.1:  # Low seasonality
                scores['crude_oil'] += 1.0
            elif seasonality_strength > 0.3:  # High seasonality
                scores['natural_gas'] += 0.5
                scores['electricity'] += 0.5

        except Exception as e:
            logger.warning(f"Error detecting seasonality: {str(e)}")

        return scores

    def _detect_from_volatility(self, data: pd.DataFrame) -> Dict[str, float]:
        """Detect utility from price volatility"""
        scores = {utility: 0.0 for utility in self.PRICE_RANGES.keys()}

        # Calculate returns and volatility
        returns = data['price'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # Annualized

        # Different utilities have different typical volatilities
        if volatility < 0.15:  # Low volatility
            scores['water'] += 1.0
            scores['coal'] += 0.5
        elif 0.15 <= volatility < 0.30:  # Medium volatility
            scores['crude_oil'] += 1.0
        elif volatility >= 0.30:  # High volatility
            scores['natural_gas'] += 1.0
            scores['electricity'] += 1.0

        return scores

    def _get_characteristics(self, data: pd.DataFrame, utility_type: str) -> Dict[str, Any]:
        """Get characteristics of the detected utility"""
        characteristics = {
            'mean_price': float(data['price'].mean()),
            'median_price': float(data['price'].median()),
            'std_price': float(data['price'].std()),
            'min_price': float(data['price'].min()),
            'max_price': float(data['price'].max()),
            'volatility': float(data['price'].pct_change().std() * np.sqrt(252)),
        }

        # Add seasonality info
        if len(data) >= 365:
            try:
                data_copy = data.copy()
                data_copy['month'] = data_copy.index.month
                monthly_avg = data_copy.groupby('month')['price'].mean()
                characteristics['peak_month'] = int(monthly_avg.idxmax())
                characteristics['lowest_month'] = int(monthly_avg.idxmin())
                characteristics['seasonality_strength'] = float(
                    (monthly_avg.max() - monthly_avg.min()) / monthly_avg.mean()
                )
            except:
                pass

        # Add utility-specific info
        characteristics['typical_unit'] = self._get_typical_unit(utility_type)
        characteristics['market_name'] = self._get_market_name(utility_type)

        return characteristics

    def _get_typical_unit(self, utility_type: str) -> str:
        """Get typical unit for utility type"""
        units = {
            'natural_gas': 'MMBtu',
            'electricity': 'MWh',
            'crude_oil': 'barrel',
            'water': '1000 gallons',
            'coal': 'ton',
            'propane': 'gallon',
        }
        return units.get(utility_type, 'unit')

    def _get_market_name(self, utility_type: str) -> str:
        """Get typical market name for utility type"""
        markets = {
            'natural_gas': 'Henry Hub',
            'electricity': 'Power Market',
            'crude_oil': 'WTI/Brent',
            'water': 'Water Utility',
            'coal': 'Coal Market',
            'propane': 'Propane Market',
        }
        return markets.get(utility_type, 'Market')
