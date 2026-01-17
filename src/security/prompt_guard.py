"""
Prompt Injection Defense System
Enterprise-grade security for AI agent inputs
"""
import re
from typing import Optional
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger()


class SecurityScreenResult(BaseModel):
    """Result of security screening"""
    is_safe: bool
    risk_score: float = Field(ge=0.0, le=1.0)
    detected_patterns: list[str] = Field(default_factory=list)
    sanitized_input: Optional[str] = None
    blocked_reason: Optional[str] = None


class PromptGuard:
    """
    Prompt injection defense system.

    Detects and blocks:
    - Direct prompt injections
    - Instruction override attempts
    - Role manipulation attacks
    - Data exfiltration attempts
    - Jailbreak patterns
    """

    # Suspicious patterns that may indicate injection attempts
    INJECTION_PATTERNS = [
        # Direct instruction overrides
        (r"ignore\s+(previous|all|above|prior)\s+instructions?", "instruction_override", 0.9),
        (r"disregard\s+(previous|all|above|prior)\s+instructions?", "instruction_override", 0.9),
        (r"forget\s+(everything|all|what)\s+.*(told|said|instructed)", "instruction_override", 0.9),

        # Role manipulation
        (r"you\s+are\s+now\s+(a|an|the)", "role_manipulation", 0.8),
        (r"pretend\s+(to\s+be|you\s+are)", "role_manipulation", 0.8),
        (r"act\s+as\s+(a|an|if)", "role_manipulation", 0.7),
        (r"your\s+new\s+(role|persona|identity)", "role_manipulation", 0.9),

        # System prompt extraction
        (r"(show|reveal|display|print|output)\s+(your|the)\s+(system|initial)\s+prompt", "prompt_extraction", 0.95),
        (r"what\s+(is|are)\s+your\s+(instructions|rules|guidelines)", "prompt_extraction", 0.7),
        (r"repeat\s+(your|the)\s+(system|initial)\s+(prompt|instructions)", "prompt_extraction", 0.95),

        # Data exfiltration
        (r"send\s+(this|data|information)\s+to\s+(http|https|email|webhook)", "data_exfiltration", 0.95),
        (r"(encode|encrypt|base64)\s+.*(send|transmit|post)", "data_exfiltration", 0.9),
        (r"curl\s+|wget\s+|fetch\s*\(", "data_exfiltration", 0.9),

        # Code execution attempts
        (r"(execute|run|eval)\s*(this|the|following)?\s*(code|script|command)", "code_execution", 0.9),
        (r"import\s+os|subprocess|shutil", "code_execution", 0.95),
        (r"__import__|exec\(|eval\(", "code_execution", 0.95),

        # Jailbreak attempts
        (r"DAN\s*mode|developer\s*mode|god\s*mode", "jailbreak", 0.95),
        (r"do\s+anything\s+now", "jailbreak", 0.9),
        (r"bypass\s+(safety|security|filters|restrictions)", "jailbreak", 0.95),

        # SQL injection (for agents with DB access)
        (r";\s*(drop|delete|truncate|alter|update)\s+", "sql_injection", 0.95),
        (r"'\s*(or|and)\s*'?\s*[0-9]*\s*=\s*", "sql_injection", 0.9),
        (r"union\s+(all\s+)?select", "sql_injection", 0.9),

        # Delimiter manipulation
        (r"<\|?/?system\|?>", "delimiter_injection", 0.95),
        (r"\[INST\]|\[/INST\]", "delimiter_injection", 0.9),
        (r"```system|```instruction", "delimiter_injection", 0.85),
    ]

    # Keywords that raise suspicion in financial context
    SUSPICIOUS_FINANCIAL_KEYWORDS = [
        (r"transfer\s+all\s+(funds|money|balance)", "unauthorized_transfer", 0.95),
        (r"change\s+(bank\s+)?account\s+(to|number)", "account_tampering", 0.9),
        (r"override\s+approval\s+(workflow|process)", "workflow_bypass", 0.9),
        (r"skip\s+(verification|validation|approval)", "validation_bypass", 0.85),
        (r"emergency\s+(override|approval|access)", "emergency_bypass", 0.8),
    ]

    def __init__(
        self,
        sensitivity: str = "high",  # low, medium, high
        custom_patterns: list[tuple] = None,
    ):
        self.sensitivity = sensitivity
        self.patterns = self.INJECTION_PATTERNS + self.SUSPICIOUS_FINANCIAL_KEYWORDS

        if custom_patterns:
            self.patterns.extend(custom_patterns)

        # Sensitivity thresholds
        self.thresholds = {
            "low": 0.9,
            "medium": 0.7,
            "high": 0.5,
        }

    async def screen_input(self, text: str) -> SecurityScreenResult:
        """
        Screen input text for potential injection attempts.

        Args:
            text: User input to screen

        Returns:
            SecurityScreenResult with safety determination
        """
        detected_patterns = []
        total_risk = 0.0

        # Normalize text for pattern matching
        normalized = text.lower().strip()

        # Check each pattern
        for pattern, attack_type, severity in self.patterns:
            if re.search(pattern, normalized, re.IGNORECASE):
                detected_patterns.append({
                    "pattern": attack_type,
                    "severity": severity,
                    "matched": pattern,
                })
                total_risk = max(total_risk, severity)

        # Check for excessive special characters (potential encoding attacks)
        special_char_ratio = len(re.findall(r'[^\w\s]', text)) / max(len(text), 1)
        if special_char_ratio > 0.3:
            detected_patterns.append({
                "pattern": "excessive_special_chars",
                "severity": 0.6,
                "matched": f"ratio: {special_char_ratio:.2f}",
            })
            total_risk = max(total_risk, 0.6)

        # Check for very long inputs (potential prompt stuffing)
        if len(text) > 5000:
            detected_patterns.append({
                "pattern": "excessive_length",
                "severity": 0.5,
                "matched": f"length: {len(text)}",
            })
            total_risk = max(total_risk, 0.5)

        # Determine if input should be blocked
        threshold = self.thresholds.get(self.sensitivity, 0.7)
        is_safe = total_risk < threshold

        # Sanitize input if slightly risky but still allowed
        sanitized = self._sanitize_input(text) if detected_patterns else text

        result = SecurityScreenResult(
            is_safe=is_safe,
            risk_score=total_risk,
            detected_patterns=[p["pattern"] for p in detected_patterns],
            sanitized_input=sanitized if is_safe else None,
            blocked_reason=f"High-risk patterns detected: {[p['pattern'] for p in detected_patterns]}" if not is_safe else None,
        )

        # Log security event
        if detected_patterns:
            logger.warning(
                "prompt_guard_detection",
                is_safe=is_safe,
                risk_score=total_risk,
                patterns=detected_patterns,
                input_length=len(text),
            )

        return result

    def _sanitize_input(self, text: str) -> str:
        """
        Sanitize potentially risky input while preserving legitimate content.

        Args:
            text: Input text to sanitize

        Returns:
            Sanitized text
        """
        sanitized = text

        # Remove potential delimiter injections
        sanitized = re.sub(r'<\|?/?system\|?>', '', sanitized)
        sanitized = re.sub(r'\[/?INST\]', '', sanitized)

        # Escape backticks that could be used for code injection
        sanitized = sanitized.replace('```', '` ` `')

        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', sanitized)

        return sanitized.strip()

    async def validate_financial_operation(
        self,
        operation: str,
        amount: float,
        user_role: str,
    ) -> SecurityScreenResult:
        """
        Additional validation for financial operations.

        Args:
            operation: Type of operation (transfer, approve, etc.)
            amount: Amount involved
            user_role: Role of user requesting operation

        Returns:
            SecurityScreenResult for the operation
        """
        detected_issues = []
        risk_score = 0.0

        # Check operation against role permissions
        role_limits = {
            "viewer": {"max_amount": 0, "allowed_ops": ["view", "query"]},
            "analyst": {"max_amount": 50000, "allowed_ops": ["view", "query", "report"]},
            "manager": {"max_amount": 500000, "allowed_ops": ["view", "query", "report", "approve"]},
            "director": {"max_amount": 2000000, "allowed_ops": ["view", "query", "report", "approve", "override"]},
            "admin": {"max_amount": float("inf"), "allowed_ops": ["all"]},
        }

        limits = role_limits.get(user_role, role_limits["viewer"])

        # Check amount threshold
        if amount > limits["max_amount"]:
            detected_issues.append(f"Amount {amount} exceeds role limit {limits['max_amount']}")
            risk_score = 0.9

        # Check operation permission
        if operation not in limits["allowed_ops"] and "all" not in limits["allowed_ops"]:
            detected_issues.append(f"Operation '{operation}' not allowed for role '{user_role}'")
            risk_score = max(risk_score, 0.95)

        return SecurityScreenResult(
            is_safe=len(detected_issues) == 0,
            risk_score=risk_score,
            detected_patterns=detected_issues,
            blocked_reason="; ".join(detected_issues) if detected_issues else None,
        )


class RateLimiter:
    """
    Rate limiting for security-sensitive operations.
    """

    def __init__(self):
        self._requests: dict[str, list[float]] = {}
        self._limits = {
            "query": (100, 60),  # 100 requests per 60 seconds
            "financial_op": (10, 60),  # 10 financial ops per 60 seconds
            "export": (5, 300),  # 5 exports per 5 minutes
        }

    async def check_rate_limit(
        self,
        user_id: str,
        operation_type: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Check if user is within rate limits.

        Args:
            user_id: User identifier
            operation_type: Type of operation

        Returns:
            Tuple of (is_allowed, reason_if_blocked)
        """
        import time

        key = f"{user_id}:{operation_type}"
        current_time = time.time()

        limit, window = self._limits.get(operation_type, (100, 60))

        # Get or create request history
        if key not in self._requests:
            self._requests[key] = []

        # Clean old requests
        self._requests[key] = [
            t for t in self._requests[key]
            if current_time - t < window
        ]

        # Check limit
        if len(self._requests[key]) >= limit:
            return False, f"Rate limit exceeded: {limit} {operation_type}s per {window}s"

        # Record request
        self._requests[key].append(current_time)

        return True, None
