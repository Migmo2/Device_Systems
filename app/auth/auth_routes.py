"""Registro, login y usuario autenticado."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.auth_service import (
    authenticate_user,
    build_access_token,
    register_user as register_user_service,
)
from app.core.rate_limit import limiter
from app.dependencies.database_dependency import database_session
from app.dependencies.auth_dependency import get_current_active_user
from app.models.user_model import User
from app.schemas.auth_schema import AuthUserResponse, Token, UserRegister

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthUserResponse, status_code=201, summary="Registrar usuario")
@limiter.limit("3/minute")
async def register_user(
    request: Request, data: UserRegister, db: Session = Depends(database_session)
):
    try:
        return register_user_service(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None


@router.post("/login", response_model=Token, summary="Iniciar sesion")
@limiter.limit("5/minute")
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database_session),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    return Token(access_token=build_access_token(user))


@router.get("/me", response_model=AuthUserResponse, summary="Consultar usuario autenticado")
async def read_current_user(user: User = Depends(get_current_active_user)):
    return user
