"""Schemas de registro, login y tokens."""

import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.user_schema import UserResponse


class UserRegister(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(default="user")
    is_active: bool = True

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if " " in value:
            raise ValueError("La contrasena no puede contener espacios")
        if not re.search(r"[A-Z]", value):
            raise ValueError("La contrasena debe incluir una mayuscula")
        if not re.search(r"[a-z]", value):
            raise ValueError("La contrasena debe incluir una minuscula")
        if not re.search(r"\d", value):
            raise ValueError("La contrasena debe incluir un numero")
        return value

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value not in {"admin", "support", "user"}:
            raise ValueError("Rol no permitido")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: str
    role: str


class AuthUserResponse(UserResponse):
    model_config = ConfigDict(from_attributes=True)
