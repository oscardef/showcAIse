from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sys
sys.path.append('/app')

from shared.auth import create_access_token

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login endpoint - simplified for MVP."""
    # TODO: Implement proper authentication
    # For now, just return a token
    token = create_access_token({"sub": request.email})
    return TokenResponse(access_token=token)


@router.post("/register", response_model=TokenResponse)
async def register(request: LoginRequest):
    """Register endpoint - simplified for MVP."""
    # TODO: Implement proper registration
    token = create_access_token({"sub": request.email})
    return TokenResponse(access_token=token)
