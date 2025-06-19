"""Production error handling and recovery mechanisms."""

import logging
import time
import traceback
from typing import Any, Callable, Optional, Dict
from functools import wraps
from datetime import datetime

from .config import config
from .monitoring import metrics

logger = logging.getLogger(__name__)

class ProductionError(Exception):
    """Base exception for production-specific errors."""
    pass

class APIConnectionError(ProductionError):
    """Raised when API connections fail."""
    pass

class AuthenticationError(ProductionError):
    """Raised when API authentication fails."""
    pass

class RateLimitError(ProductionError):
    """Raised when API rate limits are exceeded."""
    pass

class DataValidationError(ProductionError):
    """Raised when data validation fails."""
    pass

def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for retrying functions with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        wait_time = backoff_factor * (2 ** (attempt - 1))
                        logger.warning(f"Retry attempt {attempt}/{max_retries} for {func.__name__} in {wait_time}s")
                        time.sleep(wait_time)
                    
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    
                    # Record successful API call timing
                    duration = time.time() - start_time
                    if hasattr(func, '__name__') and 'api' in func.__name__.lower():
                        metrics.record_api_call(func.__name__, duration)
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    metrics.record_error()
                    
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        break
                    else:
                        logger.warning(f"Function {func.__name__} failed on attempt {attempt + 1}: {e}")
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    return decorator

def handle_api_errors(func: Callable) -> Callable:
    """Decorator for handling API-specific errors."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Convert common errors to our custom exceptions
            error_message = str(e).lower()
            
            if "401" in error_message or "unauthorized" in error_message:
                raise AuthenticationError(f"Authentication failed: {e}")
            elif "429" in error_message or "rate limit" in error_message:
                raise RateLimitError(f"Rate limit exceeded: {e}")
            elif "connection" in error_message or "timeout" in error_message:
                raise APIConnectionError(f"API connection failed: {e}")
            else:
                # Re-raise as is if not a known API error
                raise
    
    return wrapper

def safe_execute(func: Callable, fallback_value: Any = None, log_errors: bool = True) -> Any:
    """Safely execute a function with error handling."""
    try:
        return func()
    except Exception as e:
        if log_errors:
            logger.error(f"Safe execution failed for {func.__name__ if hasattr(func, '__name__') else 'function'}: {e}")
            if config.LOG_LEVEL == "DEBUG":
                logger.debug(traceback.format_exc())
        
        metrics.record_error()
        return fallback_value

class ProductionLogger:
    """Enhanced logging for production environment."""
    
    @staticmethod
    def log_api_call(api_name: str, endpoint: str, status_code: Optional[int] = None, duration: Optional[float] = None):
        """Log API call details."""
        log_data = {
            "api": api_name,
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat()
        }
        
        if status_code:
            log_data["status_code"] = status_code
        
        if duration:
            log_data["duration_ms"] = round(duration * 1000, 2)
        
        if status_code and status_code >= 400:
            logger.error(f"API call failed: {log_data}")
        else:
            logger.info(f"API call successful: {log_data}")
    
    @staticmethod
    def log_forecast_request(user_id: str, forecast_type: str = "standard"):
        """Log forecast request."""
        logger.info(f"Forecast request started: user_id={user_id}, type={forecast_type}")
        metrics.record_request()
    
    @staticmethod
    def log_forecast_completion(user_id: str, success: bool, duration: float):
        """Log forecast completion."""
        if success:
            logger.info(f"Forecast completed successfully: user_id={user_id}, duration={duration:.2f}s")
            metrics.record_forecast(user_id)
        else:
            logger.error(f"Forecast failed: user_id={user_id}, duration={duration:.2f}s")
            metrics.record_error()
    
    @staticmethod
    def log_data_source(source_name: str, is_live: bool, record_count: Optional[int] = None):
        """Log data source information."""
        source_type = "LIVE" if is_live else "FALLBACK"
        log_msg = f"Data source: {source_name} ({source_type})"
        
        if record_count is not None:
            log_msg += f" - {record_count} records"
        
        if is_live:
            logger.info(log_msg)
        else:
            logger.warning(log_msg)

def validate_environment():
    """Validate production environment configuration."""
    logger.info("Validating production environment...")
    
    # Check required environment variables
    missing_vars = config.validate_required_env_vars()
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ProductionError(error_msg)
    
    # Validate API keys format
    if config.OPENAI_API_KEY.startswith("sk-") is False:
        logger.warning("OpenAI API key format appears invalid")
    
    if config.XERO_ACCESS_TOKEN and not config.XERO_ACCESS_TOKEN.startswith("eyJ"):
        logger.warning("Xero access token format appears invalid (should be JWT)")
    
    # Check production-specific settings
    if config.is_production():
        if config.SECRET_KEY == "dev-secret-key-change-in-production":
            raise ProductionError("SECRET_KEY must be changed for production deployment")
        
        if "localhost" in config.ALLOWED_HOSTS and len(config.ALLOWED_HOSTS) == 1:
            logger.warning("ALLOWED_HOSTS contains only localhost in production")
    
    logger.info("Environment validation completed successfully")

class CircuitBreaker:
    """Circuit breaker pattern for API calls."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time < self.timeout:
                raise APIConnectionError("Circuit breaker is OPEN")
            else:
                self.state = "HALF_OPEN"
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Reset circuit breaker on successful call."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Handle failure in circuit breaker."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(f"Circuit breaker opened after {self.failure_count} failures")

# Global circuit breakers for different APIs
xero_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=60)
perplexity_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30)
notion_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=120)