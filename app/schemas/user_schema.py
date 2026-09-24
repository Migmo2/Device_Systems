"""
Esquemas de validación de usuarios con Pydantic v2
"""
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, Literal


class UserBase(BaseModel):
    """Modelo base con campos comunes"""
    name: str = Field(
        ..., 
        min_length=3, 
        max_length=100,
        description="Nombre del usuario (mínimo 3 caracteres)"
    )
    email: EmailStr = Field(
        ..., 
        description="Correo electrónico válido del usuario"
    )
    role: Literal["admin", "support", "user"] = Field(
        default="user",
        description="Rol del usuario: admin, support o user"
    )
    is_active: bool = Field(
        default=True,
        description="Estado del usuario (activo/inactivo)"
    )


class UserCreate(UserBase):
    """Modelo para crear un nuevo usuario"""
    pass


class UserReplace(BaseModel):
    """Modelo para reemplazar completamente un usuario."""
    name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    role: Literal["admin", "support", "user"]
    is_active: bool


class UserPatch(BaseModel):
    """Modelo para actualizar parcialmente un usuario."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[Literal["admin", "support", "user"]] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Modelo de respuesta con ID incluido"""
    id: int = Field(..., description="ID único del usuario")

    model_config = ConfigDict(from_attributes=True)


class UserResponseWithoutEmail(BaseModel):
    """Modelo de respuesta que oculta el email"""
    id: int
    name: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Modelo para listar múltiples usuarios"""
    users: list[UserResponse]
    total: int = Field(..., description="Total de usuarios")

    model_config = ConfigDict(from_attributes=True)
