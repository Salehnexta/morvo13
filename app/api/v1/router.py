"""Main API router for version 1 of the Morvo API."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, chat, health, onboarding, seranking
# Added diagnostics endpoint
from app.api.v1.endpoints import diagnostics

# Create the main router for the v1 API
api_router = APIRouter()

# Include the individual endpoint routers
api_router.include_router(health.router, tags=["System Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(onboarding.router, prefix="/onboarding", tags=["Onboarding"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(seranking.router, tags=["SE Ranking"])
# Diagnostics
api_router.include_router(diagnostics.router, prefix="", tags=["Diagnostics"])
