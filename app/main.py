"""Main application entry point for the Morvo FastAPI backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.router import api_router
from app.core.cache import init_cache
from app.core.config.settings import settings
from app.core.error_tracking import init_error_tracking
from app.core.rate_limiter import setup_rate_limiting

# -----------------------------
# Application Factory with Lifespan
# -----------------------------


def create_app() -> FastAPI:
    """Application factory that sets up the FastAPI app with lifespan events."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):  # pragma: no cover -- simple setup code
        # Initialize shared resources on startup
        await init_cache()
        setup_rate_limiting(app)
        yield
        # Place for graceful teardown logic if needed

    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    # Initialize error tracking as early as possible
    init_error_tracking(app)

    # Set up CORS middleware
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include the main API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/", tags=["Root"])
    async def read_root() -> dict[str, str]:
        """A simple root endpoint to confirm the API is running."""
        return {"message": "Welcome to the Morvo AI Marketing Platform API"}

    return app


# Instantiate the application for ASGI servers & tests
app: FastAPI = create_app()
