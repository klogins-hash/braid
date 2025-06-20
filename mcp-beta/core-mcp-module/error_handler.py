"""
Enhanced Error Handling and Retry Logic for MCP Operations
Provides robust error handling, retry mechanisms, and failure recovery for MCP integrations.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum
import random

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RetryStrategy(Enum):
    """Retry strategy types."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_INTERVAL = "fixed_interval"
    IMMEDIATE = "immediate"


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    jitter: bool = True
    backoff_multiplier: float = 2.0


@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    timestamp: datetime
    mcp_id: str
    operation: str
    error_type: str
    error_message: str
    severity: ErrorSeverity
    retry_count: int
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None


class MCPErrorHandler:
    """Comprehensive error handling and retry system for MCP operations."""
    
    def __init__(self, default_retry_config: Optional[RetryConfig] = None):
        """Initialize error handler.
        
        Args:
            default_retry_config: Default retry configuration
        """
        self.default_retry_config = default_retry_config or RetryConfig()
        self.error_history: List[ErrorRecord] = []
        self.operation_configs: Dict[str, RetryConfig] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
    
    def configure_operation(self, operation: str, retry_config: RetryConfig):
        """Configure retry behavior for a specific operation.
        
        Args:
            operation: Operation name (e.g., 'mcp_connection', 'tool_execution')
            retry_config: Retry configuration for this operation
        """
        self.operation_configs[operation] = retry_config
        logger.info(f"Configured retry behavior for operation: {operation}")
    
    async def execute_with_retry(
        self,
        operation: str,
        func: Callable,
        mcp_id: str,
        *args,
        retry_config: Optional[RetryConfig] = None,
        **kwargs
    ) -> Any:
        """Execute a function with retry logic.
        
        Args:
            operation: Name of the operation being performed
            func: Function to execute
            mcp_id: MCP identifier for error tracking
            retry_config: Custom retry configuration for this execution
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Result of the function execution
            
        Raises:
            Exception: If all retries are exhausted
        """
        config = retry_config or self.operation_configs.get(operation, self.default_retry_config)
        
        # Check circuit breaker
        if self._is_circuit_open(mcp_id, operation):
            raise Exception(f"Circuit breaker open for {mcp_id}:{operation}")
        
        last_exception = None
        
        for attempt in range(config.max_retries + 1):
            try:
                # Execute the function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Success - reset circuit breaker and return
                self._reset_circuit_breaker(mcp_id, operation)
                
                # Mark any previous errors as resolved
                self._mark_errors_resolved(mcp_id, operation)
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Record the error
                error_record = self._record_error(
                    mcp_id=mcp_id,
                    operation=operation,
                    error=e,
                    retry_count=attempt
                )
                
                # Check if we should retry
                if attempt >= config.max_retries:
                    # All retries exhausted
                    self._update_circuit_breaker(mcp_id, operation, error_record)
                    logger.error(
                        f"All retries exhausted for {mcp_id}:{operation}. "
                        f"Final error: {str(e)}"
                    )
                    break
                
                # Calculate delay for next retry
                delay = self._calculate_retry_delay(config, attempt)
                
                logger.warning(
                    f"Retry {attempt + 1}/{config.max_retries} for {mcp_id}:{operation} "
                    f"after {delay:.2f}s. Error: {str(e)}"
                )
                
                # Wait before retrying
                await asyncio.sleep(delay)
        
        # All retries failed
        raise last_exception
    
    def _calculate_retry_delay(self, config: RetryConfig, attempt: int) -> float:
        """Calculate delay before next retry attempt.
        
        Args:
            config: Retry configuration
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        if config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = config.base_delay * (config.backoff_multiplier ** attempt)
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = config.base_delay * (attempt + 1)
        elif config.strategy == RetryStrategy.FIXED_INTERVAL:
            delay = config.base_delay
        else:  # IMMEDIATE
            delay = 0.0
        
        # Apply maximum delay limit
        delay = min(delay, config.max_delay)
        
        # Add jitter to prevent thundering herd
        if config.jitter and delay > 0:
            jitter_amount = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_amount, jitter_amount)
        
        return max(0.0, delay)
    
    def _record_error(
        self,
        mcp_id: str,
        operation: str,
        error: Exception,
        retry_count: int
    ) -> ErrorRecord:
        """Record an error occurrence.
        
        Args:
            mcp_id: MCP identifier
            operation: Operation name
            error: Exception that occurred
            retry_count: Current retry attempt
            
        Returns:
            Created error record
        """
        # Determine error severity
        severity = self._classify_error_severity(error)
        
        error_record = ErrorRecord(
            timestamp=datetime.now(),
            mcp_id=mcp_id,
            operation=operation,
            error_type=type(error).__name__,
            error_message=str(error),
            severity=severity,
            retry_count=retry_count
        )
        
        self.error_history.append(error_record)
        
        # Keep only recent errors (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.error_history = [
            record for record in self.error_history
            if record.timestamp > cutoff_time
        ]
        
        return error_record
    
    def _classify_error_severity(self, error: Exception) -> ErrorSeverity:
        """Classify error severity based on error type and message.
        
        Args:
            error: Exception to classify
            
        Returns:
            Error severity level
        """
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Critical errors (system-level failures)
        if error_type in ['MemoryError', 'SystemExit', 'KeyboardInterrupt']:
            return ErrorSeverity.CRITICAL
        
        # High severity (authentication, permission, configuration)
        if any(keyword in error_message for keyword in [
            'authentication', 'unauthorized', 'forbidden', 'permission denied',
            'invalid credentials', 'api key', 'access denied'
        ]):
            return ErrorSeverity.HIGH
        
        # Medium severity (network, timeout, service unavailable)
        if any(keyword in error_message for keyword in [
            'timeout', 'connection', 'network', 'unavailable', 'service',
            'rate limit', 'quota exceeded'
        ]):
            return ErrorSeverity.MEDIUM
        
        # Default to low severity
        return ErrorSeverity.LOW
    
    def _mark_errors_resolved(self, mcp_id: str, operation: str):
        """Mark previous errors as resolved for successful operations.
        
        Args:
            mcp_id: MCP identifier
            operation: Operation name
        """
        for record in self.error_history:
            if (record.mcp_id == mcp_id and 
                record.operation == operation and 
                not record.resolved):
                record.resolved = True
                record.resolution_timestamp = datetime.now()
    
    def _is_circuit_open(self, mcp_id: str, operation: str) -> bool:
        """Check if circuit breaker is open for an MCP operation.
        
        Args:
            mcp_id: MCP identifier
            operation: Operation name
            
        Returns:
            True if circuit is open (should not attempt operation)
        """
        circuit_key = f"{mcp_id}:{operation}"
        circuit = self.circuit_breakers.get(circuit_key)
        
        if not circuit:
            return False
        
        # Check if circuit should be reset
        if datetime.now() > circuit['reset_time']:
            del self.circuit_breakers[circuit_key]
            return False
        
        return circuit['state'] == 'open'
    
    def _update_circuit_breaker(self, mcp_id: str, operation: str, error_record: ErrorRecord):
        """Update circuit breaker state based on error.
        
        Args:
            mcp_id: MCP identifier
            operation: Operation name
            error_record: Error that triggered the update
        """
        circuit_key = f"{mcp_id}:{operation}"
        
        # Count recent failures
        recent_errors = [
            record for record in self.error_history
            if (record.mcp_id == mcp_id and 
                record.operation == operation and
                record.timestamp > datetime.now() - timedelta(minutes=5))
        ]
        
        failure_count = len(recent_errors)
        
        # Open circuit if too many failures
        if failure_count >= 5:  # 5 failures in 5 minutes
            reset_time = datetime.now() + timedelta(minutes=10)  # 10 minute cooldown
            
            self.circuit_breakers[circuit_key] = {
                'state': 'open',
                'failure_count': failure_count,
                'last_failure': error_record.timestamp,
                'reset_time': reset_time
            }
            
            logger.warning(
                f"Circuit breaker opened for {mcp_id}:{operation} "
                f"due to {failure_count} failures. Reset at {reset_time}"
            )
    
    def _reset_circuit_breaker(self, mcp_id: str, operation: str):
        """Reset circuit breaker after successful operation.
        
        Args:
            mcp_id: MCP identifier
            operation: Operation name
        """
        circuit_key = f"{mcp_id}:{operation}"
        if circuit_key in self.circuit_breakers:
            del self.circuit_breakers[circuit_key]
            logger.info(f"Circuit breaker reset for {mcp_id}:{operation}")
    
    def get_error_summary(self, mcp_id: Optional[str] = None) -> Dict[str, Any]:
        """Get error summary for monitoring and debugging.
        
        Args:
            mcp_id: Optional MCP ID to filter errors
            
        Returns:
            Error summary statistics
        """
        filtered_errors = self.error_history
        if mcp_id:
            filtered_errors = [e for e in filtered_errors if e.mcp_id == mcp_id]
        
        if not filtered_errors:
            return {
                "total_errors": 0,
                "error_rate": 0.0,
                "by_severity": {},
                "by_type": {},
                "recent_errors": []
            }
        
        # Calculate statistics
        total_errors = len(filtered_errors)
        resolved_errors = sum(1 for e in filtered_errors if e.resolved)
        
        # Group by severity
        by_severity = {}
        for error in filtered_errors:
            severity = error.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        # Group by error type
        by_type = {}
        for error in filtered_errors:
            error_type = error.error_type
            by_type[error_type] = by_type.get(error_type, 0) + 1
        
        # Recent errors (last hour)
        recent_cutoff = datetime.now() - timedelta(hours=1)
        recent_errors = [
            {
                "timestamp": e.timestamp.isoformat(),
                "mcp_id": e.mcp_id,
                "operation": e.operation,
                "error_type": e.error_type,
                "severity": e.severity.value,
                "message": e.error_message[:200]  # Truncate long messages
            }
            for e in filtered_errors
            if e.timestamp > recent_cutoff
        ]
        
        return {
            "total_errors": total_errors,
            "resolved_errors": resolved_errors,
            "resolution_rate": resolved_errors / total_errors if total_errors > 0 else 0.0,
            "by_severity": by_severity,
            "by_type": by_type,
            "recent_errors": recent_errors[-10:],  # Last 10 recent errors
            "circuit_breakers": {
                key: {
                    "state": circuit["state"],
                    "failure_count": circuit["failure_count"],
                    "reset_time": circuit["reset_time"].isoformat()
                }
                for key, circuit in self.circuit_breakers.items()
            }
        }
    
    def create_operation_wrapper(self, operation: str, mcp_id: str):
        """Create a decorator for automatic error handling.
        
        Args:
            operation: Operation name
            mcp_id: MCP identifier
            
        Returns:
            Decorator function
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                return await self.execute_with_retry(
                    operation=operation,
                    func=func,
                    mcp_id=mcp_id,
                    *args,
                    **kwargs
                )
            return wrapper
        return decorator