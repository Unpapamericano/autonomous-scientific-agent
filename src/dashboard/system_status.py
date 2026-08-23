"""
Phase 10: System Status Monitoring

Monitors and reports on system health and resource usage.
"""

import logging
import psutil
from typing import Dict, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System health metrics."""
    cpu_percent: float  # 0-100
    memory_percent: float  # 0-100
    memory_used_gb: float
    memory_available_gb: float
    disk_percent: float  # 0-100
    disk_used_gb: float
    disk_available_gb: float
    timestamp: str
    status: str  # "healthy", "warning", "critical"


class SystemMonitor:
    """
    Monitors system resources and health.
    """

    def __init__(self, cpu_threshold: float = 80.0, memory_threshold: float = 85.0):
        """
        Initialize monitor.

        Args:
            cpu_threshold: CPU warning threshold (%)
            memory_threshold: Memory warning threshold (%)
        """
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.metrics_history = []

    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_available_gb = memory.available / (1024**3)

            # Disk
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024**3)
            disk_available_gb = disk.free / (1024**3)

            # Determine status
            if cpu_percent > self.cpu_threshold or memory_percent > self.memory_threshold:
                status = "warning"
            elif cpu_percent > 95 or memory_percent > 95:
                status = "critical"
            else:
                status = "healthy"

            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_gb=memory_used_gb,
                memory_available_gb=memory_available_gb,
                disk_percent=disk_percent,
                disk_used_gb=disk_used_gb,
                disk_available_gb=disk_available_gb,
                timestamp=datetime.utcnow().isoformat(),
                status=status,
            )

            self.metrics_history.append(metrics)
            logger.info(f"System metrics: CPU={cpu_percent:.1f}%, Mem={memory_percent:.1f}%")

            return metrics

        except Exception as e:
            logger.error(f"Failed to get system metrics: {str(e)}")
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_gb=0.0,
                memory_available_gb=0.0,
                disk_percent=0.0,
                disk_used_gb=0.0,
                disk_available_gb=0.0,
                timestamp=datetime.utcnow().isoformat(),
                status="unknown",
            )

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of recent metrics."""
        if not self.metrics_history:
            return {"total_samples": 0}

        recent = self.metrics_history[-10:]  # Last 10 samples

        avg_cpu = sum(m.cpu_percent for m in recent) / len(recent)
        avg_memory = sum(m.memory_percent for m in recent) / len(recent)

        return {
            "total_samples": len(self.metrics_history),
            "recent_samples": len(recent),
            "average_cpu": avg_cpu,
            "average_memory": avg_memory,
            "current_status": recent[-1].status if recent else "unknown",
            "latest_timestamp": recent[-1].timestamp if recent else None,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert current metrics to dict."""
        metrics = self.get_system_metrics()
        return {
            "cpu_percent": metrics.cpu_percent,
            "memory_percent": metrics.memory_percent,
            "memory_used_gb": metrics.memory_used_gb,
            "memory_available_gb": metrics.memory_available_gb,
            "disk_percent": metrics.disk_percent,
            "disk_used_gb": metrics.disk_used_gb,
            "disk_available_gb": metrics.disk_available_gb,
            "status": metrics.status,
            "timestamp": metrics.timestamp,
        }


class HealthCheck:
    """
    Performs health checks on system and services.
    """

    def __init__(self):
        self.monitor = SystemMonitor()
        self.checks = {}

    def add_check(self, name: str, check_func) -> None:
        """Add a health check function."""
        self.checks[name] = check_func

    def run_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run all health checks."""
        results = {}

        # System metrics
        system_metrics = self.monitor.get_system_metrics()
        results["system"] = {
            "status": system_metrics.status,
            "cpu_percent": system_metrics.cpu_percent,
            "memory_percent": system_metrics.memory_percent,
        }

        # Custom checks
        for name, check_func in self.checks.items():
            try:
                result = check_func()
                results[name] = {
                    "status": result.get("status", "unknown"),
                    "details": result.get("details", ""),
                }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "details": str(e),
                }

        return results

    def get_health_status(self) -> str:
        """Get overall health status."""
        results = self.run_checks()
        statuses = [r.get("status", "unknown") for r in results.values()]

        if "critical" in statuses:
            return "critical"
        elif "error" in statuses:
            return "error"
        elif "warning" in statuses:
            return "warning"
        else:
            return "healthy"


def get_system_monitor() -> SystemMonitor:
    """Get a system monitor instance."""
    return SystemMonitor()


def get_health_check() -> HealthCheck:
    """Get a health check instance."""
    return HealthCheck()
