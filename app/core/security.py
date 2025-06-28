"""
Security utilities for authentication and authorization.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from app.core.config.settings import settings
from loguru import logger

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme configuration
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token",
    scopes={
        "admin": "Full access to admin operations",
        "user": "Regular user access",
        "agent": "Agent access for automated operations",
    },
)


class TokenData(BaseModel):
    """Schema for decoded token data."""
    sub: str
    scopes: List[str] = []
    exp: Optional[datetime] = None
    jti: Optional[str] = None  # JWT ID for token revocation tracking


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if the password matches the hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], 
    scopes: List[str] = None,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: Token subject (usually user ID)
        scopes: Token scopes
        expires_delta: Token expiration time
        extra_claims: Additional claims to include in the token
        
    Returns:
        JWT token as string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Create payload with standard claims
    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "scopes": scopes or []
    }
    
    # Add any extra claims
    if extra_claims:
        payload.update(extra_claims)
    
    # Create and return the token
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


# These functions are now implemented in app/api/deps.py
# They are kept here for reference and backward compatibility
get_current_user = None
get_current_active_user = None
get_current_admin = None
