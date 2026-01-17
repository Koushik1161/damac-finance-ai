"""
Payment Plan Agent - Manages customer payment schedules
"""
from typing import Any, Optional
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
import structlog

logger = structlog.get_logger()

# Dubai Land Department Constants
DLD_FEE_RATE = Decimal("0.04")  # 4% DLD fee
ADMIN_FEE = Decimal("4200")  # Standard admin fee
OQOOD_RATE_PER_SQFT = Decimal("40")  # AED 40 per sqft for off-plan


class PaymentPlanType(BaseModel):
    """Payment plan configuration"""
    name: str  # e.g., "60/40", "1% Monthly"
    construction_percent: Decimal
    handover_percent: Decimal
    is_monthly: bool = False
    description: str


class MilestonePayment(BaseModel):
    """Individual milestone payment"""
    milestone_number: int
    description: str
    percentage: Decimal
    amount_aed: Decimal
    due_date: Optional[date] = None
    status: str = "pending"  # pending, due, paid, overdue
    paid_date: Optional[date] = None
    paid_amount: Optional[Decimal] = None


class PaymentPlanStatus(BaseModel):
    """Complete payment plan status"""
    transaction_id: str
    customer_name: str
    property_unit: str
    project_name: str
    plan_type: str
    property_price_aed: Decimal
    total_fees_aed: Decimal
    grand_total_aed: Decimal
    total_paid_aed: Decimal
    total_pending_aed: Decimal
    payment_progress_percent: Decimal
    milestones: list[MilestonePayment]
    next_due: Optional[MilestonePayment] = None
    overdue_amount: Decimal = Decimal("0")


class EscrowTransaction(BaseModel):
    """RERA-compliant escrow transaction"""
    escrow_id: str
    rera_account: str
    transaction_type: str  # "inward", "outward"
    amount_aed: Decimal
    date: date
    reference: str
    narration: str
    balance_after: Decimal


class PaymentProcessingResult(BaseModel):
    """Result of payment query processing"""
    query_type: str  # "status", "upcoming", "overdue", "escrow", "statement"
    payment_status: Optional[PaymentPlanStatus] = None
    escrow_transactions: Optional[list[EscrowTransaction]] = None
    summary: str
    recommendations: list[str] = Field(default_factory=list)


# Predefined payment plans
PAYMENT_PLANS = {
    "60/40": PaymentPlanType(
        name="60/40",
        construction_percent=Decimal("60"),
        handover_percent=Decimal("40"),
        description="60% during construction, 40% on handover"
    ),
    "80/20": PaymentPlanType(
        name="80/20",
        construction_percent=Decimal("80"),
        handover_percent=Decimal("20"),
        description="80% during construction, 20% on handover"
    ),
    "75/25": PaymentPlanType(
        name="75/25",
        construction_percent=Decimal("75"),
        handover_percent=Decimal("25"),
        description="75% during construction, 25% on handover"
    ),
    "50/50": PaymentPlanType(
        name="50/50",
        construction_percent=Decimal("50"),
        handover_percent=Decimal("50"),
        description="50% during construction, 50% on handover"
    ),
    "1% Monthly": PaymentPlanType(
        name="1% Monthly",
        construction_percent=Decimal("60"),
        handover_percent=Decimal("40"),
        is_monthly=True,
        description="1% monthly during construction, 40% on handover"
    ),
}


class PaymentPlanAgent:
    """
    Specialized agent for managing customer payment schedules.

    Capabilities:
    - Track payment plan progress
    - Calculate milestone payments
    - Generate payment reminders
    - Process escrow transactions
    - Handle DLD fee calculations
    """

    SYSTEM_PROMPT = """You are a specialized payment plan agent for DAMAC Properties.

Your responsibilities:
1. Track customer payment plan progress
2. Calculate milestone amounts and due dates
3. Identify overdue payments
4. Process and track escrow transactions
5. Generate payment statements

DAMAC Payment Plans:
- 1% Monthly: 1% per month during construction (60%), 40% on handover
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
- 5% retention held in escrow for defects liability period

Payment Process:
1. Booking (10% typically)
2. SPA Signing
3. Construction Milestones (based on plan)
4. Handover Payment
5. DLD Registration
6. Snagging Period (defects liability)

When querying payment status:
- Show total paid vs. pending
- Highlight any overdue amounts
- List upcoming due dates
- Calculate payment progress percentage
"""

    def __init__(self, model: str = "gpt-4o"):
        self.model = OpenAIModel(model)

        self.agent = Agent(
            model=self.model,
            result_type=PaymentProcessingResult,
            system_prompt=self.SYSTEM_PROMPT,
        )

        self._register_tools()

    def _register_tools(self):
        """Register tools for payment plan agent"""

        @self.agent.tool
        async def calculate_dld_fees(
            ctx: RunContext,
            property_value: float,
            area_sqft: float,
            is_offplan: bool = True
        ) -> dict:
            """Calculate DLD registration fees"""
            prop_value = Decimal(str(property_value))
            area = Decimal(str(area_sqft))

            dld_fee = prop_value * DLD_FEE_RATE
            oqood_fee = area * OQOOD_RATE_PER_SQFT if is_offplan else Decimal("0")
            admin_fee = ADMIN_FEE

            total_fees = dld_fee + oqood_fee + admin_fee

            return {
                "property_value_aed": float(prop_value),
                "dld_fee_rate": float(DLD_FEE_RATE),
                "dld_fee_aed": float(dld_fee),
                "oqood_fee_aed": float(oqood_fee) if is_offplan else 0,
                "admin_fee_aed": float(admin_fee),
                "total_fees_aed": float(total_fees),
                "is_offplan": is_offplan,
            }

        @self.agent.tool
        async def get_payment_plan_details(
            ctx: RunContext,
            plan_name: str
        ) -> dict:
            """Get payment plan structure details"""
            plan = PAYMENT_PLANS.get(plan_name)
            if not plan:
                return {
                    "error": f"Unknown plan: {plan_name}",
                    "available_plans": list(PAYMENT_PLANS.keys())
                }

            return {
                "name": plan.name,
                "construction_percent": float(plan.construction_percent),
                "handover_percent": float(plan.handover_percent),
                "is_monthly": plan.is_monthly,
                "description": plan.description,
            }

        @self.agent.tool
        async def calculate_milestone_schedule(
            ctx: RunContext,
            property_value: float,
            plan_name: str,
            spa_date: str,
            expected_handover: str
        ) -> dict:
            """Generate milestone payment schedule"""
            plan = PAYMENT_PLANS.get(plan_name)
            if not plan:
                return {"error": f"Unknown plan: {plan_name}"}

            prop_value = Decimal(str(property_value))
            construction_amount = prop_value * (plan.construction_percent / 100)
            handover_amount = prop_value * (plan.handover_percent / 100)

            milestones = []

            # Booking (always 10%)
            milestones.append({
                "milestone": 1,
                "description": "Booking Amount",
                "percentage": 10,
                "amount_aed": float(prop_value * Decimal("0.10")),
                "timing": "On booking"
            })

            if plan.is_monthly:
                # 1% monthly plan
                monthly_percent = 1
                monthly_amount = prop_value * Decimal("0.01")
                num_months = int((plan.construction_percent - 10) / monthly_percent)

                for i in range(num_months):
                    milestones.append({
                        "milestone": i + 2,
                        "description": f"Monthly Installment {i + 1}",
                        "percentage": monthly_percent,
                        "amount_aed": float(monthly_amount),
                        "timing": f"Month {i + 1} after SPA"
                    })
            else:
                # Milestone-based plan
                remaining_construction = plan.construction_percent - 10
                num_milestones = 5  # Typical construction milestones
                per_milestone = remaining_construction / num_milestones

                milestone_names = [
                    "Foundation Complete",
                    "Structure Complete (50%)",
                    "Structure Complete (100%)",
                    "MEP Rough-in",
                    "Interior Finishing"
                ]

                for i, name in enumerate(milestone_names):
                    milestones.append({
                        "milestone": i + 2,
                        "description": name,
                        "percentage": float(per_milestone),
                        "amount_aed": float(prop_value * (per_milestone / 100)),
                        "timing": f"Construction Phase {i + 1}"
                    })

            # Handover payment
            milestones.append({
                "milestone": len(milestones) + 1,
                "description": "Handover Payment",
                "percentage": float(plan.handover_percent),
                "amount_aed": float(handover_amount),
                "timing": "On handover"
            })

            return {
                "plan_name": plan_name,
                "property_value_aed": float(prop_value),
                "total_milestones": len(milestones),
                "milestones": milestones,
                "construction_total_aed": float(construction_amount),
                "handover_total_aed": float(handover_amount),
            }

        @self.agent.tool
        async def query_payment_status(
            ctx: RunContext,
            transaction_id: str
        ) -> dict:
            """Query payment status for a transaction (mock)"""
            # In production, this would query the CRM/ERP system
            import random

            total_value = random.uniform(1500000, 5000000)
            paid_percent = random.uniform(20, 80)
            paid_amount = total_value * (paid_percent / 100)
            pending_amount = total_value - paid_amount

            return {
                "transaction_id": transaction_id,
                "property_value_aed": round(total_value, 2),
                "total_paid_aed": round(paid_amount, 2),
                "total_pending_aed": round(pending_amount, 2),
                "progress_percent": round(paid_percent, 1),
                "status": "on_track" if paid_percent >= 50 else "needs_attention",
                "next_due_date": "2024-03-15",
                "next_due_amount": round(total_value * 0.10, 2),
                "overdue_amount": 0 if random.random() > 0.3 else round(total_value * 0.05, 2)
            }

        @self.agent.tool
        async def get_escrow_balance(
            ctx: RunContext,
            project_name: str
        ) -> dict:
            """Get escrow account balance for a project (mock)"""
            import random

            return {
                "project_name": project_name,
                "rera_escrow_account": f"RERA-ESC-{random.randint(10000, 99999)}",
                "current_balance_aed": round(random.uniform(10000000, 500000000), 2),
                "inward_this_month_aed": round(random.uniform(1000000, 20000000), 2),
                "outward_this_month_aed": round(random.uniform(500000, 15000000), 2),
                "pending_contractor_payments_aed": round(random.uniform(2000000, 30000000), 2),
                "last_updated": datetime.now().isoformat()
            }

    async def process(
        self,
        query: str,
        entities: dict[str, Any],
        deps: Any,
    ) -> dict[str, Any]:
        """
        Process a payment-related query.

        Args:
            query: Natural language query about payments
            entities: Extracted entities from orchestrator
            deps: Dependencies including security context

        Returns:
            Processing result with payment information
        """
        logger.info(
            "payment_agent_processing",
            query=query[:100],
            entities=entities,
        )

        try:
            result = await self.agent.run(
                f"""Process this payment plan query: {query}

Extracted entities: {entities}

Please:
1. Identify what payment information is being requested
2. Calculate relevant fees (DLD, admin, Oqood if applicable)
3. Show payment progress if transaction ID is available
4. Highlight any overdue amounts
5. Provide recommendations for next steps
"""
            )

            return {
                "status": "success",
                "agent": "payment",
                "result": result.data.dict() if hasattr(result.data, 'dict') else result.data,
                "summary": result.data.summary
            }

        except Exception as e:
            logger.error("payment_processing_error", error=str(e))
            return {
                "status": "error",
                "agent": "payment",
                "error": str(e),
                "summary": "Failed to process payment query"
            }
