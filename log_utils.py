"""Centralized logging for Action Service"""
import logging
from typing import Optional
from functools import wraps
import time
import asyncio

class ActionServiceLogger:
    """Centralized logging for Action Service"""
    
    def __init__(self, debug_mode: bool = False):
        self.logger = logging.getLogger("action_service")
        level = logging.DEBUG if debug_mode else logging.INFO
        self.logger.setLevel(level)
        
        # Add console handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def debug(self, message: str, correlation_id: Optional[str] = None):
        """Log debug message with optional correlation ID"""
        if correlation_id:
            message = f"[{correlation_id}] {message}"
        self.logger.debug(message)

    def info(self, message: str, correlation_id: Optional[str] = None):
        """Log info message with optional correlation ID"""
        if correlation_id:
            message = f"[{correlation_id}] {message}"
        self.logger.info(message)

    def error(self, message: str, correlation_id: Optional[str] = None, exc_info=None):
        """Log error message with optional correlation ID and exception info"""
        if correlation_id:
            message = f"[{correlation_id}] {message}"
        self.logger.error(message, exc_info=exc_info)

def log_execution_time(logger: ActionServiceLogger):
    """Decorator to log execution time of functions"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            correlation_id = kwargs.get('correlation_id')
            
            logger.debug(
                f"Starting {func.__name__}",
                correlation_id=correlation_id
            )
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.debug(
                    f"Completed {func.__name__} in {execution_time:.2f}s",
                    correlation_id=correlation_id
                )
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"Failed {func.__name__} after {execution_time:.2f}s: {str(e)}",
                    correlation_id=correlation_id,
                    exc_info=True
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            correlation_id = kwargs.get('correlation_id')
            
            logger.debug(
                f"Starting {func.__name__}",
                correlation_id=correlation_id
            )
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.debug(
                    f"Completed {func.__name__} in {execution_time:.2f}s",
                    correlation_id=correlation_id
                )
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"Failed {func.__name__} after {execution_time:.2f}s: {str(e)}",
                    correlation_id=correlation_id,
                    exc_info=True
                )
                raise
                
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
            
    return decorator
