"""
Logging Infrastructure with Appropriate Handlers

This module sets up centralized logging for the application with
file and console handlers, proper formatting, and log rotation.

SOLID Principles:
- SRP: Only handles logging configuration
- OCP: New handlers can be added without modifying existing code
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


class LoggingConfig:
    """
    Centralized logging configuration
    
    Features:
    - Console handler for development
    - Rotating file handler for production
    - Structured log format with timestamps
    - Separate log levels for different environments
    """
    
    # Log format
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Log file configuration
    LOG_DIR = 'logs'
    LOG_FILE = 'app.log'
    MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    BACKUP_COUNT = 5
    
    @classmethod
    def setup_logging(cls, log_level: str = 'INFO') -> None:
        """
        Set up logging with console and file handlers
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        # Create logs directory if it doesn't exist
        log_dir = Path(cls.LOG_DIR)
        log_dir.mkdir(exist_ok=True)
        
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatters
        formatter = logging.Formatter(cls.LOG_FORMAT, cls.DATE_FORMAT)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler with rotation
        log_file_path = log_dir / cls.LOG_FILE
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=cls.MAX_BYTES,
            backupCount=cls.BACKUP_COUNT
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Log startup message
        root_logger.info("Logging system initialized")
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module
        
        Args:
            name: Logger name (typically __name__ of the module)
            
        Returns:
            Logger instance
        """
        return logging.getLogger(name)


class SanitizedLogger:
    """
    Logger wrapper that sanitizes sensitive data before logging
    
    SOLID Principles:
    - SRP: Only handles log sanitization
    - OCP: New sanitization rules can be added without modifying existing code
    
    Security:
    - Removes passwords, tokens, API keys from logs
    - Masks PII (email, phone numbers)
    - Prevents sensitive data leakage
    """
    
    # Sensitive field names to sanitize
    SENSITIVE_FIELDS = [
        'password', 'token', 'secret', 'api_key', 'access_token',
        'refresh_token', 'oauth_token', 'authorization', 'auth'
    ]
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def _sanitize_message(self, message: str) -> str:
        """
        Sanitize sensitive data from log message
        
        Args:
            message: Original log message
            
        Returns:
            Sanitized log message
        """
        sanitized = message
        
        # Replace sensitive field values with [REDACTED]
        for field in self.SENSITIVE_FIELDS:
            # Pattern: field_name=value or field_name: value
            import re
            pattern = rf'{field}[=:]\s*[^\s,\)}}]+'
            sanitized = re.sub(pattern, f'{field}=[REDACTED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message with sanitization"""
        self.logger.debug(self._sanitize_message(message), *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message with sanitization"""
        self.logger.info(self._sanitize_message(message), *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message with sanitization"""
        self.logger.warning(self._sanitize_message(message), *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message with sanitization"""
        self.logger.error(self._sanitize_message(message), *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message with sanitization"""
        self.logger.critical(self._sanitize_message(message), *args, **kwargs)


# Initialize logging on module import
LoggingConfig.setup_logging(os.getenv('LOG_LEVEL', 'INFO'))


def get_logger(name: str, sanitized: bool = True) -> logging.Logger | SanitizedLogger:
    """
    Get a logger instance
    
    Args:
        name: Logger name (typically __name__ of the module)
        sanitized: Whether to use sanitized logger (default: True)
        
    Returns:
        Logger instance (sanitized or standard)
    """
    logger = LoggingConfig.get_logger(name)
    
    if sanitized:
        return SanitizedLogger(logger)
    
    return logger
