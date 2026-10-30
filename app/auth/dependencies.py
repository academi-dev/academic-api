"""
Módulo de dependencias de seguridad y autenticación.
Proporciona get_current_user y get_current_admin_user para proteger rutas mediante JWT.
"""
import uuid
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import APIError
from app.users.models import User, UserRole
from app.auth.service import verify_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    description="Ingrese el token de acceso JWT con el prefijo Bearer"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependencia que extrae y valida el JWT del encabezado Authorization.
    Verifica que el usuario exista en la base de datos y se encuentre activo.
    """
    payload = verify_token(token, expected_type="access")
    user_id_str = payload.get("sub")

    try:
        user_uuid = uuid.UUID(str(user_id_str))
    except (ValueError, TypeError):
        raise APIError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            codigo="TOKEN_INVALIDO",
            mensaje="El identificador de usuario en el token tiene un formato inválido."
        )

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise APIError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            codigo="NO_AUTORIZADO",
            mensaje="El usuario asociado al token no existe."
        )

    if not user.is_active:
        raise APIError(
            status_code=status.HTTP_403_FORBIDDEN,
            codigo="ACCESO_DENEGADO",
            mensaje="La cuenta de usuario se encuentra inactiva."
        )

    return user


def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependencia que restringe el acceso exclusivamente a usuarios con rol ADMIN.
    """
    if current_user.rol != UserRole.ADMIN:
        raise APIError(
            status_code=status.HTTP_403_FORBIDDEN,
            codigo="ACCESO_DENEGADO",
            mensaje="Esta acción requiere privilegios de administrador."
        )
    return current_user
