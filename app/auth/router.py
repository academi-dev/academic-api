"""
Router de autenticación para Academic API.
Define los endpoints de registro de usuario, login y renovación de tokens JWT.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.users.models import User
from app.users.schemas import UserResponse
from app.auth.schemas import LoginRequest, RegistroRequest, TokenResponse, RefreshTokenRequest
from app.auth.service import (
    create_user,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Autenticación"]
)


@router.post(
    "/registro",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario en el sistema con rol de estudiante por defecto."
)
def registrar_usuario(
    registro_data: RegistroRequest,
    db: Session = Depends(get_db)
) -> UserResponse:
    """Registra un nuevo usuario en la plataforma."""
    usuario = create_user(db=db, user_data=registro_data)
    return usuario


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description="Valida credenciales y genera un par de tokens JWT (acceso y refresco)."
)
def iniciar_sesion(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """Autentica al usuario y devuelve el token de acceso y de refresco."""
    usuario = authenticate_user(db=db, email=login_data.email, password=login_data.password)
    
    token_data = {
        "sub": str(usuario.id),
        "email": usuario.email,
        "rol": usuario.rol.value
    }
    
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Renovar token de acceso",
    description="Emite un nuevo token de acceso a partir de un refresh token válido."
)
def refrescar_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """Valida el token de actualización y emite nuevos tokens de acceso y refresco."""
    payload = verify_token(refresh_data.refresh_token, expected_type="refresh")
    user_id = payload.get("sub")
    
    usuario = db.query(User).filter(User.id == user_id).first()
    if not usuario or not usuario.is_active:
        from app.exceptions import APIError
        raise APIError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            codigo="TOKEN_INVALIDO",
            mensaje="El usuario asociado a la sesión no existe o está inactivo."
        )

    token_data = {
        "sub": str(usuario.id),
        "email": usuario.email,
        "rol": usuario.rol.value
    }
    
    new_access_token = create_access_token(data=token_data)
    new_refresh_token = create_refresh_token(data=token_data)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )
