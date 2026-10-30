"""
Esquemas Pydantic para los flujos de autenticación.
Define los modelos de datos para registro, inicio de sesión y tokens JWT.
"""
from pydantic import BaseModel, EmailStr, Field

from app.users.models import UserRole


class RegistroRequest(BaseModel):
    """
    Esquema de solicitud para registrar un nuevo usuario.
    El rol no se acepta desde el cliente: todo registro público crea un estudiante.
    """
    email: EmailStr = Field(..., description="Correo electrónico institucional o personal")
    password: str = Field(..., min_length=6, max_length=128, description="Contraseña de acceso")
    nombre: str = Field(..., min_length=2, max_length=150, description="Nombre completo del usuario")


class LoginRequest(BaseModel):
    """Esquema de solicitud para inicio de sesión."""
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., description="Contraseña del usuario")


class TokenResponse(BaseModel):
    """Esquema de respuesta con tokens de autenticación JWT."""
    access_token: str = Field(..., description="Token de acceso JWT de corta duración")
    refresh_token: str = Field(..., description="Token de actualización de larga duración")
    token_type: str = Field(default="bearer", description="Tipo de token (Bearer)")


class RefreshTokenRequest(BaseModel):
    """Esquema de solicitud para renovar el token de acceso."""
    refresh_token: str = Field(..., description="Token de actualización previamente otorgado")
