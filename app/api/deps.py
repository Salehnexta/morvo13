from collections.abc import AsyncGenerator
from typing import Dict, Any, List, Optional

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
import uuid as _uuid

from app.core.config.settings import settings
from app.models.user import User
from app.schemas.user import TokenData

engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# Update OAuth2 scheme to support scopes
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token",
    scopes={
        "admin": "Full access to admin operations",
        "user": "Regular user access",
        "agent": "Agent access for automated operations",
    },
)


async def get_current_user(
    security_scopes: SecurityScopes,
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> Dict[str, Any]:
    """
    Get the current user from the token.
    
    Args:
        security_scopes: Security scopes required for the endpoint
        db: Database session
        token: JWT token
        
    Returns:
        User data dictionary
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(sub=user_id, scopes=token_scopes)
    except (JWTError, ValidationError):
        raise credentials_exception
        
    # Check if the required scopes are in the token scopes
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required: {scope}",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    # Return user data from token
    return {
        "id": user_id,
        "email": payload.get("email"),
        "is_active": payload.get("is_active", True),
        "is_superuser": payload.get("is_superuser", False),
        "scopes": token_data.scopes
    }


async def get_current_active_user(
    current_user: Dict[str, Any] = Security(get_current_user, scopes=["user"]),
) -> Dict[str, Any]:
    """
    Get the current active user.
    
    Args:
        current_user: Current user data
        
    Returns:
        Current active user data
    """
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin(
    current_user: Dict[str, Any] = Security(get_current_user, scopes=["admin"]),
) -> Dict[str, Any]:
    """
    Get the current admin user.
    
    Args:
        current_user: Current user data
        
    Returns:
        Current admin user data
    """
    if not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required.",
        )
    return current_user


async def get_current_user_db(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Security(get_current_active_user),
) -> User:
    """
    Get the current user from the database.
    
    Args:
        db: Database session
        current_user: Current user data
        
    Returns:
        User model instance
    """
    try:
        user_id = _uuid.UUID(str(current_user["id"]))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
