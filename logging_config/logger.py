"""Comprehensive logging configuration for Sports Analytics Intelligence System."""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        """Format log record with colors."""
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Add color to level name
        record.levelname = f"{log_color}{record.levelname}{reset}"
        
        return super().format(record)


def setup_logging(log_level: str = 'INFO', 
                 log_file: Optional[str] = None,
                 console_output: bool = True) -> None:
    """
    Setup comprehensive logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        console_output: Whether to output logs to console
    """
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Create formatters
    console_format = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    file_format = '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
    
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Console handler with colors
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        
        colored_formatter = ColoredFormatter(console_format, datefmt=date_format)
        console_handler.setFormatter(colored_formatter)
        
        root_logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # File gets all logs
        
        file_formatter = logging.Formatter(file_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        
        root_logger.addHandler(file_handler)
    
    # Log startup message
    root_logger.info("=" * 70)
    root_logger.info("Sports Analytics Intelligence System - Logging Initialized")
    root_logger.info(f"Log Level: {log_level}")
    root_logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if log_file:
        root_logger.info(f"Log File: {log_file}")
    root_logger.info("=" * 70)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Name of the module (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class PerformanceLogger:
    """Logger for tracking performance metrics."""
    
    def __init__(self, name: str):
        """
        Initialize performance logger.
        
        Args:
            name: Name for this performance logger
        """
        self.logger = get_logger(f"performance.{name}")
        self.start_times = {}
    
    def start(self, operation: str) -> None:
        """
        Start timing an operation.
        
        Args:
            operation: Name of the operation
        """
        import time
        self.start_times[operation] = time.time()
        self.logger.debug(f"Started: {operation}")
    
    def end(self, operation: str) -> float:
        """
        End timing an operation and log the duration.
        
        Args:
            operation: Name of the operation
            
        Returns:
            Duration in seconds
        """
        import time
        if operation not in self.start_times:
            self.logger.warning(f"No start time found for operation: {operation}")
            return 0.0
        
        duration = time.time() - self.start_times[operation]
        self.logger.info(f"Completed: {operation} (Duration: {duration:.2f}s)")
        
        del self.start_times[operation]
        return duration
    
    def log_metric(self, metric_name: str, value: float, unit: str = "") -> None:
        """
        Log a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
        """
        unit_str = f" {unit}" if unit else ""
        self.logger.info(f"Metric: {metric_name} = {value:.2f}{unit_str}")
