"""Main application entry point for the Morvo FastAPI backend."""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from prometheus_client import make_asgi_app
import warnings
import time
from typing import AsyncGenerator, Callable
import uuid

# Import loguru logger directly
from loguru import logger

from app.api.v1.router import api_router
from app.core.cache import init_cache
from app.core.config.settings import settings
from app.core.error_tracking import init_error_tracking
from app.core.rate_limiter import setup_rate_limiting
from app.core.logging import setup_logging
# from app.core.tracing import init_tracing, instrument_fastapi  # New OpenTelemetry integration - DISABLED FOR NOW

# -----------------------------
# Application Factory with Lifespan
# -----------------------------

# Set up logging early
setup_logging()

warnings.filterwarnings(
    "ignore",
    message="Mixing V1 models and V2 models",
    category=UserWarning,
    module="pydantic._internal._generate_schema",
)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None
    """
    # Startup
    logger.info("Starting application...")
    
    # Initialize error tracking
    if settings.ENABLE_ERROR_TRACKING:
        logger.info("Initializing error tracking...")
        init_error_tracking()
    
    # Initialize distributed tracing
    # if settings.ENABLE_TRACING:
    #    logger.info("Initializing distributed tracing...")
    #    init_tracing()
    
    # Initialize cache
    if settings.ENABLE_CACHE:
        logger.info("Initializing cache...")
        await init_cache()
    
    logger.info("Application startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise-grade AI Marketing Platform with Saudi cultural intelligence",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)


# Security middleware
# Add middleware in reverse order of execution (last added = first executed)

# 1. Request ID middleware
@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next: Callable) -> Response:
    """
    Add a unique request ID to each request.
    
    Args:
        request: FastAPI request
        call_next: Next middleware in chain
        
    Returns:
        Response with request ID header
    """
    request_id = str(uuid.uuid4())
    # Add request ID to request state
    request.state.request_id = request_id
    
    # Process the request
    try:
        response = await call_next(request)
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        logger.error(f"Request {request_id} failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "request_id": request_id}
        )


# 2. Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable) -> Response:
    """
    Add processing time header to response.
    
    Args:
        request: FastAPI request
        call_next: Next middleware in chain
        
    Returns:
        Response with processing time header
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# 3. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
    max_age=600,  # 10 minutes
)

# 4. GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 5. Trusted Host middleware
if settings.ENABLE_TRUSTED_HOST_MIDDLEWARE and settings.ALLOWED_HOSTS:
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# 6. HTTPS redirect middleware (only in production)
if settings.ENVIRONMENT == "production" and settings.ENABLE_HTTPS_REDIRECT:
    app.add_middleware(HTTPSRedirectMiddleware)

# 7. Rate limiting middleware
if settings.ENABLE_RATE_LIMITING:
    setup_rate_limiting(app)

# Setup logging
setup_logging()

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount Prometheus metrics endpoint
if settings.ENABLE_METRICS:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Morvo AI Marketing Consultant API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
    }


@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": settings.VERSION}
