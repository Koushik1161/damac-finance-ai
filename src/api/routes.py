"""
DAMAC Finance AI - API Routes
Endpoints powered by GPT-5 for intelligent finance operations
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
import uuid
import time
import structlog

from ..llm import (
    OrchestratorLLMAgent,
    InvoiceLLMAgent,
    PaymentLLMAgent,
    CommissionLLMAgent,
)

logger = structlog.get_logger()
router = APIRouter(tags=["Finance AI"])

# Initialize LLM agents
orchestrator = OrchestratorLLMAgent()
invoice_agent = InvoiceLLMAgent()
payment_agent = PaymentLLMAgent()
commission_agent = CommissionLLMAgent()


# Request/Response Models

class QueryRequest(BaseModel):
    """Request model for AI query"""
    query: str = Field(..., min_length=1, max_length=5000, description="Natural language query")
    context: Optional[dict] = Field(default=None, description="Additional context")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Process the invoice from Al Habtoor Engineering for AED 850,000 for MEP works at DAMAC Hills 2",
                "context": {"project": "DAMAC Hills 2"}
            }
        }


class QueryResponse(BaseModel):
    """Response model for AI query"""
    request_id: str
    status: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    agent: Optional[str] = None
    result: Optional[dict] = None
    entities: Optional[dict] = None
    processing_time_ms: int
    model: Optional[str] = None


class InvoiceRequest(BaseModel):
    """Request model for invoice processing"""
    vendor_name: str
    invoice_number: Optional[str] = None
    amount: float = Field(..., gt=0)
    project_name: str
    description: Optional[str] = None
    po_number: Optional[str] = None
    vendor_trn: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "vendor_name": "Al Habtoor Engineering",
                "invoice_number": "INV-2024-001234",
                "amount": 850000,
                "project_name": "DAMAC Hills 2",
                "description": "MEP works - Phase 1",
                "po_number": "PO-78901",
                "vendor_trn": "100123456789012"
            }
        }


class CommissionRequest(BaseModel):
    """Request model for commission calculation"""
    sale_price: float = Field(..., gt=0)
    broker_name: str
    broker_brn: str
    project_name: str
    unit_id: Optional[str] = None
    commission_rate: float = Field(default=5.0, ge=0, le=10)


# Dependency injection

async def get_current_user(request: Request) -> dict:
    """Extract current user from request."""
    return {
        "user_id": getattr(request.state, "user_id", "anonymous"),
        "role": "manager",
        "permissions": ["read", "write", "approve"],
    }


# Routes

@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    http_request: Request,
    user: dict = Depends(get_current_user),
):
    """
    Process a natural language finance query using GPT-5.

    The orchestrator classifies the query and routes it to the appropriate
    specialized agent (invoice, payment, or commission).

    **Examples:**
    - "What's the payment status for unit DAMAC-CAV-2501?"
    - "Calculate commission for the AED 4.5M sale at Safa One"
    - "Process the invoice from Al Habtoor for AED 850,000"
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())

    logger.info(
        "query_received",
        request_id=request_id,
        query_preview=request.query[:100],
        user_id=user["user_id"],
    )

    try:
        # Step 1: Classify intent using orchestrator
        classification = await orchestrator.classify(request.query)

        intent = classification.get("intent", "general")
        confidence = classification.get("confidence", 0.0)
        entities = classification.get("entities", {})

        # Step 2: Route to appropriate agent
        if intent == "invoice":
            result = await invoice_agent.process(request.query, entities)
            agent_name = "invoice"
        elif intent == "payment":
            result = await payment_agent.process(request.query, entities)
            agent_name = "payment"
        elif intent == "commission":
            result = await commission_agent.process(request.query, entities)
            agent_name = "commission"
        else:
            result = {
                "message": "General query received",
                "suggestion": "Please ask about invoices, payment plans, or commissions.",
                "examples": [
                    "Process invoice from [vendor] for AED [amount]",
                    "Check payment status for [property] on [plan] plan",
                    "Calculate commission for AED [amount] sale"
                ]
            }
            agent_name = "orchestrator"

        processing_time = int((time.time() - start_time) * 1000)

        logger.info(
            "query_processed",
            request_id=request_id,
            intent=intent,
            agent=agent_name,
            processing_time_ms=processing_time,
        )

        return QueryResponse(
            request_id=request_id,
            status="success",
            intent=intent,
            confidence=confidence,
            agent=agent_name,
            result=result,
            entities=entities,
            processing_time_ms=processing_time,
            model="gpt-5-mini",
        )

    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        logger.error("query_error", request_id=request_id, error=str(e))

        return QueryResponse(
            request_id=request_id,
            status="error",
            result={"error": str(e)},
            processing_time_ms=processing_time,
        )


@router.post("/invoices/process")
async def process_invoice(
    request: InvoiceRequest,
    user: dict = Depends(get_current_user),
):
    """
    Process a vendor invoice using GPT-5 AI.

    Automatically:
    - Validates TRN format
    - Calculates VAT (5%) and retention (5%)
    - Determines approval workflow
    - Provides recommendations
    """
    start_time = time.time()

    # Build query from structured input
    query = f"""Process invoice:
- Vendor: {request.vendor_name}
- Amount: AED {request.amount:,.2f}
- Project: {request.project_name}
- Description: {request.description or 'Not provided'}
- PO Number: {request.po_number or 'Not provided'}
- Vendor TRN: {request.vendor_trn or 'Not provided'}
- Invoice Number: {request.invoice_number or 'Not provided'}"""

    entities = {
        "vendor_name": request.vendor_name,
        "amount": request.amount,
        "project_name": request.project_name,
        "vendor_trn": request.vendor_trn,
        "po_number": request.po_number,
    }

    result = await invoice_agent.process(query, entities)
    processing_time = int((time.time() - start_time) * 1000)

    return {
        "status": "success",
        "processing_time_ms": processing_time,
        "model": "gpt-5-mini",
        "result": result,
    }


@router.post("/payments/query")
async def query_payment_plan(
    query: str,
    property_value: Optional[float] = None,
    plan_type: Optional[str] = None,
    project_name: Optional[str] = None,
    user: dict = Depends(get_current_user),
):
    """
    Query payment plan information using GPT-5 AI.

    Provide natural language query or structured parameters.
    """
    start_time = time.time()

    entities = {}
    if property_value:
        entities["property_value"] = property_value
    if plan_type:
        entities["plan_type"] = plan_type
    if project_name:
        entities["project_name"] = project_name

    result = await payment_agent.process(query, entities)
    processing_time = int((time.time() - start_time) * 1000)

    return {
        "status": "success",
        "processing_time_ms": processing_time,
        "model": "gpt-5-mini",
        "result": result,
    }


@router.post("/commissions/calculate")
async def calculate_commission(
    request: CommissionRequest,
    user: dict = Depends(get_current_user),
):
    """
    Calculate broker commission using GPT-5 AI.

    Includes:
    - Gross commission calculation
    - VAT (5%) calculation
    - Split between external broker and internal sales
    - RERA broker validation
    """
    start_time = time.time()

    query = f"""Calculate commission:
- Sale Price: AED {request.sale_price:,.2f}
- Project: {request.project_name}
- Broker: {request.broker_name}
- Broker BRN: {request.broker_brn}
- Commission Rate: {request.commission_rate}%
- Unit: {request.unit_id or 'Not specified'}"""

    entities = {
        "sale_price": request.sale_price,
        "broker_name": request.broker_name,
        "broker_brn": request.broker_brn,
        "project_name": request.project_name,
        "commission_rate": request.commission_rate,
    }

    result = await commission_agent.process(query, entities)
    processing_time = int((time.time() - start_time) * 1000)

    return {
        "status": "success",
        "processing_time_ms": processing_time,
        "model": "gpt-5-mini",
        "result": result,
    }


@router.get("/reports/financial-summary")
async def get_financial_summary(
    period: str = "month",
    user: dict = Depends(get_current_user),
):
    """
    Get financial summary report.
    Note: This endpoint uses mock data for demonstration.
    """
    import random

    multiplier = {"day": 1, "week": 7, "month": 30, "quarter": 90}.get(period, 30)

    return {
        "period": period,
        "generated_at": datetime.utcnow().isoformat(),
        "note": "Mock data for demonstration",
        "invoices": {
            "processed": random.randint(10, 50) * (multiplier // 7 + 1),
            "total_amount_aed": round(random.uniform(5000000, 50000000) * (multiplier / 30), 2),
            "pending_approval": random.randint(5, 20),
        },
        "payments": {
            "received": random.randint(20, 100) * (multiplier // 7 + 1),
            "total_amount_aed": round(random.uniform(10000000, 100000000) * (multiplier / 30), 2),
        },
        "commissions": {
            "calculated": random.randint(10, 40) * (multiplier // 7 + 1),
            "total_amount_aed": round(random.uniform(1000000, 10000000) * (multiplier / 30), 2),
        },
    }


@router.get("/health/llm")
async def llm_health_check():
    """Check LLM connection health."""
    try:
        from ..llm.client import get_llm_client
        client = get_llm_client()

        # Quick test
        result = client.chat_completion(
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=50,
        )

        return {
            "status": "healthy",
            "orchestrator_model": client.orchestrator_model,
            "agent_model": client.agent_model,
            "test_response": result,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }
