"""Reglas de negocio para registro y autenticacion."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import create_access_token, get_password_hash, verify_password
from app.models.user_model import User
from app.schemas.auth_schema import UserRegister


def register_user(db: Session, data: UserRegister) -> User:
    email = str(data.email).lower()
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise ValueError("El correo ya esta registrado")

    user = User(
        name=data.name,
        email=email,
        role=data.role,
        is_active=data.is_active,
        hashed_password=get_password_hash(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email.lower()))
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


def build_access_token(user: User) -> str:
    return create_access_token(str(user.id), user.role)
