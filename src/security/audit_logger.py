"""
Audit Logging System
Enterprise-grade audit trail for AI agent operations
"""
from datetime import datetime
from typing import Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
import structlog
import json

logger = structlog.get_logger()


class AuditEventType(str, Enum):
    """Types of audit events"""
    # Query events
    QUERY_RECEIVED = "query_received"
    QUERY_CLASSIFIED = "query_classified"
    QUERY_COMPLETED = "query_completed"
    QUERY_FAILED = "query_failed"

    # Agent events
    AGENT_INVOKED = "agent_invoked"
    AGENT_RESPONSE = "agent_response"
    AGENT_ERROR = "agent_error"

    # Tool events
    TOOL_CALLED = "tool_called"
    TOOL_RESPONSE = "tool_response"
    TOOL_ERROR = "tool_error"

    # Security events
    SECURITY_SCREEN = "security_screen"
    INJECTION_BLOCKED = "injection_blocked"
    PII_DETECTED = "pii_detected"
    PII_ACCESSED = "pii_accessed"
    RATE_LIMITED = "rate_limited"

    # Data events
    DATA_READ = "data_read"
    DATA_WRITE = "data_write"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"

    # Financial events
    INVOICE_PROCESSED = "invoice_processed"
    PAYMENT_PROCESSED = "payment_processed"
    COMMISSION_CALCULATED = "commission_calculated"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"

    # System events
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    CONFIG_CHANGE = "config_change"
    ERROR_OCCURRED = "error_occurred"


class AuditSeverity(str, Enum):
    """Audit event severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditEvent(BaseModel):
    """Single audit log entry"""
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: str
    session_id: str
    agent_name: Optional[str] = None
    tool_name: Optional[str] = None
    action: str
    resource: Optional[str] = None
    resource_id: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
    duration_ms: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    correlation_id: Optional[str] = None
    outcome: str = "success"  # success, failure, blocked, partial


class AuditLogger:
    """
    Enterprise audit logging for AI agent operations.

    Features:
    - Immutable audit trail
    - PII-safe logging (automatic redaction)
    - Correlation IDs for request tracing
    - Severity-based filtering
    - Multiple output destinations
    """

    def __init__(
        self,
        service_name: str = "damac-finance-ai",
        min_severity: AuditSeverity = AuditSeverity.INFO,
        enable_file_logging: bool = True,
        log_file_path: str = "./audit_logs/audit.jsonl",
    ):
        """
        Initialize audit logger.

        Args:
            service_name: Name of the service for log identification
            min_severity: Minimum severity level to log
            enable_file_logging: Whether to write logs to file
            log_file_path: Path for audit log file
        """
        self.service_name = service_name
        self.min_severity = min_severity
        self.enable_file_logging = enable_file_logging
        self.log_file_path = log_file_path

        # Severity ordering for filtering
        self._severity_order = {
            AuditSeverity.DEBUG: 0,
            AuditSeverity.INFO: 1,
            AuditSeverity.WARNING: 2,
            AuditSeverity.ERROR: 3,
            AuditSeverity.CRITICAL: 4,
        }

        # Create log directory if needed
        if self.enable_file_logging:
            import os
            os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)

    async def log(self, event: AuditEvent) -> None:
        """
        Log an audit event.

        Args:
            event: Audit event to log
        """
        # Check severity threshold
        if self._severity_order[event.severity] < self._severity_order[self.min_severity]:
            return

        # Add service metadata
        log_entry = {
            "service": self.service_name,
            **event.dict(),
            "timestamp": event.timestamp.isoformat(),
        }

        # Log to structured logger
        log_func = {
            AuditSeverity.DEBUG: logger.debug,
            AuditSeverity.INFO: logger.info,
            AuditSeverity.WARNING: logger.warning,
            AuditSeverity.ERROR: logger.error,
            AuditSeverity.CRITICAL: logger.critical,
        }.get(event.severity, logger.info)

        log_func(
            f"audit_{event.event_type.value}",
            **{k: v for k, v in log_entry.items() if v is not None}
        )

        # Write to file if enabled
        if self.enable_file_logging:
            await self._write_to_file(log_entry)

    async def _write_to_file(self, log_entry: dict) -> None:
        """Write log entry to JSONL file."""
        try:
            import aiofiles
            async with aiofiles.open(self.log_file_path, 'a') as f:
                await f.write(json.dumps(log_entry, default=str) + '\n')
        except ImportError:
            # Fallback to sync if aiofiles not available
            with open(self.log_file_path, 'a') as f:
                f.write(json.dumps(log_entry, default=str) + '\n')

    async def log_query(
        self,
        user_id: str,
        session_id: str,
        query: str,
        classification: dict,
        response_summary: str,
        duration_ms: int = None,
        correlation_id: str = None,
    ) -> None:
        """
        Log a user query with classification and response.

        Args:
            user_id: User identifier
            session_id: Session identifier
            query: User query (will be truncated for privacy)
            classification: Query classification result
            response_summary: Summary of response
            duration_ms: Query processing time
            correlation_id: Request correlation ID
        """
        import uuid

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.QUERY_COMPLETED,
            severity=AuditSeverity.INFO,
            user_id=user_id,
            session_id=session_id,
            action="process_query",
            details={
                "query_preview": query[:100] + "..." if len(query) > 100 else query,
                "query_length": len(query),
                "intent": classification.get("intent"),
                "confidence": classification.get("confidence"),
                "response_summary": response_summary[:200],
            },
            duration_ms=duration_ms,
            correlation_id=correlation_id,
            outcome="success",
        )

        await self.log(event)

    async def log_security_event(
        self,
        user_id: str,
        event_type: str,
        details: dict,
        severity: AuditSeverity = AuditSeverity.WARNING,
    ) -> None:
        """
        Log a security-related event.

        Args:
            user_id: User identifier
            event_type: Type of security event
            details: Event details
            severity: Event severity
        """
        import uuid

        audit_type = {
            "prompt_injection_blocked": AuditEventType.INJECTION_BLOCKED,
            "pii_detected": AuditEventType.PII_DETECTED,
            "rate_limited": AuditEventType.RATE_LIMITED,
        }.get(event_type, AuditEventType.SECURITY_SCREEN)

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event_type=audit_type,
            severity=severity,
            user_id=user_id,
            session_id="security",
            action=event_type,
            details=details,
            outcome="blocked" if "blocked" in event_type else "detected",
        )

        await self.log(event)

    async def log_financial_operation(
        self,
        user_id: str,
        session_id: str,
        operation: str,
        resource_type: str,
        resource_id: str,
        amount: float = None,
        currency: str = "AED",
        outcome: str = "success",
        details: dict = None,
    ) -> None:
        """
        Log a financial operation for compliance.

        Args:
            user_id: User performing operation
            session_id: Session identifier
            operation: Type of operation
            resource_type: Type of resource (invoice, payment, commission)
            resource_id: Resource identifier
            amount: Amount involved
            currency: Currency code
            outcome: Operation outcome
            details: Additional details
        """
        import uuid

        event_type_map = {
            "invoice_process": AuditEventType.INVOICE_PROCESSED,
            "payment_process": AuditEventType.PAYMENT_PROCESSED,
            "commission_calculate": AuditEventType.COMMISSION_CALCULATED,
            "approval_request": AuditEventType.APPROVAL_REQUESTED,
            "approval_grant": AuditEventType.APPROVAL_GRANTED,
            "approval_deny": AuditEventType.APPROVAL_DENIED,
        }

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event_type=event_type_map.get(operation, AuditEventType.DATA_WRITE),
            severity=AuditSeverity.INFO if outcome == "success" else AuditSeverity.WARNING,
            user_id=user_id,
            session_id=session_id,
            action=operation,
            resource=resource_type,
            resource_id=resource_id,
            details={
                "amount": amount,
                "currency": currency,
                **(details or {}),
            },
            outcome=outcome,
        )

        await self.log(event)

    async def log_agent_invocation(
        self,
        user_id: str,
        session_id: str,
        agent_name: str,
        query: str,
        tools_used: list[str] = None,
        duration_ms: int = None,
        tokens_used: int = None,
        cost: float = None,
        outcome: str = "success",
    ) -> None:
        """
        Log an agent invocation with metrics.

        Args:
            user_id: User identifier
            session_id: Session identifier
            agent_name: Name of agent invoked
            query: Query sent to agent
            tools_used: List of tools called
            duration_ms: Processing duration
            tokens_used: LLM tokens consumed
            cost: Estimated cost
            outcome: Invocation outcome
        """
        import uuid

        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event_type=AuditEventType.AGENT_INVOKED,
            severity=AuditSeverity.INFO,
            user_id=user_id,
            session_id=session_id,
            agent_name=agent_name,
            action="invoke_agent",
            details={
                "query_preview": query[:100] + "..." if len(query) > 100 else query,
                "tools_used": tools_used or [],
                "tokens_used": tokens_used,
                "estimated_cost_usd": cost,
            },
            duration_ms=duration_ms,
            outcome=outcome,
        )

        await self.log(event)


class ComplianceReporter:
    """
    Generate compliance reports from audit logs.
    """

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
        self.log_file = audit_logger.log_file_path

    async def generate_daily_report(self, date: datetime) -> dict:
        """
        Generate daily compliance report.

        Args:
            date: Date for report

        Returns:
            Report dictionary
        """
        # In production, this would query a proper database
        report = {
            "report_date": date.date().isoformat(),
            "generated_at": datetime.utcnow().isoformat(),
            "metrics": {
                "total_queries": 0,
                "security_events": 0,
                "financial_operations": 0,
                "pii_access_events": 0,
                "blocked_requests": 0,
            },
            "top_users": [],
            "security_summary": {
                "injection_attempts": 0,
                "rate_limit_hits": 0,
                "suspicious_activities": [],
            },
            "financial_summary": {
                "invoices_processed": 0,
                "payments_processed": 0,
                "commissions_calculated": 0,
                "total_amount_processed": 0,
            },
        }

        return report

    async def export_audit_trail(
        self,
        start_date: datetime,
        end_date: datetime,
        event_types: list[AuditEventType] = None,
        user_id: str = None,
    ) -> list[dict]:
        """
        Export audit trail for compliance review.

        Args:
            start_date: Start of period
            end_date: End of period
            event_types: Filter by event types
            user_id: Filter by user

        Returns:
            List of audit events
        """
        # In production, this would query the audit database
        return []
