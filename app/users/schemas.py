"""
Esquemas Pydantic para la entidad Usuario.
Define la validación y serialización de datos de entrada y salida.
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field

from app.users.models import UserRole


class UserBase(BaseModel):
    """Esquema base con atributos comunes de usuario."""
    email: EmailStr = Field(..., description="Correo electrónico único del usuario")
    nombre: str = Field(..., min_length=2, max_length=150, description="Nombre completo")
    rol: UserRole = Field(default=UserRole.ESTUDIANTE, description="Rol del usuario en la plataforma")


class UserCreate(UserBase):
    """Esquema para la creación de un nuevo usuario."""
    password: str = Field(..., min_length=6, max_length=128, description="Contraseña en texto plano")


class UserResponse(UserBase):
    """Esquema de respuesta pública de usuario."""
    id: uuid.UUID = Field(..., description="Identificador único UUID")
    is_active: bool = Field(..., description="Indica si la cuenta está activa")
    created_at: datetime = Field(..., description="Fecha y hora de creación en UTC")

    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """Esquema de usuario interno que incluye el hash de la contraseña."""
    hashed_password: str = Field(..., description="Hash bcrypt de la contraseña")
