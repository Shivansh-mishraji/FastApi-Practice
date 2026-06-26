# dependencies.py: Reusable route dependencies (auth, database, etc.)
from typing import AsyncGenerator
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_async_session
from app.models import User
from app.security import decode_access_token
from app.exceptions import AuthenticationFailedException, AccessDeniedException

# OAuth2PasswordBearer extracts the bearer token from the Authorization header.
# tokenUrl specifies where client can request a token (swagger uses this for Auth button)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_session)
) -> User:
    """
    FastAPI dependency that extracts the JWT token from the headers,
    verifies it, and returns the current authenticated User.
    Raises AuthenticationFailedException if validation fails.
    """
    email = decode_access_token(token)
    if not email:
        raise AuthenticationFailedException("Could not validate credentials or token expired")
    
    # Query database asynchronously to find the user
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise AuthenticationFailedException("User not found in system")
    
    return user

async def get_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Sub-dependency that ensures the authenticated user is currently active.
    """
    if not current_user.is_active:
        raise AccessDeniedException("User account is inactive")
    return current_user
