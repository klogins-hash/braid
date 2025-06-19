"""Production monitoring and health check system."""

import logging
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

from .config import config

logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check endpoints."""
    
    def log_message(self, format, *args):
        """Override to use our logger instead of stderr."""
        logger.debug(format % args)
    
    def do_GET(self):
        """Handle GET requests for health checks."""
        if self.path == "/health":
            self._health_check()
        elif self.path == "/metrics":
            self._metrics()
        elif self.path == "/ready":
            self._readiness_check()
        else:
            self._not_found()
    
    def _health_check(self):
        """Basic health check - is the service running?"""
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "environment": config.ENVIRONMENT,
                "version": "1.0.0"
            }
            
            self._json_response(200, health_status)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self._json_response(500, {"status": "unhealthy", "error": str(e)})
    
    def _readiness_check(self):
        """Readiness check - are all dependencies available?"""
        try:
            readiness_status = {
                "status": "ready",
                "timestamp": datetime.now().isoformat(),
                "dependencies": self._check_dependencies()
            }
            
            # If any critical dependency is down, mark as not ready
            if not all(dep["status"] == "ok" for dep in readiness_status["dependencies"].values() if dep.get("critical", False)):
                readiness_status["status"] = "not_ready"
                self._json_response(503, readiness_status)
            else:
                self._json_response(200, readiness_status)
                
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            self._json_response(500, {"status": "error", "error": str(e)})
    
    def _check_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Check status of external dependencies."""
        dependencies = {}
        
        # Check OpenAI API
        dependencies["openai"] = self._check_api_key("OpenAI", config.OPENAI_API_KEY, critical=True)
        
        # Check Xero API
        dependencies["xero"] = self._check_xero_connection()
        
        # Check Perplexity API
        dependencies["perplexity"] = self._check_api_key("Perplexity", config.PERPLEXITY_API_KEY, critical=True)
        
        # Check Notion API (optional)
        if config.NOTION_API_KEY:
            dependencies["notion"] = self._check_notion_connection()
        else:
            dependencies["notion"] = {"status": "disabled", "critical": False}
        
        # Check LangSmith (optional but recommended)
        if config.LANGCHAIN_API_KEY:
            dependencies["langsmith"] = self._check_api_key("LangSmith", config.LANGCHAIN_API_KEY, critical=False)
        else:
            dependencies["langsmith"] = {"status": "disabled", "critical": False}
        
        return dependencies
    
    def _check_api_key(self, service_name: str, api_key: str, critical: bool = True) -> Dict[str, Any]:
        """Check if API key is configured."""
        if not api_key or api_key == "":
            return {
                "status": "error", 
                "message": f"{service_name} API key not configured",
                "critical": critical
            }
        
        if api_key.startswith("your_") or api_key == "dev-secret-key-change-in-production":
            return {
                "status": "error",
                "message": f"{service_name} API key appears to be placeholder",
                "critical": critical
            }
        
        return {
            "status": "ok",
            "message": f"{service_name} API key configured",
            "critical": critical
        }
    
    def _check_xero_connection(self) -> Dict[str, Any]:
        """Check Xero API connection."""
        try:
            if not config.XERO_ACCESS_TOKEN:
                return {
                    "status": "error",
                    "message": "Xero access token not configured",
                    "critical": True
                }
            
            # Test connection
            headers = {
                'Authorization': f'Bearer {config.XERO_ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://api.xero.com/connections',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                connections = response.json()
                return {
                    "status": "ok",
                    "message": f"Connected to {len(connections)} organizations",
                    "critical": True,
                    "connections": len(connections)
                }
            else:
                return {
                    "status": "error",
                    "message": f"Xero API returned {response.status_code}",
                    "critical": True
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Xero connection failed: {str(e)}",
                "critical": True
            }
    
    def _check_notion_connection(self) -> Dict[str, Any]:
        """Check Notion API connection."""
        try:
            headers = {
                'Authorization': f'Bearer {config.NOTION_API_KEY}',
                'Notion-Version': '2022-06-28'
            }
            
            response = requests.get(
                'https://api.notion.com/v1/users/me',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "status": "ok",
                    "message": "Notion API connected",
                    "critical": False
                }
            else:
                return {
                    "status": "error",
                    "message": f"Notion API returned {response.status_code}",
                    "critical": False
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Notion connection failed: {str(e)}",
                "critical": False
            }
    
    def _metrics(self):
        """Return application metrics."""
        try:
            metrics = AgentMetrics.get_metrics()
            self._json_response(200, metrics)
        except Exception as e:
            logger.error(f"Metrics endpoint failed: {e}")
            self._json_response(500, {"error": str(e)})
    
    def _json_response(self, status_code: int, data: Dict[str, Any]):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def _not_found(self):
        """Return 404 for unknown endpoints."""
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Not found"}).encode())

class AgentMetrics:
    """Collect and store application metrics."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AgentMetrics, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.start_time = datetime.now()
            self.request_count = 0
            self.error_count = 0
            self.forecast_count = 0
            self.api_call_times = {}
            self.last_forecast = None
            self._initialized = True
    
    def record_request(self):
        """Record a new request."""
        self.request_count += 1
    
    def record_error(self):
        """Record an error."""
        self.error_count += 1
    
    def record_forecast(self, user_id: str):
        """Record a successful forecast."""
        self.forecast_count += 1
        self.last_forecast = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def record_api_call(self, api_name: str, duration: float):
        """Record API call timing."""
        if api_name not in self.api_call_times:
            self.api_call_times[api_name] = []
        self.api_call_times[api_name].append(duration)
        
        # Keep only last 100 calls for memory efficiency
        if len(self.api_call_times[api_name]) > 100:
            self.api_call_times[api_name] = self.api_call_times[api_name][-100:]
    
    @classmethod
    def get_metrics(cls) -> Dict[str, Any]:
        """Get current metrics."""
        instance = cls()
        uptime = datetime.now() - instance.start_time
        
        metrics = {
            "uptime_seconds": int(uptime.total_seconds()),
            "requests_total": instance.request_count,
            "errors_total": instance.error_count,
            "forecasts_total": instance.forecast_count,
            "last_forecast": instance.last_forecast,
            "error_rate": (instance.error_count / max(instance.request_count, 1)) * 100,
        }
        
        # Add API timing statistics
        for api_name, times in instance.api_call_times.items():
            if times:
                metrics[f"{api_name}_avg_response_time"] = sum(times) / len(times)
                metrics[f"{api_name}_max_response_time"] = max(times)
                metrics[f"{api_name}_call_count"] = len(times)
        
        return metrics

def start_health_server():
    """Start the health check HTTP server."""
    try:
        server = HTTPServer(('0.0.0.0', config.HEALTH_CHECK_PORT), HealthCheckHandler)
        logger.info(f"Health check server starting on port {config.HEALTH_CHECK_PORT}")
        
        # Run in a separate thread so it doesn't block the main application
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        
        return server
    except Exception as e:
        logger.error(f"Failed to start health check server: {e}")
        return None

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

# Global metrics instance
metrics = AgentMetrics()