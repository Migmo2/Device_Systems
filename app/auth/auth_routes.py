"""Registro, login y usuario autenticado."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import create_access_token, get_password_hash, verify_password
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
    if db.scalar(select(User).where(User.email == str(data.email).lower())) is not None:
        raise HTTPException(status_code=400, detail="El correo ya esta registrado")
    user = User(
        name=data.name,
        email=str(data.email).lower(),
        role=data.role,
        is_active=data.is_active,
        hashed_password=get_password_hash(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token, summary="Iniciar sesion")
@limiter.limit("5/minute")
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database_session),
):
    user = db.scalar(select(User).where(User.email == form_data.username.lower()))
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    return Token(access_token=create_access_token(str(user.id), user.role))


@router.get("/me", response_model=AuthUserResponse, summary="Consultar usuario autenticado")
async def read_current_user(user: User = Depends(get_current_active_user)):
    return user
