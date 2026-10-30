"""
Servicio de lógica de negocio para autenticación.
Gestiona el cifrado de contraseñas, validación de credenciales
y generación/verificación de tokens JWT (acceso y refresco).
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import status

from app.config import settings
from app.exceptions import APIError
from app.users.models import User, UserRole
from app.auth.schemas import RegistroRequest


# Contexto de cifrado para contraseñas utilizando bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Genera el hash seguro de una contraseña utilizando bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un token de acceso JWT firmado con expiración corta.
    """
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": now_utc,
        "type": "access"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Genera un token de actualización JWT firmado con expiración extendida.
    """
    to_encode = data.copy()
    now_utc = datetime.now(timezone.utc)
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": now_utc,
        "type": "refresh"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str, expected_type: str = "access") -> Dict[str, Any]:
    """
    Decodifica y valida un token JWT comprobando firma, vigencia y tipo de token.
    Lanza APIError en caso de token inválido o expirado.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_type = payload.get("type")
        if token_type != expected_type:
            raise APIError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                codigo="TOKEN_INVALIDO",
                mensaje=f"Tipo de token incorrecto. Se esperaba '{expected_type}'."
            )
        user_id = payload.get("sub")
        if not user_id:
            raise APIError(
                status_code=status.HTTP_401_UNAUTHORIZED,
                codigo="TOKEN_INVALIDO",
                mensaje="El token no contiene un identificador de usuario válido."
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise APIError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            codigo="TOKEN_EXPIRADO",
            mensaje="El token ha expirado. Por favor inicie sesión nuevamente."
        )
    except jwt.InvalidTokenError:
        raise APIError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            codigo="TOKEN_INVALIDO",
            mensaje="El token proporcionado no es válido."
        )


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Autentica un usuario verificando su correo y contraseña en la base de datos.
    """
    user = db.query(User).filter(User.email == email.lower().strip()).first()
    if not user:
        raise APIError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            codigo="CREDENCIALES_INVALIDAS",
            mensaje="Correo electrónico o contraseña incorrectos."
        )
    if not verify_password(password, user.hashed_password):
        raise APIError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            codigo="CREDENCIALES_INVALIDAS",
            mensaje="Correo electrónico o contraseña incorrectos."
        )
    if not user.is_active:
        raise APIError(
            status_code=status.HTTP_403_FORBIDDEN,
            codigo="ACCESO_DENEGADO",
            mensaje="La cuenta de usuario está desactivada."
        )
    return user


def create_user(db: Session, user_data: RegistroRequest) -> User:
    """
    Registra un nuevo usuario en la base de datos previa verificación de unicidad de correo.
    """
    email_clean = user_data.email.lower().strip()
    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise APIError(
            status_code=status.HTTP_409_CONFLICT,
            codigo="CORREO_REGISTRADO",
            mensaje="Ya existe una cuenta registrada con este correo electrónico."
        )

    new_user = User(
        id=uuid.uuid4(),
        email=email_clean,
        hashed_password=get_password_hash(user_data.password),
        nombre=user_data.nombre.strip(),
        rol=UserRole.ESTUDIANTE,
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
