"""
Structured logging configuration.
Provides JSON logging for production and console logging for development.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from config import get_settings

settings = get_settings()


class JSONFormatter(logging.Formatter):
    """JSON log formatter for production."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        return json.dumps(log_data)


def setup_logging():
    """Configure logging based on environment."""
    # Determine log level
    log_level = getattr(logging, settings.log_level if hasattr(settings, 'log_level') else 'INFO')
    
    # Create logger
    logger = logging.getLogger("mavilon")
    logger.setLevel(log_level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Use JSON formatter for production, simple formatter for development
    if hasattr(settings, 'environment') and settings.environment == "production":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


# Global logger instance
logger = setup_logging()
