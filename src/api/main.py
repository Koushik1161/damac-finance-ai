"""
DAMAC Finance AI - FastAPI Application
Production-grade API for multi-agent finance operations
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog
import time
import uuid

from .routes import router
from ..security.prompt_guard import PromptGuard, RateLimiter
from ..security.pii_handler import PIIHandler
from ..security.audit_logger import AuditLogger, AuditSeverity, AuditEvent, AuditEventType

logger = structlog.get_logger()

# Global instances (would be properly initialized in production)
prompt_guard = PromptGuard(sensitivity="high")
pii_handler = PIIHandler()
audit_logger = AuditLogger()
rate_limiter = RateLimiter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("damac_finance_ai_starting", version="1.0.0")

    # Initialize connections (database, LLM providers, etc.)
    # In production, this would set up:
    # - Azure OpenAI client
    # - PostgreSQL connection pool
    # - Langfuse client
    # - Azure Monitor

    yield

    # Shutdown
    logger.info("damac_finance_ai_shutting_down")


# Create FastAPI application
app = FastAPI(
    title="DAMAC Finance AI",
    description="""
    Multi-Agent AI System for Finance Operations

    ## Features
    - **Invoice Processing**: Automated vendor invoice handling with VAT/retention
    - **Payment Plans**: Customer payment tracking and milestone management
    - **Commission Calculation**: Broker commission with splits and RERA validation

    ## Security
    - Prompt injection defense
    - PII detection and masking
    - Comprehensive audit logging
    - Rate limiting

    ## Compliance
    - UAE VAT (5%) calculation
    - DLD fee (4%) handling
    - RERA escrow compliance
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware (configure for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """
    Middleware for request processing.
    - Adds correlation ID
    - Logs request/response
    - Handles errors
    - Tracks timing
    """
    # Generate correlation ID
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id

    # Get user ID (from auth in production)
    user_id = request.headers.get("X-User-ID", "anonymous")
    request.state.user_id = user_id

    # Start timing
    start_time = time.time()

    # Check rate limit
    is_allowed, reason = await rate_limiter.check_rate_limit(user_id, "query")
    if not is_allowed:
        logger.warning(
            "rate_limit_exceeded",
            user_id=user_id,
            reason=reason,
        )
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "message": reason,
            },
            headers={"X-Correlation-ID": correlation_id},
        )

    try:
        response = await call_next(request)

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Add headers
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Processing-Time-Ms"] = str(duration_ms)

        # Log request
        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            user_id=user_id,
            correlation_id=correlation_id,
        )

        return response

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)

        logger.error(
            "http_request_error",
            method=request.method,
            path=request.url.path,
            error=str(e),
            duration_ms=duration_ms,
            correlation_id=correlation_id,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "An unexpected error occurred",
                "correlation_id": correlation_id,
            },
            headers={"X-Correlation-ID": correlation_id},
        )


# Include routers
app.include_router(router, prefix="/api/v1")


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "service": "damac-finance-ai",
        "version": "1.0.0",
    }


@app.get("/health/ready")
async def readiness_check():
    """
    Readiness check - verifies all dependencies are available.
    """
    checks = {
        "database": True,  # Would check actual DB connection
        "llm_provider": True,  # Would check Azure OpenAI
        "cache": True,  # Would check Redis
    }

    all_ready = all(checks.values())

    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
    }


@app.get("/health/live")
async def liveness_check():
    """Liveness check for container orchestration."""
    return {"status": "alive"}


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "correlation_id": getattr(request.state, "correlation_id", None),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))

    logger.exception(
        "unhandled_exception",
        error=str(exc),
        correlation_id=correlation_id,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred. Please try again.",
            "correlation_id": correlation_id,
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
