"""
LLM-Powered Agents for DAMAC Finance AI
Uses GPT-5 for intelligent finance operations
"""
import json
from typing import Any
import structlog

from .client import get_llm_client

logger = structlog.get_logger()


class OrchestratorLLMAgent:
    """
    Orchestrator Agent - Classifies queries and routes to specialized agents.
    Uses GPT-5-mini for fast, cost-effective classification.
    """

    SYSTEM_PROMPT = """You are the DAMAC Finance AI orchestrator. Classify user queries into:
- "invoice": Vendor invoices, purchase orders, payments to vendors, construction costs
- "payment": Customer payment plans, milestones, escrow, DLD fees
- "commission": Broker commissions, sales agent payouts, commission splits
- "general": Other queries

Respond with JSON:
{
  "intent": "invoice|payment|commission|general",
  "confidence": 0.0-1.0,
  "entities": {
    "amount": {"value": number, "currency": "AED"},
    "vendor_name": "string or null",
    "project_name": "string or null",
    "broker_name": "string or null",
    "plan_type": "string or null",
    ...other relevant entities
  }
}

Extract all relevant entities: amounts, vendor names, project names, dates, broker info, etc."""

    def __init__(self):
        self.client = get_llm_client()

    async def classify(self, query: str) -> dict:
        """Classify query intent and extract entities."""
        try:
            result = self.client.chat_completion(
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": query}
                ],
                model=self.client.orchestrator_model,
                max_tokens=1000,
            )
            logger.info("query_classified", intent=result.get("intent"))
            return result
        except Exception as e:
            logger.error("classification_error", error=str(e))
            return {"intent": "general", "confidence": 0.0, "entities": {}, "error": str(e)}


class InvoiceLLMAgent:
    """
    Invoice Processing Agent - Handles vendor invoice workflows.
    """

    SYSTEM_PROMPT = """You are DAMAC's Invoice Processing Agent for Dubai real estate operations.

UAE Tax & Finance Rules:
- VAT: 5% on subtotal
- Retention: 5% held for 12 months (defects liability period)
- Net Payable = Subtotal + VAT - Retention

Approval Thresholds (AED):
- Up to 50,000: Auto-approve (if PO matched)
- 50,001 - 500,000: Project Manager approval
- 500,001 - 2,000,000: Finance Director approval
- Above 2,000,000: CFO approval

TRN (Tax Registration Number) Format: 15 digits starting with 100

DAMAC Projects: DAMAC Hills, DAMAC Hills 2, DAMAC Lagoons, Cavalli Tower, Safa One, AYKON City

Respond with JSON:
{
  "parsed_invoice": {
    "vendor_name": "string",
    "vendor_trn": "string or null",
    "amount": number,
    "project_name": "string",
    "description": "string"
  },
  "calculations": {
    "subtotal": number,
    "vat_rate": 5,
    "vat_amount": number,
    "retention_rate": 5,
    "retention_amount": number,
    "net_payable": number
  },
  "approval": {
    "level": "auto|project_manager|finance_director|cfo",
    "required_approvers": ["list of roles"],
    "threshold_reason": "explanation"
  },
  "validation": {
    "is_valid": boolean,
    "issues": ["list of issues"],
    "recommendations": ["list of recommendations"]
  }
}"""

    def __init__(self):
        self.client = get_llm_client()

    async def process(self, query: str, entities: dict) -> dict:
        """Process invoice query."""
        try:
            result = self.client.chat_completion(
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"Query: {query}\nEntities: {json.dumps(entities)}"}
                ],
                max_tokens=2000,
            )
            return result
        except Exception as e:
            logger.error("invoice_processing_error", error=str(e))
            return {"error": str(e)}


class PaymentLLMAgent:
    """
    Payment Plan Agent - Manages customer payment schedules.
    """

    SYSTEM_PROMPT = """You are DAMAC's Payment Plan Agent for Dubai real estate operations.

Payment Plans:
- 1% Monthly: 1% per month during construction (~60%), 40% on handover
- 60/40: 60% during construction (milestone-based), 40% on handover
- 80/20: 80% during construction, 20% on handover
- 75/25: 75% during construction, 25% on handover
- 50/50: 50% during construction, 50% on handover

Dubai Fees:
- DLD Registration Fee: 4% of property value
- Admin Fee: AED 4,200 (standard)
- Oqood Fee (off-plan): AED 40 per sqft

Escrow Requirements (RERA):
- All customer payments must go to RERA-registered escrow account
- Contractor payments from escrow require RERA approval

DAMAC Projects: DAMAC Hills, DAMAC Hills 2, DAMAC Lagoons, Cavalli Tower, Safa One, AYKON City

Respond with JSON:
{
  "payment_status": {
    "plan_type": "string",
    "property_value": number,
    "construction_share": number,
    "handover_share": number
  },
  "milestones": [
    {"name": "string", "percentage": number, "amount": number, "status": "paid|pending|due"}
  ],
  "fees": {
    "dld_fee": number,
    "admin_fee": 4200,
    "oqood_fee": "number or formula"
  },
  "next_due": {
    "milestone": "string",
    "amount": number,
    "notes": "string"
  },
  "escrow_note": "string"
}"""

    def __init__(self):
        self.client = get_llm_client()

    async def process(self, query: str, entities: dict) -> dict:
        """Process payment plan query."""
        try:
            result = self.client.chat_completion(
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"Query: {query}\nEntities: {json.dumps(entities)}"}
                ],
                max_tokens=4000,
            )
            return result
        except Exception as e:
            logger.error("payment_processing_error", error=str(e))
            return {"error": str(e)}


class CommissionLLMAgent:
    """
    Commission Agent - Calculates and processes broker commissions.
    """

    SYSTEM_PROMPT = """You are DAMAC's Commission Agent for Dubai real estate operations.

Commission Structure:
- Standard rate: 5% of sale price
- Premium projects may have negotiated rates (3-7%)
- VAT on commission: 5%

Commission Split:
- External broker: 60% of gross commission
- Internal sales team: 40% of gross commission

RERA Requirements:
- All brokers must have valid RERA BRN (Broker Registration Number)
- BRN format: BRN-XXXXX (5 digits)
- Expired BRN = commission on hold until renewed

DAMAC Projects: DAMAC Hills, DAMAC Hills 2, DAMAC Lagoons, Cavalli Tower, Safa One, AYKON City

Respond with JSON:
{
  "calculation": {
    "sale_price": number,
    "commission_rate": 5,
    "gross_commission": number,
    "vat_rate": 5,
    "vat_amount": number,
    "total_with_vat": number
  },
  "split": {
    "external_broker": {
      "name": "string",
      "percentage": 60,
      "amount": number,
      "vat": number,
      "total": number
    },
    "internal_sales": {
      "percentage": 40,
      "amount": number,
      "vat": number,
      "total": number
    }
  },
  "broker_validation": {
    "brn": "string",
    "is_valid_format": boolean,
    "status": "valid|invalid|needs_verification"
  },
  "total_payable": number
}"""

    def __init__(self):
        self.client = get_llm_client()

    async def process(self, query: str, entities: dict) -> dict:
        """Process commission query."""
        try:
            result = self.client.chat_completion(
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"Query: {query}\nEntities: {json.dumps(entities)}"}
                ],
                max_tokens=3000,
            )
            return result
        except Exception as e:
            logger.error("commission_processing_error", error=str(e))
            return {"error": str(e)}
