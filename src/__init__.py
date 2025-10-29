"""
Universal Utility Risk Analytics Platform
Main package initialization
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from src.utils.config_loader import load_config
from src.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)
logger.info(f"UURAP v{__version__} initialized")
