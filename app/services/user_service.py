"""Logica de negocio para usuarios persistidos con SQLAlchemy."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_model import User


def list_users(db: Session, role: Optional[str] = None, is_active: Optional[bool] = None):
    query = select(User).order_by(User.id)
    if role is not None:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    return list(db.scalars(query).all())


def email_exists(db: Session, email: str, exclude_user_id: Optional[int] = None) -> bool:
    query = select(User).where(User.email == email.lower())
    if exclude_user_id is not None:
        query = query.where(User.id != exclude_user_id)
    return db.scalar(query) is not None


def create_user(db: Session, user_data: dict) -> User:
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def replace_user(db: Session, user_id: int, user_data: dict) -> User:
    user = db.get(User, user_id)
    for field, value in user_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, user_data: dict) -> User:
    user = db.get(User, user_id)
    for field, value in user_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> None:
    user = db.get(User, user_id)
    db.delete(user)
    db.commit()