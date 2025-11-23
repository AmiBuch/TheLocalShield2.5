"""
Authentication utilities for JWT tokens and password hashing.
"""

from datetime import datetime, timedelta
from typing import Optional
import hashlib
import bcrypt
from jose import JWTError, jwt
from fastapi import HTTPException, status

# Secret key for JWT (in production, use environment variable)
SECRET_KEY = "your-secret-key-change-this-in-production-min-32-chars"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def _pre_hash_password(password: str) -> bytes:
    """
    Pre-hash password with SHA256 to handle bcrypt's 72-byte limit.
    Returns binary digest (32 bytes) which is well under the 72-byte limit.
    This allows passwords of any length while maintaining security.
    """
    return hashlib.sha256(password.encode('utf-8')).digest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    Handles bcrypt's 72-byte limit by pre-hashing with SHA256.
    """
    # Pre-hash the password to handle long passwords (32 bytes binary)
    pre_hashed_bytes = _pre_hash_password(plain_password)
    # Verify using bcrypt directly
    try:
        return bcrypt.checkpw(pre_hashed_bytes, hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    Handles bcrypt's 72-byte limit by pre-hashing with SHA256.
    """
    # Pre-hash the password to handle long passwords (32 bytes binary)
    pre_hashed_bytes = _pre_hash_password(password)
    # Hash using bcrypt directly (generates salt automatically)
    hashed = bcrypt.hashpw(pre_hashed_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> Optional[int]:
    """Extract user_id from JWT token."""
    payload = verify_token(token)
    if payload:
        return payload.get("sub")  # 'sub' is the user_id in the token
    return None

