"""Configuration loader utility"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file and environment variables

    Args:
        config_path: Path to config.yaml file. If None, looks in project root.

    Returns:
        Dictionary containing configuration
    """
    # Load environment variables
    load_dotenv()

    # Determine config file path
    if config_path is None:
        # Look for config.yaml in project root
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent
        config_path = project_root / "config.yaml"
    else:
        config_path = Path(config_path)

    # Load YAML config
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    else:
        # Return default config if file doesn't exist
        config = get_default_config()

    # Override with environment variables
    config = override_with_env(config)

    return config


def get_default_config() -> Dict[str, Any]:
    """Get default configuration"""
    return {
        'app': {
            'name': 'Universal Utility Risk Analytics Platform',
            'version': '1.0.0',
            'debug': True,
            'log_level': 'INFO',
        },
        'data': {
            'upload_dir': 'data/uploads',
            'output_dir': 'data/outputs',
            'max_file_size_mb': 100,
        },
        'forecasting': {
            'default_horizon': 90,
            'min_history_days': 365,
        },
        'api': {
            'host': '0.0.0.0',
            'port': 8000,
        },
        'dashboard': {
            'port': 8501,
        }
    }


def override_with_env(config: Dict[str, Any]) -> Dict[str, Any]:
    """Override config values with environment variables"""

    # App settings
    if os.getenv('DEBUG'):
        config['app']['debug'] = os.getenv('DEBUG').lower() == 'true'
    if os.getenv('LOG_LEVEL'):
        config['app']['log_level'] = os.getenv('LOG_LEVEL')

    # API settings
    if os.getenv('API_HOST'):
        config['api']['host'] = os.getenv('API_HOST')
    if os.getenv('API_PORT'):
        config['api']['port'] = int(os.getenv('API_PORT'))

    # Dashboard settings
    if os.getenv('DASHBOARD_PORT'):
        config['dashboard']['port'] = int(os.getenv('DASHBOARD_PORT'))

    return config


def get_config_value(config: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Get nested config value using dot notation

    Args:
        config: Configuration dictionary
        path: Dot-separated path (e.g., 'app.debug')
        default: Default value if path doesn't exist

    Returns:
        Config value or default
    """
    keys = path.split('.')
    value = config

    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default
