"""Dependencias reutilizables para las rutas de usuarios."""

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import database_session
from app.models.user_model import User


def get_user_or_404(
    user_id: int = Path(..., gt=0, description="ID unico del usuario"),
    db: Session = Depends(database_session),
) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado",
        )
    return user