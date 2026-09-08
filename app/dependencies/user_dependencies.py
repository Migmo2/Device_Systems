"""Dependencias reutilizables para las rutas de usuarios."""

from fastapi import HTTPException, Path, status

from app.data.users_db import fake_users_db


def get_user_or_404(user_id: int = Path(..., gt=0, description="ID unico del usuario")):
    user = fake_users_db.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado",
        )
    return user