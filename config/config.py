"""Configuration management for Sports Analytics Intelligence System."""

import yaml
import os
from pathlib import Path
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for loading and accessing application settings."""
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        """Singleton pattern to ensure only one config instance exists."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager."""
        if not self._config:
            self.load_config()
    
    def load_config(self, config_path: str = None) -> None:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file. If None, uses default.
        """
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                'config.yaml'
            )
        
        try:
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
            self._set_defaults()
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            self._set_defaults()
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        self._config = {
            'video': {
                'fps': 24,
                'codec': 'mp4v'
            },
            'models': {
                'confidence_threshold': 0.5,
                'iou_threshold': 0.45
            },
            'tracking': {
                'use_stub': False,
                'interpolate_ball': True
            },
            'analytics': {
                'generate_heatmaps': True,
                'track_formations': True,
                'analyze_passes': True,
                'export_statistics': True
            },
            'logging': {
                'level': 'INFO',
                'console_output': True
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Configuration key path (e.g., 'video.fps')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Examples:
            >>> config.get('video.fps')
            24
            >>> config.get('models.confidence_threshold')
            0.5
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            logger.debug(f"Config key '{key_path}' not found, using default: {default}")
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Configuration key path (e.g., 'video.fps')
            value: Value to set
        """
        keys = key_path.split('.')
        config = self._config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        logger.debug(f"Config '{key_path}' set to {value}")
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Complete configuration dictionary
        """
        return self._config.copy()
    
    def save_config(self, output_path: str = None) -> None:
        """
        Save current configuration to YAML file.
        
        Args:
            output_path: Path where to save the configuration
        """
        if output_path is None:
            output_path = os.path.join(
                os.path.dirname(__file__),
                'config.yaml'
            )
        
        try:
            with open(output_path, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)
            logger.info(f"Configuration saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def create_directories(self) -> None:
        """Create necessary directories based on configuration."""
        dirs_to_create = [
            self.get('video.output_path', 'output_videos/'),
            self.get('export.export_path', 'analytics_output/'),
            self.get('logging.log_file', 'logs/sports_analytics.log'),
            'stubs/',
            'models/'
        ]
        
        for dir_path in dirs_to_create:
            path = Path(dir_path).parent if '.' in dir_path else Path(dir_path)
            path.mkdir(parents=True, exist_ok=True)
        
        logger.info("Required directories created")


# Global configuration instance
config = Config()
