# security.py: Password hashing and JWT generation/validation utilities
from datetime import datetime, timedelta, timezone
from typing import Any, Union
import bcrypt
import jwt
from app.config import settings

def hash_password(password: str) -> str:
    """
    Hashes a plain text password using bcrypt.
    """
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against the stored bcrypt hash.
    """
    pwd_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Generates a secure JSON Web Token (JWT) containing user info.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Union[str, None]:
    """
    Decodes and validates a JWT. Returns the subject (email) if valid, or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except (jwt.PyJWTError, AttributeError):
        return None
