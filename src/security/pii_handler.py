"""
PII (Personally Identifiable Information) Handler
Detects, masks, and manages sensitive data in DAMAC finance operations
"""
import re
from typing import Optional
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger()


class PIIMatch(BaseModel):
    """Single PII match in text"""
    pii_type: str
    original: str
    masked: str
    start_pos: int
    end_pos: int
    confidence: float


class PIIMaskResult(BaseModel):
    """Result of PII masking operation"""
    original_text: str
    masked_text: str
    pii_found: list[PIIMatch]
    pii_count: int
    has_high_sensitivity_pii: bool


class PIIHandler:
    """
    PII detection and masking for enterprise compliance.

    Handles:
    - UAE Emirates ID
    - Passport numbers
    - Bank account numbers (IBAN)
    - Credit card numbers
    - Phone numbers
    - Email addresses
    - Tax Registration Numbers (TRN)
    """

    # PII detection patterns for UAE/Dubai context
    PII_PATTERNS = {
        "emirates_id": {
            "pattern": r"\b784[-\s]?\d{4}[-\s]?\d{7}[-\s]?\d\b",
            "mask_format": "784-****-*******-*",
            "sensitivity": "high",
            "description": "UAE Emirates ID",
        },
        "passport": {
            "pattern": r"\b[A-Z]{1,2}\d{6,9}\b",
            "mask_format": "**{last4}",
            "sensitivity": "high",
            "description": "Passport Number",
        },
        "iban": {
            "pattern": r"\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b",
            "mask_format": "{first4}****{last4}",
            "sensitivity": "high",
            "description": "International Bank Account Number",
        },
        "credit_card": {
            "pattern": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
            "mask_format": "****-****-****-{last4}",
            "sensitivity": "critical",
            "description": "Credit Card Number",
        },
        "uae_phone": {
            "pattern": r"\b\+?971[-\s]?(?:50|51|52|54|55|56|58)[-\s]?\d{3}[-\s]?\d{4}\b",
            "mask_format": "+971 ** *** {last4}",
            "sensitivity": "medium",
            "description": "UAE Phone Number",
        },
        "email": {
            "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "mask_format": "{first2}***@***",
            "sensitivity": "medium",
            "description": "Email Address",
        },
        "trn": {
            "pattern": r"\b100\d{12}\b",
            "mask_format": "100*********{last3}",
            "sensitivity": "medium",
            "description": "UAE Tax Registration Number",
        },
        "rera_brn": {
            "pattern": r"\bBRN[-\s]?\d{5}\b",
            "mask_format": "BRN-*****",
            "sensitivity": "low",
            "description": "RERA Broker Registration Number",
        },
    }

    def __init__(
        self,
        mask_all: bool = True,
        allowed_pii_types: list[str] = None,
        log_pii_access: bool = True,
    ):
        """
        Initialize PII handler.

        Args:
            mask_all: If True, mask all detected PII
            allowed_pii_types: List of PII types that should not be masked
            log_pii_access: If True, log all PII detections
        """
        self.mask_all = mask_all
        self.allowed_pii_types = allowed_pii_types or []
        self.log_pii_access = log_pii_access

    def mask_text(self, text: str) -> PIIMaskResult:
        """
        Detect and mask PII in text.

        Args:
            text: Text to scan for PII

        Returns:
            PIIMaskResult with masked text and detected PII
        """
        if not text:
            return PIIMaskResult(
                original_text=text,
                masked_text=text,
                pii_found=[],
                pii_count=0,
                has_high_sensitivity_pii=False,
            )

        masked_text = text
        pii_found = []
        has_high_sensitivity = False

        # Detect each type of PII
        for pii_type, config in self.PII_PATTERNS.items():
            matches = list(re.finditer(config["pattern"], text, re.IGNORECASE))

            for match in matches:
                original_value = match.group()
                start_pos = match.start()
                end_pos = match.end()

                # Generate masked value
                masked_value = self._generate_mask(
                    original_value,
                    config["mask_format"],
                    pii_type
                )

                # Track high sensitivity PII
                if config["sensitivity"] in ["high", "critical"]:
                    has_high_sensitivity = True

                # Create PII match record
                pii_match = PIIMatch(
                    pii_type=pii_type,
                    original=original_value,
                    masked=masked_value,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    confidence=0.95 if config["sensitivity"] == "high" else 0.85,
                )
                pii_found.append(pii_match)

                # Apply mask if not in allowed list
                if pii_type not in self.allowed_pii_types:
                    masked_text = masked_text.replace(original_value, masked_value)

        # Log if configured
        if self.log_pii_access and pii_found:
            logger.info(
                "pii_detected",
                pii_types=[p.pii_type for p in pii_found],
                count=len(pii_found),
                has_high_sensitivity=has_high_sensitivity,
            )

        return PIIMaskResult(
            original_text=text,
            masked_text=masked_text,
            pii_found=pii_found,
            pii_count=len(pii_found),
            has_high_sensitivity_pii=has_high_sensitivity,
        )

    def _generate_mask(
        self,
        value: str,
        mask_format: str,
        pii_type: str
    ) -> str:
        """
        Generate masked value based on format template.

        Args:
            value: Original PII value
            mask_format: Template for masking
            pii_type: Type of PII

        Returns:
            Masked value
        """
        # Extract parts for partial masking
        clean_value = re.sub(r'[-\s]', '', value)

        if "{last4}" in mask_format:
            last4 = clean_value[-4:] if len(clean_value) >= 4 else clean_value
            mask_format = mask_format.replace("{last4}", last4)

        if "{first4}" in mask_format:
            first4 = clean_value[:4] if len(clean_value) >= 4 else clean_value
            mask_format = mask_format.replace("{first4}", first4)

        if "{first2}" in mask_format:
            first2 = clean_value[:2] if len(clean_value) >= 2 else clean_value
            mask_format = mask_format.replace("{first2}", first2)

        if "{last3}" in mask_format:
            last3 = clean_value[-3:] if len(clean_value) >= 3 else clean_value
            mask_format = mask_format.replace("{last3}", last3)

        return mask_format

    def detect_pii(self, text: str) -> list[PIIMatch]:
        """
        Detect PII without masking (for validation purposes).

        Args:
            text: Text to scan

        Returns:
            List of detected PII matches
        """
        result = self.mask_text(text)
        return result.pii_found

    def validate_no_pii(self, text: str) -> tuple[bool, list[str]]:
        """
        Validate that text contains no PII.

        Args:
            text: Text to validate

        Returns:
            Tuple of (is_clean, list of detected PII types)
        """
        result = self.mask_text(text)
        pii_types = list(set(p.pii_type for p in result.pii_found))
        return (len(pii_types) == 0, pii_types)

    def redact_for_logging(self, data: dict) -> dict:
        """
        Recursively redact PII from dictionary for safe logging.

        Args:
            data: Dictionary that may contain PII

        Returns:
            Dictionary with PII redacted
        """
        if not isinstance(data, dict):
            if isinstance(data, str):
                return self.mask_text(data).masked_text
            return data

        redacted = {}
        for key, value in data.items():
            if isinstance(value, str):
                redacted[key] = self.mask_text(value).masked_text
            elif isinstance(value, dict):
                redacted[key] = self.redact_for_logging(value)
            elif isinstance(value, list):
                redacted[key] = [self.redact_for_logging(item) for item in value]
            else:
                redacted[key] = value

        return redacted


class PIIVault:
    """
    Secure storage for PII with tokenization.
    In production, this would use Azure Key Vault or similar.
    """

    def __init__(self):
        self._vault: dict[str, str] = {}  # token -> encrypted value
        self._reverse: dict[str, str] = {}  # hash(value) -> token

    def tokenize(self, pii_value: str, pii_type: str) -> str:
        """
        Replace PII with a secure token.

        Args:
            pii_value: Original PII value
            pii_type: Type of PII

        Returns:
            Token that can be used in place of PII
        """
        import hashlib
        import uuid

        # Check if already tokenized
        value_hash = hashlib.sha256(pii_value.encode()).hexdigest()
        if value_hash in self._reverse:
            return self._reverse[value_hash]

        # Generate token
        token = f"PII_{pii_type.upper()}_{uuid.uuid4().hex[:12]}"

        # Store (in production, encrypt before storing)
        self._vault[token] = pii_value
        self._reverse[value_hash] = token

        logger.info(
            "pii_tokenized",
            pii_type=pii_type,
            token=token,
        )

        return token

    def detokenize(self, token: str, requester_id: str) -> Optional[str]:
        """
        Retrieve original PII from token (with audit logging).

        Args:
            token: Token to detokenize
            requester_id: ID of user/system requesting detokenization

        Returns:
            Original PII value or None if not found
        """
        if token not in self._vault:
            logger.warning(
                "pii_detokenize_failed",
                token=token,
                requester=requester_id,
                reason="token_not_found",
            )
            return None

        logger.info(
            "pii_detokenized",
            token=token,
            requester=requester_id,
        )

        return self._vault[token]
