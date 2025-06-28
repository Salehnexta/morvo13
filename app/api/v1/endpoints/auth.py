"""
Authentication endpoints for user registration, login, and token management.
"""

from datetime import timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user, get_current_admin, get_current_user_db
from app.core.config.settings import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserPublic

router = APIRouter()


@router.post("/register", response_model=UserPublic)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Register a new user.
    
    Args:
        user_in: User creation data
        db: Database session
        
    Returns:
        Created user
    """
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email, 
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.post("/token", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    Args:
        db: Database session
        form_data: OAuth2 form data with username and password
        
    Returns:
        Access token
    """
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )
    
    # Determine user scopes
    scopes = ["user"]
    if user.is_superuser:
        scopes.append("admin")
    
    # Create access token with appropriate scopes
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Include additional user info in token
    extra_claims = {
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser
    }
    
    return Token(
        access_token=create_access_token(
            subject=str(user.id), 
            scopes=scopes,
            expires_delta=access_token_expires,
            extra_claims=extra_claims
        ),
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope=" ".join(scopes)
    )


@router.post("/login/access-token", response_model=Token)
async def legacy_login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """
    Legacy endpoint for backward compatibility.
    """
    return await login_access_token(db=db, form_data=form_data)


@router.get("/users/me", response_model=UserPublic)
async def read_users_me(
    current_user: User = Depends(get_current_user_db),
) -> User:
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user data
    """
    return current_user


@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    current_user_data: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Refresh access token.
    
    Args:
        current_user_data: Current authenticated user data
        db: Database session
        
    Returns:
        New access token
    """
    try:
        user_id = current_user_data["id"]
    except (KeyError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token data",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user or inactive account",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Determine user scopes
    scopes = ["user"]
    if user.is_superuser:
        scopes.append("admin")
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Include additional user info in token
    extra_claims = {
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser
    }
    
    return Token(
        access_token=create_access_token(
            subject=str(user.id), 
            scopes=scopes,
            expires_delta=access_token_expires,
            extra_claims=extra_claims
        ),
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope=" ".join(scopes)
    )
