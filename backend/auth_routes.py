"""
Authentication routes for user registration and login.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import sqlite3
import traceback
from database import db
from auth import get_password_hash, verify_password, create_access_token, verify_token

router = APIRouter()
security = HTTPBearer()


class RegisterRequest(BaseModel):
    """Model for user registration."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password (min 6 characters)")
    name: Optional[str] = Field(None, description="User name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123",
                "name": "John Doe"
            }
        }


class LoginRequest(BaseModel):
    """Model for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "password123"
            }
        }


class AuthResponse(BaseModel):
    """Model for authentication response."""
    user_id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: Optional[str] = Field(None, description="User name")
    token: str = Field(..., description="JWT access token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "email": "user@example.com",
                "name": "John Doe",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email from database."""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, password_hash, name, expo_push_token
                FROM users
                WHERE email = ?
            """, (email,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None


def create_user(email: str, password_hash: str, name: Optional[str] = None) -> Optional[int]:
    """Create a new user in the database."""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (email, password_hash, name)
                VALUES (?, ?, ?)
            """, (email, password_hash, name or email.split('@')[0]))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        # Email already exists
        print(f"Integrity error creating user: {e}")
        return None
    except Exception as e:
        import traceback
        print(f"Error creating user: {e}")
        traceback.print_exc()
        return None


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """
    Register a new user.
    
    Args:
        request: Registration request with email, password, and optional name
        
    Returns:
        AuthResponse with user_id, email, name, and JWT token
    """
    try:
        # Check if user already exists
        existing_user = get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = get_password_hash(request.password)
        
        # Create user
        user_id = create_user(request.email, password_hash, request.name)
        
        if not user_id:
            # Check if it failed due to duplicate email (race condition)
            existing_user = get_user_by_email(request.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user. Please try again."
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user_id)})
        
        return AuthResponse(
            user_id=user_id,
            email=request.email,
            name=request.name,
            token=access_token
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in register: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login an existing user.
    
    Args:
        request: Login request with email and password
        
    Returns:
        AuthResponse with user_id, email, name, and JWT token
    """
    # Get user from database
    user = get_user_by_email(request.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user["id"])})
    
    return AuthResponse(
        user_id=user["id"],
        email=user["email"],
        name=user.get("name"),
        token=access_token
    )


@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current authenticated user information.
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        
    Returns:
        User information
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Convert to int (token stores as string)
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    
    # Get user from database
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, email, name, expo_push_token
                FROM users
                WHERE id = ?
            """, (user_id_int,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user: {str(e)}"
        )


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    Dependency to get current user ID from JWT token.
    Use this in protected routes.
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        
    Returns:
        User ID (int)
        
    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    try:
        # HTTPBearer should have already validated the Authorization header exists
        token = credentials.credentials
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        payload = verify_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Convert to int (token stores as string)
        try:
            return int(user_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any unexpected errors and convert to HTTPException
        print(f"Unexpected error in get_current_user_id: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )

