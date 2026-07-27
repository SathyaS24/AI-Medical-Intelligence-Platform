import os
import logging
from logging.handlers import RotatingFileHandler
from backend.config import LOG_DIR, LOG_LEVEL

def setup_logger(name: str = "medical_platform") -> logging.Logger:
    """Configures and returns a logger that outputs to both console and rotating file handler."""
    logger = logging.getLogger(name)
    
    # Set log level
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if logger is already configured
    if logger.handlers:
        return logger
        
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Rotating File Handler (10MB max, keeping 5 backup logs)
    log_file_path = os.path.join(LOG_DIR, "application.log")
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Create pre-configured instance
logger = setup_logger()
