"""Operational metrics collection and reporting."""

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from threading import Lock
from typing import Any


class MetricType(Enum):
    """Supported metric types."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class MetricValue:
    """A single metric measurement."""

    value: float | int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class Metric:
    """A named metric with history of values."""

    name: str
    type: MetricType
    description: str
    values: list[MetricValue] = field(default_factory=list)
    lock: Lock = field(default_factory=Lock, init=False, repr=False, compare=False)

    def add(self, value: float | int, labels: dict[str, str] | None = None) -> None:
        """Add a measurement to this metric."""
        with self.lock:
            self.values.append(
                MetricValue(
                    value=value,
                    labels=labels or {},
                )
            )

    def reset(self) -> None:
        """Clear all measurements."""
        with self.lock:
            self.values.clear()

    def summarize(self, window_seconds: float = 60.0) -> dict[str, Any]:
        """Return a summary of recent measurements."""
        with self.lock:
            now = datetime.now(timezone.utc)
            cutoff = now.timestamp() - window_seconds
            recent = [v for v in self.values if v.timestamp.timestamp() >= cutoff]

            if not recent:
                return {"count": 0, "values": []}

            values = [v.value for v in recent]
            return {
                "count": len(recent),
                "min": min(values),
                "max": max(values),
                "sum": sum(values),
                "avg": sum(values) / len(values),
                "latest": values[-1],
            }


class MetricsRegistry:
    """Registry for collecting and reporting operational metrics."""

    def __init__(self) -> None:
        self._metrics: dict[str, Metric] = {}
        self._lock = Lock()

    def get_or_create(
        self,
        name: str,
        type: MetricType,
        description: str = "",
    ) -> Metric:
        """Get an existing metric or create a new one."""
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = Metric(name=name, type=type, description=description)
            return self._metrics[name]

    def counter(self, name: str, description: str = "") -> Metric:
        """Get or create a counter metric."""
        return self.get_or_create(name, MetricType.COUNTER, description)

    def gauge(self, name: str, description: str = "") -> Metric:
        """Get or create a gauge metric."""
        return self.get_or_create(name, MetricType.GAUGE, description)

    def histogram(self, name: str, description: str = "") -> Metric:
        """Get or create a histogram metric."""
        return self.get_or_create(name, MetricType.HISTOGRAM, description)

    def timer(self, name: str, description: str = "") -> Metric:
        """Get or create a timer metric."""
        return self.get_or_create(name, MetricType.TIMER, description)

    def time(self, name: str, labels: dict[str, str] | None = None) -> Callable[[], None]:
        """Return a context manager for timing an operation."""
        metric = self.timer(name)
        start = time.perf_counter()

        def finish() -> None:
            duration = (time.perf_counter() - start) * 1000
            metric.add(duration, labels)

        return finish

    def get_all_summaries(self, window_seconds: float = 60.0) -> dict[str, dict[str, Any]]:
        """Get summaries of all metrics."""
        with self._lock:
            return {
                name: metric.summarize(window_seconds)
                for name, metric in self._metrics.items()
            }

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            for metric in self._metrics.values():
                metric.reset()


# Global metrics registry instance
_metrics_registry: MetricsRegistry | None = None


def get_metrics_registry() -> MetricsRegistry:
    """Get the global metrics registry."""
    global _metrics_registry
    if _metrics_registry is None:
        _metrics_registry = MetricsRegistry()
    return _metrics_registry
