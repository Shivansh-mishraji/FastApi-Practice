# routes/auth.py: Authentication routes (register, login)
from datetime import timedelta
from fastapi import APIRouter, Depends, BackgroundTasks, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_async_session
from app.models import User
from app.schemas import UserCreate, UserResponse, Token
from app.security import hash_password, verify_password, create_access_token
from app.config import settings
from app.exceptions import DuplicateEntityException, AuthenticationFailedException

router = APIRouter(prefix="/auth", tags=["Authentication"])

def simulate_send_welcome_email(email: str):
    """
    Dummy email sender function executed in a background task
    to showcase asynchronous background task processing.
    """
    import time
    time.sleep(2)  # Simulate email delay
    print(f"[BACKGROUND TASK] Welcome email successfully sent to {email}!")

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Register a new user:
    - Checks if the email is already in use.
    - Hashes the password.
    - Creates the user in the database.
    - Runs a background task to send a welcome email.
    """
    # Check if user already exists
    query = select(User).where(User.email == user_in.email)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise DuplicateEntityException("A user with this email is already registered.")

    # Create new user
    hashed_pwd = hash_password(user_in.password)
    new_user = User(email=user_in.email, hashed_password=hashed_pwd)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Queue background task (simulates asynchronous email)
    background_tasks.add_task(simulate_send_welcome_email, new_user.email)

    return new_user

@router.post(
    "/token",
    response_model=Token,
    summary="Login and receive an Access Token"
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session)
):
    """
    OAuth2 compatible token login:
    - Standard username (email) and password inputs.
    - Verifies password hashes.
    - Returns JWT Bearer token if successful.
    """
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise AuthenticationFailedException("Incorrect email or password")

    # Generate JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
