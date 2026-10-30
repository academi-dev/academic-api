"""
Router de FastAPI para la gestión de tareas académicas.
Proporciona endpoints CRUD protegidos con filtros por materia, estado y fecha de entrega.
"""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.tareas.models import TareaEstado
from app.tareas.schemas import (
    TareaCreate,
    TareaUpdate,
    TareaResponse,
    PaginatedTareasResponse
)
from app.tareas.service import (
    get_tareas,
    get_tarea_by_id,
    create_tarea,
    update_tarea,
    delete_tarea
)

router = APIRouter(
    prefix="/api/v1/tareas",
    tags=["Tareas"]
)


@router.get(
    "",
    response_model=PaginatedTareasResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar tareas con filtros y paginación",
    description="Retorna una lista paginada de tareas del usuario autenticado, filtrables por materia, estado y rango de fechas."
)
def listar_tareas(
    limite: int = Query(default=10, ge=1, le=100, description="Cantidad máxima de tareas a retornar"),
    desplazamiento: int = Query(default=0, ge=0, description="Cantidad de registros a omitir para paginación"),
    materia_id: Optional[uuid.UUID] = Query(default=None, description="Filtrar por identificador de materia"),
    estado: Optional[TareaEstado] = Query(default=None, description="Filtrar por estado: pendiente, en_progreso, completada"),
    fecha_inicio: Optional[datetime] = Query(default=None, description="Fecha de entrega mínima (ISO 8601 UTC)"),
    fecha_fin: Optional[datetime] = Query(default=None, description="Fecha de entrega máxima (ISO 8601 UTC)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> PaginatedTareasResponse:
    """Lista las tareas del usuario autenticado aplicando los filtros opcionales."""
    items, total = get_tareas(
        db=db,
        usuario_id=current_user.id,
        materia_id=materia_id,
        estado=estado,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        limite=limite,
        desplazamiento=desplazamiento
    )
    return PaginatedTareasResponse(
        total=total,
        limite=limite,
        desplazamiento=desplazamiento,
        items=items
    )


@router.post(
    "",
    response_model=TareaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva tarea",
    description="Crea una nueva tarea asignada a una materia del usuario autenticado."
)
def registrar_tarea(
    tarea_in: TareaCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TareaResponse:
    """Registra una nueva tarea académica."""
    return create_tarea(db=db, tarea_in=tarea_in, usuario_id=current_user.id)


@router.get(
    "/{tarea_id}",
    response_model=TareaResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener tarea por ID",
    description="Consulta la información detallada de una tarea por su identificador UUID."
)
def obtener_tarea(
    tarea_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TareaResponse:
    """Obtiene los detalles de una tarea perteneciente al usuario."""
    return get_tarea_by_id(db=db, tarea_id=tarea_id, usuario_id=current_user.id)


@router.put(
    "/{tarea_id}",
    response_model=TareaResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar tarea",
    description="Actualiza parcialmente o en su totalidad los datos de una tarea del usuario."
)
def actualizar_tarea_endpoint(
    tarea_id: uuid.UUID,
    tarea_in: TareaUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TareaResponse:
    """Actualiza una tarea existente."""
    return update_tarea(
        db=db,
        tarea_id=tarea_id,
        tarea_in=tarea_in,
        usuario_id=current_user.id
    )


@router.delete(
    "/{tarea_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar tarea",
    description="Elimina de forma permanente una tarea del usuario autenticado."
)
def eliminar_tarea_endpoint(
    tarea_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """Elimina una tarea existente."""
    delete_tarea(db=db, tarea_id=tarea_id, usuario_id=current_user.id)
    return None
