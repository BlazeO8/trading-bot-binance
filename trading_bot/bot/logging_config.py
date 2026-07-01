"""Logging configuration for the trading bot"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    """
    Configure and return a logger instance with file and console handlers.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Log file path with timestamp
    log_filename = log_dir / f"trading_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_filename,
        maxBytes=2097152,  # 2MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
