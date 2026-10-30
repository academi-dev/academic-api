"""
Router de FastAPI para la gestión de materias.
Proporciona endpoints CRUD protegidos con autenticación JWT y soporte de paginación.
"""
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.materias.schemas import (
    MateriaCreate,
    MateriaUpdate,
    MateriaResponse,
    PaginatedMateriasResponse
)
from app.materias.service import (
    get_materias,
    get_materia_by_id,
    create_materia,
    update_materia,
    delete_materia
)

router = APIRouter(
    prefix="/api/v1/materias",
    tags=["Materias"]
)


@router.get(
    "",
    response_model=PaginatedMateriasResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar materias del usuario autenticado",
    description="Retorna una lista paginada de las materias pertenecientes al usuario actual."
)
def listar_materias(
    limite: int = Query(default=10, ge=1, le=100, description="Cantidad máxima de materias a retornar"),
    desplazamiento: int = Query(default=0, ge=0, description="Cantidad de registros a omitir para paginación"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> PaginatedMateriasResponse:
    """Lista las materias registradas para el usuario autenticado de forma paginada."""
    items, total = get_materias(
        db=db,
        usuario_id=current_user.id,
        limite=limite,
        desplazamiento=desplazamiento
    )
    return PaginatedMateriasResponse(
        total=total,
        limite=limite,
        desplazamiento=desplazamiento,
        items=items
    )


@router.post(
    "",
    response_model=MateriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva materia",
    description="Registra una nueva materia académica asociada a la cuenta del usuario autenticado."
)
def registrar_materia(
    materia_in: MateriaCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MateriaResponse:
    """Crea una nueva materia académica."""
    return create_materia(db=db, materia_in=materia_in, usuario_id=current_user.id)


@router.get(
    "/{materia_id}",
    response_model=MateriaResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener materia por ID",
    description="Consulta la información detallada de una materia por su identificador UUID."
)
def obtener_materia(
    materia_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MateriaResponse:
    """Devuelve los detalles de una materia si pertenece al usuario autenticado."""
    return get_materia_by_id(db=db, materia_id=materia_id, usuario_id=current_user.id)


@router.put(
    "/{materia_id}",
    response_model=MateriaResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar materia",
    description="Actualiza uno o varios campos de una materia existente perteneciente al usuario."
)
def actualizar_materia(
    materia_id: uuid.UUID,
    materia_in: MateriaUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> MateriaResponse:
    """Modifica los atributos de una materia existente."""
    return update_materia(
        db=db,
        materia_id=materia_id,
        materia_in=materia_in,
        usuario_id=current_user.id
    )


@router.delete(
    "/{materia_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar materia",
    description="Elimina una materia y todas sus tareas asociadas."
)
def eliminar_materia_endpoint(
    materia_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """Elimina definitivamente la materia y sus tareas dependientes."""
    delete_materia(db=db, materia_id=materia_id, usuario_id=current_user.id)
    return None
