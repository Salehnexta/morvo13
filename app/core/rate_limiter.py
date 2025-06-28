"""
Rate limiting middleware and configuration.
"""

from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from typing import Callable, Dict, Optional

from app.core.config.settings import settings
from loguru import logger


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request headers or remote address.
    
    This function checks for X-Forwarded-For, X-Real-IP headers first,
    and falls back to the client's direct IP address.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address as string
    """
    # Try to get IP from X-Forwarded-For header (common with proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, the first one is the client
        return forwarded_for.split(",")[0].strip()
    
    # Try X-Real-IP header (used by some proxies)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct client IP
    return get_remote_address(request)


def get_key_by_path(request: Request) -> str:
    """
    Get rate limit key based on IP and path.
    
    This allows different rate limits for different endpoints.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Key string combining IP and path
    """
    return f"{get_client_ip(request)}:{request.url.path}"


# Create limiter instance with custom key function
limiter = Limiter(
    key_func=get_client_ip,  # Default to IP-based limiting
    default_limits=[f"{settings.RATE_LIMIT_REQUESTS} per {settings.RATE_LIMIT_WINDOW_SECONDS} seconds"],
    storage_uri=settings.REDIS_URL if settings.REDIS_URL else None,  # Use Redis if available
)


# Rate limit handlers for different endpoints
path_limits: Dict[str, str] = {
    "/api/v1/auth/token": "20 per minute",  # Stricter limits for auth endpoints
    "/api/v1/auth/register": "10 per hour",
    "/api/v1/chat": "60 per minute",  # Higher limits for chat
}


def setup_rate_limiting(app: FastAPI) -> None:
    """
    Configure rate limiting for the application.
    
    Args:
        app: FastAPI application instance
    """
    if not settings.ENABLE_RATE_LIMITING:
        logger.info("Rate limiting is disabled")
        return
    
    logger.info(f"Setting up rate limiting: {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW_SECONDS} seconds")
    
    # Add limiter to app state
    app.state.limiter = limiter
    
    # Add exception handler for rate limit exceeded
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
        """
        Custom handler for rate limit exceeded exceptions.
        
        Args:
            request: FastAPI request
            exc: Rate limit exceeded exception
            
        Returns:
            JSON response with rate limit error details
        """
        logger.warning(f"Rate limit exceeded for {get_client_ip(request)}: {request.url.path}")
        return exc.response
    
    logger.info("Rate limiting configured successfully")
