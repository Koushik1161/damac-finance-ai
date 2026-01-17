"""
Metrics Collection for DAMAC Finance AI
Tracks performance, costs, and business KPIs
"""
import time
from typing import Any, Optional
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
import structlog

logger = structlog.get_logger()


@dataclass
class QueryMetrics:
    """Metrics for a single query"""
    query_id: str
    start_time: float
    end_time: Optional[float] = None
    intent: Optional[str] = None
    agent: Optional[str] = None
    tools_called: list[str] = field(default_factory=list)
    tokens_prompt: int = 0
    tokens_completion: int = 0
    cost_usd: float = 0.0
    success: bool = True
    error: Optional[str] = None


class MetricsCollector:
    """
    Collects and tracks metrics for AI agent operations.

    Features:
    - Query latency tracking
    - Token usage and cost estimation
    - Business KPI tracking
    - Langfuse integration (production)
    """

    # Cost per 1K tokens (GPT-4o pricing as of 2024)
    COST_PER_1K_PROMPT = 0.005
    COST_PER_1K_COMPLETION = 0.015

    def __init__(
        self,
        langfuse_enabled: bool = False,
        azure_monitor_enabled: bool = False,
    ):
        self.langfuse_enabled = langfuse_enabled
        self.azure_monitor_enabled = azure_monitor_enabled
        self._current_metrics: dict[str, QueryMetrics] = {}
        self._aggregated: dict[str, Any] = {
            "total_queries": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "total_latency_ms": 0,
            "by_agent": {},
            "by_intent": {},
        }

    @contextmanager
    def measure_latency(self, operation: str):
        """
        Context manager to measure operation latency.

        Usage:
            with metrics.measure_latency("classification"):
                result = await classifier.run(query)
        """
        start = time.time()
        try:
            yield
        finally:
            duration_ms = int((time.time() - start) * 1000)
            logger.debug(
                "operation_latency",
                operation=operation,
                duration_ms=duration_ms,
            )

    def start_query(self, query_id: str) -> QueryMetrics:
        """Start tracking a new query."""
        metrics = QueryMetrics(
            query_id=query_id,
            start_time=time.time(),
        )
        self._current_metrics[query_id] = metrics
        return metrics

    def end_query(
        self,
        query_id: str,
        intent: str = None,
        agent: str = None,
        tokens_prompt: int = 0,
        tokens_completion: int = 0,
        success: bool = True,
        error: str = None,
    ) -> QueryMetrics:
        """End tracking for a query and calculate final metrics."""
        metrics = self._current_metrics.get(query_id)
        if not metrics:
            return None

        metrics.end_time = time.time()
        metrics.intent = intent
        metrics.agent = agent
        metrics.tokens_prompt = tokens_prompt
        metrics.tokens_completion = tokens_completion
        metrics.success = success
        metrics.error = error

        # Calculate cost
        metrics.cost_usd = (
            (tokens_prompt / 1000) * self.COST_PER_1K_PROMPT +
            (tokens_completion / 1000) * self.COST_PER_1K_COMPLETION
        )

        # Update aggregates
        self._update_aggregates(metrics)

        # Log metrics
        latency_ms = int((metrics.end_time - metrics.start_time) * 1000)
        logger.info(
            "query_metrics",
            query_id=query_id,
            intent=intent,
            agent=agent,
            latency_ms=latency_ms,
            tokens_total=tokens_prompt + tokens_completion,
            cost_usd=round(metrics.cost_usd, 4),
            success=success,
        )

        # Clean up
        del self._current_metrics[query_id]

        return metrics

    def _update_aggregates(self, metrics: QueryMetrics) -> None:
        """Update aggregated metrics."""
        self._aggregated["total_queries"] += 1
        self._aggregated["total_tokens"] += metrics.tokens_prompt + metrics.tokens_completion
        self._aggregated["total_cost_usd"] += metrics.cost_usd

        if metrics.end_time and metrics.start_time:
            latency_ms = int((metrics.end_time - metrics.start_time) * 1000)
            self._aggregated["total_latency_ms"] += latency_ms

        # By agent
        if metrics.agent:
            if metrics.agent not in self._aggregated["by_agent"]:
                self._aggregated["by_agent"][metrics.agent] = {
                    "count": 0,
                    "tokens": 0,
                    "cost_usd": 0.0,
                }
            self._aggregated["by_agent"][metrics.agent]["count"] += 1
            self._aggregated["by_agent"][metrics.agent]["tokens"] += (
                metrics.tokens_prompt + metrics.tokens_completion
            )
            self._aggregated["by_agent"][metrics.agent]["cost_usd"] += metrics.cost_usd

        # By intent
        if metrics.intent:
            if metrics.intent not in self._aggregated["by_intent"]:
                self._aggregated["by_intent"][metrics.intent] = 0
            self._aggregated["by_intent"][metrics.intent] += 1

    def record_tool_call(self, query_id: str, tool_name: str) -> None:
        """Record a tool invocation."""
        metrics = self._current_metrics.get(query_id)
        if metrics:
            metrics.tools_called.append(tool_name)

    def get_summary(self) -> dict:
        """Get aggregated metrics summary."""
        total_queries = max(self._aggregated["total_queries"], 1)

        return {
            "period": "session",
            "timestamp": datetime.utcnow().isoformat(),
            "queries": {
                "total": self._aggregated["total_queries"],
                "avg_latency_ms": self._aggregated["total_latency_ms"] // total_queries,
            },
            "tokens": {
                "total": self._aggregated["total_tokens"],
                "avg_per_query": self._aggregated["total_tokens"] // total_queries,
            },
            "cost": {
                "total_usd": round(self._aggregated["total_cost_usd"], 4),
                "avg_per_query_usd": round(self._aggregated["total_cost_usd"] / total_queries, 4),
            },
            "by_agent": self._aggregated["by_agent"],
            "by_intent": self._aggregated["by_intent"],
        }

    def reset(self) -> None:
        """Reset all metrics."""
        self._current_metrics.clear()
        self._aggregated = {
            "total_queries": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "total_latency_ms": 0,
            "by_agent": {},
            "by_intent": {},
        }


class BusinessKPITracker:
    """
    Tracks business-level KPIs for the AI system.
    """

    def __init__(self):
        self._kpis = {
            "invoices_processed": 0,
            "invoices_auto_approved": 0,
            "payments_tracked": 0,
            "commissions_calculated": 0,
            "total_invoice_value_aed": 0.0,
            "total_commission_value_aed": 0.0,
            "avg_processing_time_seconds": 0.0,
            "error_rate_percent": 0.0,
        }
        self._processing_times: list[float] = []
        self._error_count = 0
        self._total_operations = 0

    def record_invoice_processed(
        self,
        amount_aed: float,
        auto_approved: bool = False,
        processing_time_seconds: float = None,
    ) -> None:
        """Record an invoice processing."""
        self._kpis["invoices_processed"] += 1
        self._kpis["total_invoice_value_aed"] += amount_aed
        if auto_approved:
            self._kpis["invoices_auto_approved"] += 1

        self._total_operations += 1
        if processing_time_seconds:
            self._processing_times.append(processing_time_seconds)
            self._update_avg_processing_time()

    def record_commission_calculated(
        self,
        amount_aed: float,
        processing_time_seconds: float = None,
    ) -> None:
        """Record a commission calculation."""
        self._kpis["commissions_calculated"] += 1
        self._kpis["total_commission_value_aed"] += amount_aed

        self._total_operations += 1
        if processing_time_seconds:
            self._processing_times.append(processing_time_seconds)
            self._update_avg_processing_time()

    def record_error(self) -> None:
        """Record an error."""
        self._error_count += 1
        self._total_operations += 1
        self._update_error_rate()

    def _update_avg_processing_time(self) -> None:
        """Update average processing time."""
        if self._processing_times:
            self._kpis["avg_processing_time_seconds"] = (
                sum(self._processing_times) / len(self._processing_times)
            )

    def _update_error_rate(self) -> None:
        """Update error rate."""
        if self._total_operations > 0:
            self._kpis["error_rate_percent"] = (
                self._error_count / self._total_operations * 100
            )

    def get_kpis(self) -> dict:
        """Get current KPIs."""
        return {
            **self._kpis,
            "timestamp": datetime.utcnow().isoformat(),
        }
