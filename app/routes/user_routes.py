"""Endpoints CRUD del recurso users."""

from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import database_session
from app.dependencies.auth_dependency import get_current_active_user
from app.core.rate_limit import limiter
from app.dependencies.user_dependencies import get_user_or_404
from app.schemas.user_schema import (
    UserCreate,
    UserListResponse,
    UserPatch,
    UserReplace,
    UserResponse,
)
from app.services.user_service import (
    create_user,
    delete_user,
    email_exists,
    list_users,
    replace_user,
    update_user,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=UserListResponse,
    summary="Listar usuarios",
    description="Retorna usuarios y permite filtrar por rol o estado.",
    response_description="Lista de usuarios encontrados",
)
@limiter.limit("30/minute")
async def get_all_users(
    request: Request,
    role: Optional[Literal["admin", "support", "user"]] = Query(
        None, description="Filtrar por rol"
    ),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(database_session),
    _current_user=Depends(get_current_active_user),
):
    users = list_users(db, role=role, is_active=is_active)
    return UserListResponse(users=users, total=len(users))


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar usuario",
    description="Retorna un usuario por su identificador.",
    response_description="Usuario encontrado",
)
async def get_user_by_id(
    user=Depends(get_user_or_404), _current_user=Depends(get_current_active_user)
):
    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Registra un usuario con correo unico.",
    response_description="Usuario creado",
)
async def create_new_user(user: UserCreate, db: Session = Depends(database_session)):
    user_data = user.model_dump()
    user_data["email"] = str(user_data["email"]).lower()
    if email_exists(db, user_data["email"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El correo '{user.email}' ya esta registrado en el sistema",
        )
    try:
        return create_user(db, user_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El correo ya esta registrado") from None


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Reemplazar usuario",
    description="Reemplaza todos los campos de un usuario existente.",
    response_description="Usuario actualizado completamente",
)
async def replace_existing_user(
    user_data: UserReplace,
    user=Depends(get_user_or_404),
    db: Session = Depends(database_session),
):
    if email_exists(db, str(user_data.email), exclude_user_id=user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El correo '{user_data.email}' ya esta registrado en el sistema",
        )
    return replace_user(db, user.id, user_data.model_dump())


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario parcialmente",
    description="Modifica solo los campos enviados por el cliente.",
    response_description="Usuario actualizado parcialmente",
)
async def patch_existing_user(
    user_data: UserPatch,
    user=Depends(get_user_or_404),
    db: Session = Depends(database_session),
):
    changes = user_data.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe enviar al menos un campo para actualizar",
        )
    if "email" in changes and email_exists(
        db, str(changes["email"]), exclude_user_id=user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El correo '{user_data.email}' ya esta registrado en el sistema",
        )
    return update_user(db, user.id, changes)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar usuario",
    description="Elimina un usuario existente y no retorna contenido.",
    response_description="Usuario eliminado",
)
async def delete_existing_user(
    user=Depends(get_user_or_404), db: Session = Depends(database_session)
):
    delete_user(db, user.id)