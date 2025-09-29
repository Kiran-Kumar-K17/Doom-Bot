"""
Logger setup for Iron Doom Jarvis
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "iron_doom_jarvis", level: str = "INFO") -> logging.Logger:
    """Setup logger with file and console handlers"""
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    log_file = os.path.join(logs_dir, f"{name}.log")
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log startup message
    logger.info(f"Logger initialized for {name}")
    
    return logger

def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """Log error with context"""
    error_msg = f"{context}: {type(error).__name__}: {str(error)}" if context else f"{type(error).__name__}: {str(error)}"
    logger.error(error_msg, exc_info=True)

def log_api_request(logger: logging.Logger, service: str, endpoint: str, status: int, duration: float):
    """Log API request details"""
    logger.info(f"API Request - {service} {endpoint} - Status: {status} - Duration: {duration:.2f}s")

def log_command_usage(logger: logging.Logger, user: str, command: str, args: str = ""):
    """Log Discord command usage"""
    logger.info(f"Command Used - User: {user} - Command: {command} - Args: {args}")

def log_scheduler_task(logger: logging.Logger, task_name: str, status: str, duration: float = None):
    """Log scheduled task execution"""
    if duration:
        logger.info(f"Scheduled Task - {task_name} - Status: {status} - Duration: {duration:.2f}s")
    else:
        logger.info(f"Scheduled Task - {task_name} - Status: {status}")
        
def log_user_interaction(logger: logging.Logger, user: str, action: str, details: str = ""):
    """Log user interactions for analytics"""
    logger.info(f"User Interaction - User: {user} - Action: {action} - Details: {details}")

class ContextLogger:
    """Context manager for logging function execution"""
    
    def __init__(self, logger: logging.Logger, func_name: str, log_level: str = "DEBUG"):
        self.logger = logger
        self.func_name = func_name
        self.log_level = getattr(logging, log_level.upper())
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log(self.log_level, f"Starting {self.func_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type:
            self.logger.error(f"Error in {self.func_name} after {duration:.2f}s: {exc_val}")
        else:
            self.logger.log(self.log_level, f"Completed {self.func_name} in {duration:.2f}s")

def setup_service_logger(service_name: str) -> logging.Logger:
    """Setup logger for a specific service"""
    logger_name = f"iron_doom_jarvis.{service_name}"
    return setup_logger(logger_name)