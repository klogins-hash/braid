"""
MCP Health Monitoring and Diagnostics System
Provides comprehensive health checking, monitoring, and diagnostics for MCP servers.
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Health check result."""
    mcp_id: str
    status: HealthStatus
    response_time: float
    timestamp: datetime
    details: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class MCPMetrics:
    """MCP performance metrics."""
    mcp_id: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    last_success: Optional[datetime]
    last_failure: Optional[datetime]
    uptime_percentage: float


class MCPHealthMonitor:
    """Comprehensive health monitoring system for MCP servers."""
    
    def __init__(self, check_interval: int = 30, history_retention: int = 1440):
        """Initialize health monitor.
        
        Args:
            check_interval: Health check interval in seconds
            history_retention: How many health check results to retain (minutes)
        """
        self.check_interval = check_interval
        self.history_retention = timedelta(minutes=history_retention)
        self.health_history: Dict[str, List[HealthCheck]] = {}
        self.metrics: Dict[str, MCPMetrics] = {}
        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None
    
    async def start_monitoring(self, mcp_configs: Dict[str, Dict[str, Any]]):
        """Start health monitoring for configured MCPs.
        
        Args:
            mcp_configs: Dictionary of MCP configurations
        """
        if self.running:
            logger.warning("Health monitoring already running")
            return
        
        self.running = True
        self.mcp_configs = mcp_configs
        
        # Initialize metrics for each MCP
        for mcp_id in mcp_configs:
            if mcp_id not in self.metrics:
                self.metrics[mcp_id] = MCPMetrics(
                    mcp_id=mcp_id,
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0,
                    average_response_time=0.0,
                    last_success=None,
                    last_failure=None,
                    uptime_percentage=100.0
                )
        
        # Start monitoring loop
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info(f"Started health monitoring for {len(mcp_configs)} MCPs")
    
    async def stop_monitoring(self):
        """Stop health monitoring."""
        if not self.running:
            return
        
        self.running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped health monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Perform health checks for all MCPs
                check_tasks = [
                    self._check_mcp_health(mcp_id, config)
                    for mcp_id, config in self.mcp_configs.items()
                ]
                
                results = await asyncio.gather(*check_tasks, return_exceptions=True)
                
                # Process results
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f"Health check failed: {result}")
                    elif isinstance(result, HealthCheck):
                        self._record_health_check(result)
                
                # Clean up old history
                self._cleanup_history()
                
                # Update metrics
                self._update_metrics()
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _check_mcp_health(self, mcp_id: str, config: Dict[str, Any]) -> HealthCheck:
        """Perform health check for a single MCP.
        
        Args:
            mcp_id: MCP identifier
            config: MCP configuration
            
        Returns:
            Health check result
        """
        start_time = time.time()
        
        try:
            # Determine health check method based on MCP type
            docker_required = config.get("docker_required", False)
            
            if docker_required:
                status, details = await self._check_docker_mcp(mcp_id, config)
            else:
                status, details = await self._check_subprocess_mcp(mcp_id, config)
            
            response_time = time.time() - start_time
            
            return HealthCheck(
                mcp_id=mcp_id,
                status=status,
                response_time=response_time,
                timestamp=datetime.now(),
                details=details
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            
            return HealthCheck(
                mcp_id=mcp_id,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                timestamp=datetime.now(),
                details={"error": str(e)},
                error_message=str(e)
            )
    
    async def _check_docker_mcp(self, mcp_id: str, config: Dict[str, Any]) -> Tuple[HealthStatus, Dict[str, Any]]:
        """Check health of Docker-based MCP."""
        try:
            import docker
            client = docker.from_env()
            
            # Find container by name pattern
            container_name = f"{mcp_id}-mcp-server"
            
            try:
                container = client.containers.get(container_name)
                
                # Check container status
                container.reload()
                state = container.attrs['State']
                
                if state['Status'] == 'running' and state['Health']['Status'] == 'healthy':
                    return HealthStatus.HEALTHY, {
                        "container_status": state['Status'],
                        "health_status": state['Health']['Status'],
                        "uptime": state.get('StartedAt'),
                        "restart_count": state.get('RestartCount', 0)
                    }
                elif state['Status'] == 'running':
                    return HealthStatus.DEGRADED, {
                        "container_status": state['Status'],
                        "health_status": state['Health'].get('Status', 'unknown'),
                        "issue": "Container running but health check failing"
                    }
                else:
                    return HealthStatus.UNHEALTHY, {
                        "container_status": state['Status'],
                        "error": state.get('Error', 'Container not running')
                    }
                    
            except docker.errors.NotFound:
                return HealthStatus.UNHEALTHY, {
                    "error": f"Container {container_name} not found"
                }
                
        except ImportError:
            return HealthStatus.UNKNOWN, {
                "error": "Docker client not available"
            }
        except Exception as e:
            return HealthStatus.UNHEALTHY, {
                "error": f"Docker health check failed: {str(e)}"
            }
    
    async def _check_subprocess_mcp(self, mcp_id: str, config: Dict[str, Any]) -> Tuple[HealthStatus, Dict[str, Any]]:
        """Check health of subprocess-based MCP (like NPX MCPs)."""
        try:
            # For subprocess MCPs, we check if the process would start successfully
            # This is a basic connectivity test
            
            command = config.get("command", "")
            args = config.get("args", [])
            
            if not command:
                return HealthStatus.UNKNOWN, {
                    "error": "No command specified for subprocess MCP"
                }
            
            # Try to run a quick test command
            process = await asyncio.create_subprocess_exec(
                command,
                "--help",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=10.0
            )
            
            if process.returncode == 0 or "help" in stdout.decode().lower():
                return HealthStatus.HEALTHY, {
                    "command_available": True,
                    "exit_code": process.returncode
                }
            else:
                return HealthStatus.DEGRADED, {
                    "command_available": True,
                    "exit_code": process.returncode,
                    "stderr": stderr.decode()[:500]  # Limit error output
                }
                
        except asyncio.TimeoutError:
            return HealthStatus.DEGRADED, {
                "error": "Health check timed out"
            }
        except FileNotFoundError:
            return HealthStatus.UNHEALTHY, {
                "error": f"Command not found: {command}"
            }
        except Exception as e:
            return HealthStatus.UNHEALTHY, {
                "error": f"Subprocess health check failed: {str(e)}"
            }
    
    def _record_health_check(self, health_check: HealthCheck):
        """Record health check result."""
        mcp_id = health_check.mcp_id
        
        if mcp_id not in self.health_history:
            self.health_history[mcp_id] = []
        
        self.health_history[mcp_id].append(health_check)
        
        # Update request metrics
        metrics = self.metrics[mcp_id]
        metrics.total_requests += 1
        
        if health_check.status == HealthStatus.HEALTHY:
            metrics.successful_requests += 1
            metrics.last_success = health_check.timestamp
        else:
            metrics.failed_requests += 1
            metrics.last_failure = health_check.timestamp
    
    def _cleanup_history(self):
        """Remove old health check records."""
        cutoff_time = datetime.now() - self.history_retention
        
        for mcp_id in self.health_history:
            self.health_history[mcp_id] = [
                check for check in self.health_history[mcp_id]
                if check.timestamp > cutoff_time
            ]
    
    def _update_metrics(self):
        """Update aggregated metrics."""
        for mcp_id, history in self.health_history.items():
            if not history:
                continue
            
            metrics = self.metrics[mcp_id]
            
            # Calculate average response time
            response_times = [check.response_time for check in history]
            metrics.average_response_time = sum(response_times) / len(response_times)
            
            # Calculate uptime percentage (last 24 hours)
            recent_checks = [
                check for check in history
                if check.timestamp > datetime.now() - timedelta(hours=24)
            ]
            
            if recent_checks:
                healthy_checks = sum(
                    1 for check in recent_checks
                    if check.status == HealthStatus.HEALTHY
                )
                metrics.uptime_percentage = (healthy_checks / len(recent_checks)) * 100
    
    def get_mcp_status(self, mcp_id: str) -> Dict[str, Any]:
        """Get current status for an MCP.
        
        Args:
            mcp_id: MCP identifier
            
        Returns:
            Current status information
        """
        if mcp_id not in self.health_history:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": "No health data available"
            }
        
        history = self.health_history[mcp_id]
        if not history:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": "No recent health checks"
            }
        
        latest = history[-1]
        metrics = self.metrics.get(mcp_id)
        
        return {
            "status": latest.status.value,
            "last_check": latest.timestamp.isoformat(),
            "response_time": latest.response_time,
            "details": latest.details,
            "error_message": latest.error_message,
            "metrics": asdict(metrics) if metrics else None
        }
    
    def get_overall_status(self) -> Dict[str, Any]:
        """Get overall system status.
        
        Returns:
            Overall status summary
        """
        if not self.health_history:
            return {
                "status": "unknown",
                "total_mcps": 0,
                "healthy_mcps": 0,
                "degraded_mcps": 0,
                "unhealthy_mcps": 0
            }
        
        status_counts = {
            "healthy": 0,
            "degraded": 0,
            "unhealthy": 0,
            "unknown": 0
        }
        
        for mcp_id in self.health_history:
            history = self.health_history[mcp_id]
            if history:
                latest_status = history[-1].status
                if latest_status == HealthStatus.HEALTHY:
                    status_counts["healthy"] += 1
                elif latest_status == HealthStatus.DEGRADED:
                    status_counts["degraded"] += 1
                elif latest_status == HealthStatus.UNHEALTHY:
                    status_counts["unhealthy"] += 1
                else:
                    status_counts["unknown"] += 1
        
        total_mcps = sum(status_counts.values())
        
        # Determine overall status
        if status_counts["unhealthy"] > 0:
            overall_status = "unhealthy"
        elif status_counts["degraded"] > 0:
            overall_status = "degraded"
        elif status_counts["healthy"] == total_mcps:
            overall_status = "healthy"
        else:
            overall_status = "unknown"
        
        return {
            "status": overall_status,
            "total_mcps": total_mcps,
            "healthy_mcps": status_counts["healthy"],
            "degraded_mcps": status_counts["degraded"],
            "unhealthy_mcps": status_counts["unhealthy"],
            "unknown_mcps": status_counts["unknown"],
            "uptime_percentage": self._calculate_overall_uptime()
        }
    
    def _calculate_overall_uptime(self) -> float:
        """Calculate overall system uptime percentage."""
        if not self.metrics:
            return 0.0
        
        uptimes = [metrics.uptime_percentage for metrics in self.metrics.values()]
        return sum(uptimes) / len(uptimes) if uptimes else 0.0
    
    def export_health_report(self, output_path: str):
        """Export comprehensive health report.
        
        Args:
            output_path: Path to save the report
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "overall_status": self.get_overall_status(),
            "mcp_statuses": {
                mcp_id: self.get_mcp_status(mcp_id)
                for mcp_id in self.health_history
            },
            "configuration": {
                "check_interval": self.check_interval,
                "history_retention_minutes": self.history_retention.total_seconds() / 60
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Health report exported to {output_path}")