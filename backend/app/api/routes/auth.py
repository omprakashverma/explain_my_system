from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

from backend.app.api.dependencies import bearer_scheme, require_current_user
from backend.app.models.request_models import LoginRequest, RegisterRequest
from backend.app.models.response_models import AuthResponse, UserResponse
from backend.app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest) -> dict[str, object]:
    return auth_service.register(req.username, req.password, req.email)


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest) -> dict[str, object]:
    return auth_service.login(req.username, req.password)


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict[str, bool]:
    if credentials and credentials.credentials:
        auth_service.logout(credentials.credentials)
    return {"success": True}


@router.get("/me", response_model=UserResponse)
async def me(current_user: dict[str, object] = Depends(require_current_user)) -> dict[str, object]:
    return current_user
