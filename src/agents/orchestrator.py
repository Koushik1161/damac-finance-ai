"""
Orchestrator Agent - Routes queries to specialized agents
"""
from typing import Literal, Any
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
import structlog

from ..security.prompt_guard import PromptGuard
from ..security.audit_logger import AuditLogger
from ..observability.metrics import MetricsCollector

logger = structlog.get_logger()


class QueryClassification(BaseModel):
    """Classification result for incoming query"""
    intent: Literal["invoice", "payment", "commission", "general", "unknown"]
    confidence: float = Field(ge=0.0, le=1.0)
    entities: dict[str, Any] = Field(default_factory=dict)
    requires_multi_agent: bool = False
    reasoning: str


class OrchestratorDependencies(BaseModel):
    """Dependencies injected into orchestrator agent"""
    user_id: str
    session_id: str
    prompt_guard: Any  # PromptGuard instance
    audit_logger: Any  # AuditLogger instance
    metrics: Any  # MetricsCollector instance

    class Config:
        arbitrary_types_allowed = True


class OrchestratorAgent:
    """
    Main orchestrator that routes queries to specialized agents.

    Responsibilities:
    - Intent classification
    - Security screening (prompt injection defense)
    - Agent routing
    - Response aggregation
    - Audit logging
    """

    SYSTEM_PROMPT = """You are the orchestrator for DAMAC's Finance Operations AI System.

Your role is to:
1. Understand user queries about finance operations
2. Classify the intent (invoice processing, payment plans, commissions, or general)
3. Extract relevant entities (amounts, dates, project names, vendor names, etc.)
4. Determine if multiple agents are needed for complex queries

DAMAC Context:
- DAMAC is a luxury real estate developer in Dubai
- Projects include: DAMAC Hills, DAMAC Lagoons, Cavalli Tower, AYKON City, etc.
- Payment plans: 1% monthly, 60/40, 80/20, 75/25
- UAE regulations: 4% DLD fee, 5% VAT, 5% retention on construction
- Currency: AED (UAE Dirhams)

Classification Guidelines:
- "invoice": Vendor invoices, purchase orders, payment approvals, construction costs
- "payment": Customer payments, payment plans, milestones, escrow, DLD fees
- "commission": Broker commissions, sales agent payouts, commission splits
- "general": General queries, status updates, reports spanning multiple areas

Always extract:
- Amounts (with currency)
- Dates/periods
- Project names
- Vendor/customer names
- Unit/property references
"""

    def __init__(
        self,
        model: str = "gpt-4o",
        invoice_agent: Any = None,
        payment_agent: Any = None,
        commission_agent: Any = None,
    ):
        self.model = OpenAIModel(model)
        self.invoice_agent = invoice_agent
        self.payment_agent = payment_agent
        self.commission_agent = commission_agent

        # Create classification agent
        self.classifier = Agent(
            model=self.model,
            result_type=QueryClassification,
            system_prompt=self.SYSTEM_PROMPT,
        )

    async def process_query(
        self,
        query: str,
        deps: OrchestratorDependencies,
    ) -> dict[str, Any]:
        """
        Process a user query through the orchestration pipeline.

        Args:
            query: User's natural language query
            deps: Dependencies including security and observability

        Returns:
            Processed response from appropriate agent(s)
        """
        # Step 1: Security screening
        security_result = await deps.prompt_guard.screen_input(query)
        if not security_result.is_safe:
            await deps.audit_logger.log_security_event(
                user_id=deps.user_id,
                event_type="prompt_injection_blocked",
                details=security_result.dict(),
            )
            return {
                "status": "blocked",
                "reason": "Query flagged by security screening",
                "safe_message": "Your query could not be processed. Please rephrase.",
            }

        # Step 2: Classify intent
        with deps.metrics.measure_latency("classification"):
            classification = await self.classifier.run(query)

        logger.info(
            "query_classified",
            intent=classification.data.intent,
            confidence=classification.data.confidence,
            session_id=deps.session_id,
        )

        # Step 3: Route to appropriate agent
        response = await self._route_query(
            query=query,
            classification=classification.data,
            deps=deps,
        )

        # Step 4: Audit log
        await deps.audit_logger.log_query(
            user_id=deps.user_id,
            session_id=deps.session_id,
            query=query,
            classification=classification.data.dict(),
            response_summary=response.get("summary", ""),
        )

        return response

    async def _route_query(
        self,
        query: str,
        classification: QueryClassification,
        deps: OrchestratorDependencies,
    ) -> dict[str, Any]:
        """Route query to appropriate specialized agent"""

        if classification.intent == "invoice" and self.invoice_agent:
            return await self.invoice_agent.process(
                query=query,
                entities=classification.entities,
                deps=deps,
            )

        elif classification.intent == "payment" and self.payment_agent:
            return await self.payment_agent.process(
                query=query,
                entities=classification.entities,
                deps=deps,
            )

        elif classification.intent == "commission" and self.commission_agent:
            return await self.commission_agent.process(
                query=query,
                entities=classification.entities,
                deps=deps,
            )

        elif classification.requires_multi_agent:
            return await self._multi_agent_process(
                query=query,
                classification=classification,
                deps=deps,
            )

        else:
            return {
                "status": "success",
                "intent": classification.intent,
                "message": "Query classified but no specialized handler available",
                "classification": classification.dict(),
            }

    async def _multi_agent_process(
        self,
        query: str,
        classification: QueryClassification,
        deps: OrchestratorDependencies,
    ) -> dict[str, Any]:
        """Handle queries requiring multiple agents"""
        results = {}

        # This would coordinate multiple agents for complex queries
        # For example: "Show me all pending invoices and their impact on cash flow"

        return {
            "status": "success",
            "multi_agent": True,
            "results": results,
        }
