"""
Commission Agent - Calculates and processes broker commissions
"""
from typing import Any, Optional
from decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
import structlog

logger = structlog.get_logger()

# Commission Constants
STANDARD_COMMISSION_RATE = Decimal("0.05")  # 5%
VAT_RATE = Decimal("0.05")  # 5% VAT on commission
EXTERNAL_BROKER_SPLIT = Decimal("0.60")  # 60% to external broker
INTERNAL_SALES_SPLIT = Decimal("0.40")  # 40% to internal team


class BrokerDetails(BaseModel):
    """Broker information"""
    broker_name: str
    rera_brn: str  # Broker Registration Number
    trn: Optional[str] = None  # Tax Registration Number
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    is_verified: bool = False


class CommissionSplit(BaseModel):
    """Commission split breakdown"""
    external_broker_aed: Decimal
    internal_sales_aed: Decimal
    team_lead_bonus_aed: Decimal = Decimal("0")
    referral_fee_aed: Decimal = Decimal("0")


class CommissionCalculation(BaseModel):
    """Complete commission calculation"""
    transaction_id: str
    property_unit: str
    project_name: str
    sale_price_aed: Decimal
    commission_rate_percent: Decimal
    gross_commission_aed: Decimal
    vat_amount_aed: Decimal
    total_with_vat_aed: Decimal
    split: CommissionSplit
    broker: BrokerDetails
    sales_agent: str
    calculation_date: date
    payment_status: str  # pending, approved, processing, paid


class CommissionReport(BaseModel):
    """Commission report for period"""
    period_start: date
    period_end: date
    total_sales_aed: Decimal
    total_commission_aed: Decimal
    total_vat_aed: Decimal
    num_transactions: int
    top_brokers: list[dict]
    top_agents: list[dict]
    by_project: dict[str, Decimal]


class CommissionProcessingResult(BaseModel):
    """Result of commission query processing"""
    query_type: str  # "calculate", "status", "report", "validate_broker"
    calculation: Optional[CommissionCalculation] = None
    report: Optional[CommissionReport] = None
    summary: str
    warnings: list[str] = Field(default_factory=list)


class CommissionAgent:
    """
    Specialized agent for calculating and processing broker commissions.

    Capabilities:
    - Calculate commission amounts
    - Apply commission splits
    - Validate RERA broker numbers
    - Generate commission reports
    - Track payment status
    """

    SYSTEM_PROMPT = """You are a specialized commission processing agent for DAMAC Properties.

Your responsibilities:
1. Calculate broker commissions on property sales
2. Apply correct commission splits (external/internal)
3. Validate RERA broker registration numbers
4. Calculate VAT on commissions
5. Generate commission reports

Commission Structure:
- Standard rate: 5% of sale price
- Premium properties may have negotiated rates (3-7%)
- Off-plan projects: Full commission on SPA signing
- Ready properties: Commission on transfer

Commission Split:
- External broker: 60% of gross commission
- Internal sales team: 40% of gross commission
- Team lead bonus: Optional (from internal share)
- Referral fees: Deducted before split

VAT Treatment:
- 5% VAT applies to all commission payments
- Broker must provide valid TRN for VAT invoice
- DAMAC pays gross + VAT to registered brokers
- Non-VAT registered brokers receive gross only

RERA Requirements:
- All brokers must have valid RERA BRN (Broker Registration Number)
- BRN format: BRN-XXXXX (5 digits)
- Expired BRN = commission on hold until renewed
- DAMAC employees cannot receive broker commission (conflict of interest)

Payment Process:
1. Sale completed (SPA signed or transferred)
2. Commission calculation submitted
3. Broker validation (RERA check)
4. Finance approval
5. Payment processing (within 45 days)

Commission Scenarios:
- Direct sale (no broker): Internal team gets full 5%
- Single broker: Standard 60/40 split
- Co-broker: Split between brokers before 60/40
- Sub-agent: Main broker handles sub-agent payment
"""

    def __init__(self, model: str = "gpt-4o"):
        self.model = OpenAIModel(model)

        self.agent = Agent(
            model=self.model,
            result_type=CommissionProcessingResult,
            system_prompt=self.SYSTEM_PROMPT,
        )

        self._register_tools()

    def _register_tools(self):
        """Register tools for commission agent"""

        @self.agent.tool
        async def calculate_commission(
            ctx: RunContext,
            sale_price: float,
            commission_rate: float = 5.0,
            has_external_broker: bool = True,
            is_vat_registered: bool = True
        ) -> dict:
            """Calculate commission with splits and VAT"""
            price = Decimal(str(sale_price))
            rate = Decimal(str(commission_rate)) / 100

            gross_commission = price * rate
            vat = gross_commission * VAT_RATE if is_vat_registered else Decimal("0")
            total = gross_commission + vat

            if has_external_broker:
                external = gross_commission * EXTERNAL_BROKER_SPLIT
                internal = gross_commission * INTERNAL_SALES_SPLIT
            else:
                external = Decimal("0")
                internal = gross_commission

            return {
                "sale_price_aed": float(price),
                "commission_rate_percent": float(rate * 100),
                "gross_commission_aed": float(gross_commission),
                "vat_rate_percent": 5.0 if is_vat_registered else 0,
                "vat_amount_aed": float(vat),
                "total_payable_aed": float(total),
                "split": {
                    "external_broker_aed": float(external),
                    "internal_sales_aed": float(internal),
                    "external_with_vat_aed": float(external + (external * VAT_RATE if is_vat_registered else 0)),
                }
            }

        @self.agent.tool
        async def validate_rera_brn(
            ctx: RunContext,
            brn: str
        ) -> dict:
            """Validate RERA Broker Registration Number"""
            # BRN format: BRN-XXXXX
            is_valid_format = (
                brn.startswith("BRN-") and
                len(brn) == 9 and
                brn[4:].isdigit()
            )

            if not is_valid_format:
                return {
                    "brn": brn,
                    "is_valid": False,
                    "status": "invalid_format",
                    "message": "BRN must be in format BRN-XXXXX (5 digits)"
                }

            # Mock RERA database check
            import random
            is_active = random.random() > 0.1  # 90% chance of being active

            return {
                "brn": brn,
                "is_valid": is_active,
                "status": "active" if is_active else "expired",
                "broker_name": "Sample Broker LLC" if is_active else None,
                "expiry_date": "2025-12-31" if is_active else "2023-06-30",
                "message": "Broker registration verified" if is_active else "BRN expired - commission on hold"
            }

        @self.agent.tool
        async def get_commission_status(
            ctx: RunContext,
            commission_id: str
        ) -> dict:
            """Get status of commission payment (mock)"""
            import random
            from datetime import datetime, timedelta

            statuses = ["pending_approval", "approved", "processing", "paid", "on_hold"]
            status = random.choice(statuses)

            calc_date = datetime.now() - timedelta(days=random.randint(1, 60))

            return {
                "commission_id": commission_id,
                "status": status,
                "gross_amount_aed": round(random.uniform(50000, 500000), 2),
                "calculation_date": calc_date.date().isoformat(),
                "approval_date": (calc_date + timedelta(days=3)).date().isoformat() if status != "pending_approval" else None,
                "expected_payment_date": (calc_date + timedelta(days=45)).date().isoformat(),
                "actual_payment_date": (calc_date + timedelta(days=random.randint(30, 45))).date().isoformat() if status == "paid" else None,
                "hold_reason": "Pending RERA verification" if status == "on_hold" else None
            }

        @self.agent.tool
        async def generate_commission_report(
            ctx: RunContext,
            start_date: str,
            end_date: str,
            group_by: str = "project"
        ) -> dict:
            """Generate commission report for period (mock)"""
            import random

            projects = ["DAMAC Hills", "Cavalli Tower", "DAMAC Lagoons", "Safa One", "AYKON City"]
            by_project = {p: round(random.uniform(500000, 5000000), 2) for p in projects}

            total_commission = sum(by_project.values())
            total_sales = total_commission / 0.05  # Reverse calculate from 5%

            top_brokers = [
                {"name": f"Broker {i}", "commission_aed": round(random.uniform(100000, 500000), 2), "deals": random.randint(1, 10)}
                for i in range(1, 6)
            ]
            top_brokers.sort(key=lambda x: x["commission_aed"], reverse=True)

            top_agents = [
                {"name": f"Agent {i}", "commission_aed": round(random.uniform(50000, 200000), 2), "deals": random.randint(1, 15)}
                for i in range(1, 6)
            ]
            top_agents.sort(key=lambda x: x["commission_aed"], reverse=True)

            return {
                "period": {"start": start_date, "end": end_date},
                "summary": {
                    "total_sales_aed": round(total_sales, 2),
                    "total_commission_aed": round(total_commission, 2),
                    "total_vat_aed": round(total_commission * float(VAT_RATE), 2),
                    "num_transactions": sum(b["deals"] for b in top_brokers),
                    "avg_commission_per_deal": round(total_commission / max(1, sum(b["deals"] for b in top_brokers)), 2)
                },
                "by_project": by_project,
                "top_brokers": top_brokers[:5],
                "top_agents": top_agents[:5],
            }

        @self.agent.tool
        async def check_conflict_of_interest(
            ctx: RunContext,
            broker_name: str,
            sales_agent: str
        ) -> dict:
            """Check for conflict of interest between broker and sales agent"""
            # In production, this would check against HR database
            import random

            has_conflict = random.random() < 0.05  # 5% chance of conflict

            return {
                "broker_name": broker_name,
                "sales_agent": sales_agent,
                "has_conflict": has_conflict,
                "conflict_type": "related_party" if has_conflict else None,
                "action_required": "Escalate to compliance" if has_conflict else "None",
                "message": "Conflict detected - broker may be related to sales agent" if has_conflict else "No conflict detected"
            }

    async def process(
        self,
        query: str,
        entities: dict[str, Any],
        deps: Any,
    ) -> dict[str, Any]:
        """
        Process a commission-related query.

        Args:
            query: Natural language query about commissions
            entities: Extracted entities from orchestrator
            deps: Dependencies including security context

        Returns:
            Processing result with commission information
        """
        logger.info(
            "commission_agent_processing",
            query=query[:100],
            entities=entities,
        )

        try:
            result = await self.agent.run(
                f"""Process this commission query: {query}

Extracted entities: {entities}

Please:
1. Identify what commission information is being requested
2. Calculate commission with correct splits if applicable
3. Validate broker RERA number if provided
4. Check for any conflicts of interest
5. Provide the commission status or generate report as needed
"""
            )

            return {
                "status": "success",
                "agent": "commission",
                "result": result.data.dict() if hasattr(result.data, 'dict') else result.data,
                "summary": result.data.summary
            }

        except Exception as e:
            logger.error("commission_processing_error", error=str(e))
            return {
                "status": "error",
                "agent": "commission",
                "error": str(e),
                "summary": "Failed to process commission query"
            }
