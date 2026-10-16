"""
SweetyAI - Advanced Logging & Monitoring System
Structured logging, metrics collection, performance tracking, error monitoring
"""

import os
import sys
import time
import json
import logging
import traceback
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from pathlib import Path
from functools import wraps
from collections import defaultdict
import threading

# Structured logging
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    print("[Logging] structlog not available. Run: pip install structlog")

# Prometheus metrics
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("[Logging] prometheus_client not available. Run: pip install prometheus-client")


# =============================================================================
# STRUCTURED LOGGER CONFIGURATION
# =============================================================================

class StructuredLogger:
    """Structured logger with context and JSON output."""

    def __init__(self, name: str = "sweetyai", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Configure structlog if available
        if STRUCTLOG_AVAILABLE:
            self._configure_structlog()
            self.logger = structlog.get_logger(name)
        else:
            # Fallback to standard logging
            self.logger = self._configure_standard_logging()

    def _configure_structlog(self):
        """Configure structlog with processors."""
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True
        )

    def _configure_standard_logging(self):
        """Fallback to standard logging with JSON formatter."""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # File handler
        log_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # JSON formatter
        formatter = logging.Formatter(
            '{"timestamp":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    def info(self, message: str, **kwargs):
        """Log info message with context."""
        if STRUCTLOG_AVAILABLE:
            self.logger.info(message, **kwargs)
        else:
            self.logger.info(f"{message} | {json.dumps(kwargs)}")

    def error(self, message: str, **kwargs):
        """Log error message with context."""
        if STRUCTLOG_AVAILABLE:
            self.logger.error(message, **kwargs)
        else:
            self.logger.error(f"{message} | {json.dumps(kwargs)}")

    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        if STRUCTLOG_AVAILABLE:
            self.logger.warning(message, **kwargs)
        else:
            self.logger.warning(f"{message} | {json.dumps(kwargs)}")

    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        if STRUCTLOG_AVAILABLE:
            self.logger.debug(message, **kwargs)
        else:
            self.logger.debug(f"{message} | {json.dumps(kwargs)}")

    def exception(self, message: str, exc: Exception, **kwargs):
        """Log exception with full traceback."""
        error_details = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc(),
            **kwargs
        }
        self.error(message, **error_details)


# =============================================================================
# PROMETHEUS METRICS COLLECTION
# =============================================================================

class MetricsCollector:
    """Prometheus metrics collector for monitoring."""

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        if not PROMETHEUS_AVAILABLE:
            print("[Metrics] Prometheus not available")
            self.enabled = False
            return

        self.enabled = True
        self.registry = registry or CollectorRegistry()

        # Request metrics
        self.request_counter = Counter(
            'sweetyai_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )

        self.request_duration = Histogram(
            'sweetyai_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )

        # Tool usage metrics
        self.tool_calls = Counter(
            'sweetyai_tool_calls_total',
            'Total tool calls',
            ['tool_name', 'status'],
            registry=self.registry
        )

        self.tool_duration = Histogram(
            'sweetyai_tool_duration_seconds',
            'Tool execution duration',
            ['tool_name'],
            registry=self.registry
        )

        # Agent metrics
        self.agent_tasks = Counter(
            'sweetyai_agent_tasks_total',
            'Total agent tasks',
            ['agent_type', 'status'],
            registry=self.registry
        )

        self.agent_duration = Histogram(
            'sweetyai_agent_duration_seconds',
            'Agent task duration',
            ['agent_type'],
            registry=self.registry
        )

        # System metrics
        self.active_sessions = Gauge(
            'sweetyai_active_sessions',
            'Number of active user sessions',
            registry=self.registry
        )

        self.memory_usage = Gauge(
            'sweetyai_memory_usage_bytes',
            'Memory usage in bytes',
            registry=self.registry
        )

        # Error metrics
        self.errors_total = Counter(
            'sweetyai_errors_total',
            'Total errors',
            ['error_type', 'component'],
            registry=self.registry
        )

    def record_request(self, method: str, endpoint: str, status: str, duration: float):
        """Record API request metrics."""
        if not self.enabled:
            return

        self.request_counter.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_tool_call(self, tool_name: str, status: str, duration: float):
        """Record tool execution metrics."""
        if not self.enabled:
            return

        self.tool_calls.labels(tool_name=tool_name, status=status).inc()
        self.tool_duration.labels(tool_name=tool_name).observe(duration)

    def record_agent_task(self, agent_type: str, status: str, duration: float):
        """Record agent task metrics."""
        if not self.enabled:
            return

        self.agent_tasks.labels(agent_type=agent_type, status=status).inc()
        self.agent_duration.labels(agent_type=agent_type).observe(duration)

    def record_error(self, error_type: str, component: str):
        """Record error occurrence."""
        if not self.enabled:
            return

        self.errors_total.labels(error_type=error_type, component=component).inc()

    def set_active_sessions(self, count: int):
        """Set active sessions count."""
        if not self.enabled:
            return

        self.active_sessions.set(count)

    def set_memory_usage(self, bytes_used: int):
        """Set memory usage."""
        if not self.enabled:
            return

        self.memory_usage.set(bytes_used)

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        if not self.enabled:
            return "Metrics disabled"

        return generate_latest(self.registry).decode('utf-8')


# =============================================================================
# PERFORMANCE TRACKER
# =============================================================================

class PerformanceTracker:
    """Track performance metrics for operations."""

    def __init__(self):
        self.timings = defaultdict(list)
        self.lock = threading.Lock()

    def start_timing(self, operation: str) -> float:
        """Start timing an operation."""
        return time.time()

    def end_timing(self, operation: str, start_time: float) -> float:
        """End timing and record duration."""
        duration = time.time() - start_time

        with self.lock:
            self.timings[operation].append({
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })

        return duration

    def get_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for an operation."""
        with self.lock:
            timings = self.timings.get(operation, [])

        if not timings:
            return {"operation": operation, "count": 0}

        durations = [t['duration'] for t in timings]

        return {
            "operation": operation,
            "count": len(durations),
            "total_time": sum(durations),
            "avg_time": sum(durations) / len(durations),
            "min_time": min(durations),
            "max_time": max(durations),
            "last_execution": timings[-1]['timestamp']
        }

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all operations."""
        with self.lock:
            operations = list(self.timings.keys())

        return {op: self.get_stats(op) for op in operations}

    def clear_stats(self, operation: Optional[str] = None):
        """Clear statistics."""
        with self.lock:
            if operation:
                self.timings.pop(operation, None)
            else:
                self.timings.clear()


# =============================================================================
# ERROR MONITOR
# =============================================================================

class ErrorMonitor:
    """Monitor and track errors with categorization."""

    def __init__(self, log_dir: str = "logs/errors"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.error_counts = defaultdict(int)
        self.recent_errors = []
        self.max_recent = 100
        self.lock = threading.Lock()

    def record_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        severity: str = "error"
    ):
        """Record an error with context."""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
            "context": context,
            "severity": severity
        }

        with self.lock:
            # Update counts
            error_type = error_data["type"]
            self.error_counts[error_type] += 1

            # Add to recent errors
            self.recent_errors.append(error_data)
            if len(self.recent_errors) > self.max_recent:
                self.recent_errors.pop(0)

        # Log to file
        self._log_error_to_file(error_data)

    def _log_error_to_file(self, error_data: Dict[str, Any]):
        """Write error to log file."""
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = self.log_dir / f"errors_{date_str}.jsonl"

        with open(log_file, 'a') as f:
            f.write(json.dumps(error_data) + '\n')

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors."""
        with self.lock:
            return {
                "total_errors": sum(self.error_counts.values()),
                "error_types": dict(self.error_counts),
                "recent_errors": self.recent_errors[-10:]  # Last 10
            }

    def get_errors_by_type(self, error_type: str) -> List[Dict[str, Any]]:
        """Get all errors of specific type."""
        with self.lock:
            return [
                err for err in self.recent_errors
                if err["type"] == error_type
            ]

    def clear_errors(self):
        """Clear error history."""
        with self.lock:
            self.error_counts.clear()
            self.recent_errors.clear()


# =============================================================================
# DECORATORS FOR AUTOMATIC MONITORING
# =============================================================================

def monitor_performance(operation_name: Optional[str] = None):
    """Decorator to automatically monitor function performance."""
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Log performance
                logger.info(
                    f"Performance: {op_name}",
                    duration=duration,
                    status="success"
                )

                # Record metrics
                if metrics_collector.enabled:
                    metrics_collector.tool_duration.labels(
                        tool_name=op_name
                    ).observe(duration)

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Log error
                logger.exception(
                    f"Error in {op_name}",
                    e,
                    duration=duration
                )

                # Record error metrics
                if metrics_collector.enabled:
                    metrics_collector.record_error(
                        error_type=type(e).__name__,
                        component=op_name
                    )

                raise

        return wrapper
    return decorator


def track_tool_execution(tool_name: str):
    """Decorator to track tool execution metrics."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Record successful execution
                metrics_collector.record_tool_call(
                    tool_name=tool_name,
                    status="success",
                    duration=duration
                )

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Record failed execution
                metrics_collector.record_tool_call(
                    tool_name=tool_name,
                    status="error",
                    duration=duration
                )

                error_monitor.record_error(e, {"tool": tool_name})
                raise

        return wrapper
    return decorator


# =============================================================================
# MONITORING DASHBOARD DATA
# =============================================================================

class MonitoringDashboard:
    """Aggregate monitoring data for dashboard display."""

    def __init__(
        self,
        logger: StructuredLogger,
        metrics: MetricsCollector,
        performance: PerformanceTracker,
        errors: ErrorMonitor
    ):
        self.logger = logger
        self.metrics = metrics
        self.performance = performance
        self.errors = errors

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get all monitoring data for dashboard."""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics.get_metrics() if self.metrics.enabled else {},
            "performance": self.performance.get_all_stats(),
            "errors": self.errors.get_error_summary(),
            "health": self._get_health_status()
        }

    def _get_health_status(self) -> Dict[str, Any]:
        """Calculate system health status."""
        error_summary = self.errors.get_error_summary()
        total_errors = error_summary.get("total_errors", 0)

        if total_errors == 0:
            status = "healthy"
        elif total_errors < 10:
            status = "degraded"
        else:
            status = "unhealthy"

        return {
            "status": status,
            "total_errors": total_errors,
            "timestamp": datetime.now().isoformat()
        }

    def export_report(self, output_path: str):
        """Export monitoring report to file."""
        data = self.get_dashboard_data()

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        return f"Report exported to {output_path}"


# =============================================================================
# GLOBAL INSTANCES
# =============================================================================

# Initialize global monitoring components
logger = StructuredLogger()
metrics_collector = MetricsCollector()
performance_tracker = PerformanceTracker()
error_monitor = ErrorMonitor()
dashboard = MonitoringDashboard(logger, metrics_collector, performance_tracker, error_monitor)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def log_info(message: str, **kwargs):
    """Quick info logging."""
    logger.info(message, **kwargs)


def log_error(message: str, **kwargs):
    """Quick error logging."""
    logger.error(message, **kwargs)


def log_exception(message: str, exc: Exception, **kwargs):
    """Quick exception logging."""
    logger.exception(message, exc, **kwargs)
    error_monitor.record_error(exc, kwargs)


def get_metrics() -> str:
    """Get Prometheus metrics."""
    return metrics_collector.get_metrics()


def get_performance_stats(operation: Optional[str] = None) -> Dict[str, Any]:
    """Get performance statistics."""
    if operation:
        return performance_tracker.get_stats(operation)
    return performance_tracker.get_all_stats()


def get_error_summary() -> Dict[str, Any]:
    """Get error summary."""
    return error_monitor.get_error_summary()


def get_dashboard_data() -> Dict[str, Any]:
    """Get full dashboard data."""
    return dashboard.get_dashboard_data()


def export_monitoring_report(output_path: str = "monitoring_report.json") -> str:
    """Export monitoring report."""
    return dashboard.export_report(output_path)


__all__ = [
    'StructuredLogger',
    'MetricsCollector',
    'PerformanceTracker',
    'ErrorMonitor',
    'MonitoringDashboard',
    'monitor_performance',
    'track_tool_execution',
    'logger',
    'metrics_collector',
    'performance_tracker',
    'error_monitor',
    'dashboard',
    'log_info',
    'log_error',
    'log_exception',
    'get_metrics',
    'get_performance_stats',
    'get_error_summary',
    'get_dashboard_data',
    'export_monitoring_report'
]
