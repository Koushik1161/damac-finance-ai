"""
Invoice Processing Agent - Handles vendor invoice workflows
"""
from typing import Any, Optional
from decimal import Decimal
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.models.openai import OpenAIModel
import structlog

logger = structlog.get_logger()

# UAE Tax Constants
VAT_RATE = Decimal("0.05")  # 5% VAT
RETENTION_RATE = Decimal("0.05")  # 5% retention


class InvoiceLineItem(BaseModel):
    """Single line item on an invoice"""
    line_number: int
    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    amount: Decimal


class ParsedInvoice(BaseModel):
    """Structured invoice data"""
    invoice_id: str
    vendor_name: str
    vendor_trn: Optional[str] = None  # Tax Registration Number
    invoice_date: str
    due_date: str
    project_name: str
    cost_center: str
    line_items: list[InvoiceLineItem]
    subtotal: Decimal
    vat_amount: Decimal
    retention_amount: Decimal
    total_amount: Decimal
    net_payable: Decimal
    po_reference: Optional[str] = None
    contract_reference: Optional[str] = None


class ApprovalRecommendation(BaseModel):
    """Invoice approval workflow recommendation"""
    approval_level: str  # "auto", "manager", "director", "cfo"
    threshold_reason: str
    required_approvers: list[str]
    flags: list[str] = Field(default_factory=list)
    risk_score: float = Field(ge=0.0, le=1.0)


class InvoiceProcessingResult(BaseModel):
    """Complete result of invoice processing"""
    parsed_invoice: ParsedInvoice
    validation_status: str  # "valid", "warnings", "errors"
    validation_messages: list[str]
    approval: ApprovalRecommendation
    erp_entry_created: bool
    erp_reference: Optional[str] = None


class InvoiceAgent:
    """
    Specialized agent for processing vendor invoices.

    Capabilities:
    - Parse invoice documents (text, structured data)
    - Extract and validate line items
    - Calculate VAT and retention
    - Route for approval based on thresholds
    - Create ERP entries
    """

    SYSTEM_PROMPT = """You are a specialized invoice processing agent for DAMAC Properties.

Your responsibilities:
1. Parse invoice details from text or structured input
2. Validate invoice data against DAMAC standards
3. Calculate UAE VAT (5%) and construction retention (5%)
4. Determine approval routing based on amount thresholds
5. Prepare ERP entries

DAMAC Invoice Standards:
- All invoices must have valid TRN (Tax Registration Number)
- Construction invoices require PO reference
- Retention is held for 12 months (defects liability period)
- VAT is calculated on subtotal before retention

Approval Thresholds:
- Up to AED 50,000: Auto-approve (if PO matched)
- AED 50,001 - 500,000: Project Manager approval
- AED 500,001 - 2,000,000: Finance Director approval
- Above AED 2,000,000: CFO approval

Validation Checks:
- TRN format: 100XXXXXXXXX (15 digits starting with 100)
- Invoice date not future dated
- Line items match PO specifications
- Vendor on approved vendor list
- No duplicate invoice numbers

Cost Centers by Project:
- DAMAC Hills: CC-DAH-XXX
- DAMAC Hills 2: CC-DH2-XXX
- Cavalli Tower: CC-CAV-XXX
- DAMAC Lagoons: CC-LAG-XXX
"""

    def __init__(self, model: str = "gpt-4o"):
        self.model = OpenAIModel(model)

        # Create the agent with tools
        self.agent = Agent(
            model=self.model,
            result_type=InvoiceProcessingResult,
            system_prompt=self.SYSTEM_PROMPT,
        )

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register tools available to the invoice agent"""

        @self.agent.tool
        async def validate_vendor_trn(ctx: RunContext, trn: str) -> dict:
            """Validate UAE Tax Registration Number format"""
            is_valid = (
                len(trn) == 15 and
                trn.startswith("100") and
                trn.isdigit()
            )
            return {
                "trn": trn,
                "is_valid": is_valid,
                "message": "Valid TRN format" if is_valid else "Invalid TRN format - must be 15 digits starting with 100"
            }

        @self.agent.tool
        async def calculate_invoice_amounts(
            ctx: RunContext,
            subtotal: float,
            apply_vat: bool = True,
            apply_retention: bool = True
        ) -> dict:
            """Calculate VAT, retention, and net payable amounts"""
            subtotal_dec = Decimal(str(subtotal))

            vat = subtotal_dec * VAT_RATE if apply_vat else Decimal("0")
            retention = subtotal_dec * RETENTION_RATE if apply_retention else Decimal("0")
            total = subtotal_dec + vat
            net_payable = total - retention

            return {
                "subtotal_aed": float(subtotal_dec),
                "vat_rate": float(VAT_RATE),
                "vat_amount_aed": float(vat),
                "retention_rate": float(RETENTION_RATE),
                "retention_amount_aed": float(retention),
                "total_aed": float(total),
                "net_payable_aed": float(net_payable),
            }

        @self.agent.tool
        async def check_po_match(
            ctx: RunContext,
            po_number: str,
            vendor_name: str,
            amount: float
        ) -> dict:
            """Check if invoice matches Purchase Order (mock implementation)"""
            # In production, this would query the ERP system
            return {
                "po_number": po_number,
                "po_found": True,  # Mock: always found
                "vendor_match": True,
                "amount_within_tolerance": True,
                "remaining_po_value": 150000.00,  # Mock value
                "message": f"PO {po_number} validated for {vendor_name}"
            }

        @self.agent.tool
        async def determine_approval_route(
            ctx: RunContext,
            net_payable: float,
            has_po: bool,
            is_new_vendor: bool = False
        ) -> dict:
            """Determine approval workflow based on amount and risk factors"""
            amount = Decimal(str(net_payable))

            if amount <= 50000 and has_po and not is_new_vendor:
                level = "auto"
                approvers = []
            elif amount <= 500000:
                level = "manager"
                approvers = ["Project Manager", "Finance Manager"]
            elif amount <= 2000000:
                level = "director"
                approvers = ["Finance Director"]
            else:
                level = "cfo"
                approvers = ["CFO", "Finance Director"]

            # Risk flags
            flags = []
            if is_new_vendor:
                flags.append("NEW_VENDOR")
            if amount > 1000000:
                flags.append("HIGH_VALUE")
            if not has_po:
                flags.append("NO_PO")

            risk_score = len(flags) * 0.2

            return {
                "approval_level": level,
                "required_approvers": approvers,
                "flags": flags,
                "risk_score": min(risk_score, 1.0),
                "threshold_reason": f"Amount AED {float(amount):,.2f} requires {level} approval"
            }

        @self.agent.tool
        async def create_erp_entry(
            ctx: RunContext,
            invoice_data: dict
        ) -> dict:
            """Create entry in ERP system (mock implementation)"""
            # In production, this would create actual SAP/Oracle entry
            import uuid
            erp_ref = f"ERP-INV-{uuid.uuid4().hex[:8].upper()}"

            return {
                "success": True,
                "erp_reference": erp_ref,
                "status": "pending_approval",
                "message": f"Invoice entry created with reference {erp_ref}"
            }

    async def process(
        self,
        query: str,
        entities: dict[str, Any],
        deps: Any,
    ) -> dict[str, Any]:
        """
        Process an invoice-related query.

        Args:
            query: Natural language query about invoices
            entities: Extracted entities from orchestrator
            deps: Dependencies including security context

        Returns:
            Processing result with parsed invoice and recommendations
        """
        logger.info(
            "invoice_agent_processing",
            query=query[:100],
            entities=entities,
        )

        try:
            result = await self.agent.run(
                f"""Process this invoice query: {query}

Extracted entities: {entities}

Please:
1. Parse any invoice details mentioned
2. Calculate VAT (5%) and retention (5%) if applicable
3. Validate the data
4. Determine approval routing
5. Create ERP entry if valid
"""
            )

            return {
                "status": "success",
                "agent": "invoice",
                "result": result.data.dict() if hasattr(result.data, 'dict') else result.data,
                "summary": f"Invoice processed with status: {result.data.validation_status}"
            }

        except Exception as e:
            logger.error("invoice_processing_error", error=str(e))
            return {
                "status": "error",
                "agent": "invoice",
                "error": str(e),
                "summary": "Failed to process invoice query"
            }

    async def parse_invoice_document(
        self,
        document_text: str,
        document_type: str = "text"
    ) -> ParsedInvoice:
        """
        Parse invoice from document text or structured input.

        Args:
            document_text: Raw text or JSON representation of invoice
            document_type: "text", "pdf_text", or "structured"

        Returns:
            Parsed and structured invoice data
        """
        result = await self.agent.run(
            f"""Parse this invoice document and extract all details:

Document Type: {document_type}
Content:
{document_text}

Extract:
- Invoice ID, dates
- Vendor details (name, TRN)
- All line items
- Calculate totals with VAT and retention
"""
        )

        return result.data.parsed_invoice
