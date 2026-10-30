"""
Servicio de lógica de negocio para la gestión de tareas.
Implementa validaciones de pertenencia de materias, filtros avanzados y CRUD.
"""
import uuid
from datetime import datetime
from typing import Tuple, List, Optional
from sqlalchemy.orm import Session
from fastapi import status

from app.exceptions import APIError
from app.materias.models import Materia
from app.tareas.models import Tarea, TareaEstado
from app.tareas.schemas import TareaCreate, TareaUpdate


def _validar_materia_propietario(db: Session, materia_id: uuid.UUID, usuario_id: uuid.UUID) -> Materia:
    """
    Valida que la materia exista y pertenezca al usuario solicitante.
    """
    materia = db.query(Materia).filter(
        Materia.id == materia_id,
        Materia.usuario_id == usuario_id
    ).first()
    if not materia:
        raise APIError(
            status_code=status.HTTP_404_NOT_FOUND,
            codigo="RECURSO_NO_ENCONTRADO",
            mensaje=f"La materia con ID '{materia_id}' no existe o no pertenece al usuario."
        )
    return materia


def get_tareas(
    db: Session,
    usuario_id: uuid.UUID,
    materia_id: Optional[uuid.UUID] = None,
    estado: Optional[TareaEstado] = None,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    limite: int = 10,
    desplazamiento: int = 0
) -> Tuple[List[Tarea], int]:
    """
    Lista las tareas del usuario aplicando filtros opcionales de materia, estado y rango de fechas.
    Retorna una tupla (lista_tareas, total_registros).
    """
    query = db.query(Tarea).filter(Tarea.usuario_id == usuario_id)

    if materia_id is not None:
        query = query.filter(Tarea.materia_id == materia_id)

    if estado is not None:
        query = query.filter(Tarea.estado == estado)

    if fecha_inicio is not None:
        query = query.filter(Tarea.fecha_entrega >= fecha_inicio)

    if fecha_fin is not None:
        query = query.filter(Tarea.fecha_entrega <= fecha_fin)

    total = query.count()
    tareas = query.order_by(Tarea.fecha_entrega.asc(), Tarea.created_at.desc()).offset(desplazamiento).limit(limite).all()
    return tareas, total


def get_tarea_by_id(
    db: Session,
    tarea_id: uuid.UUID,
    usuario_id: uuid.UUID
) -> Tarea:
    """
    Obtiene una tarea por su ID garantizando que pertenezca al usuario autenticado.
    Lanza APIError 404 si no se encuentra.
    """
    tarea = db.query(Tarea).filter(
        Tarea.id == tarea_id,
        Tarea.usuario_id == usuario_id
    ).first()

    if not tarea:
        raise APIError(
            status_code=status.HTTP_404_NOT_FOUND,
            codigo="RECURSO_NO_ENCONTRADO",
            mensaje=f"No se encontró la tarea con identificador '{tarea_id}'."
        )
    return tarea


def create_tarea(
    db: Session,
    tarea_in: TareaCreate,
    usuario_id: uuid.UUID
) -> Tarea:
    """
    Crea una nueva tarea previa verificación de que la materia asociada le pertenece al usuario.
    """
    _validar_materia_propietario(db=db, materia_id=tarea_in.materia_id, usuario_id=usuario_id)

    tarea = Tarea(
        id=uuid.uuid4(),
        titulo=tarea_in.titulo.strip(),
        descripcion=tarea_in.descripcion.strip() if tarea_in.descripcion else None,
        fecha_entrega=tarea_in.fecha_entrega,
        prioridad=tarea_in.prioridad,
        estado=tarea_in.estado,
        materia_id=tarea_in.materia_id,
        usuario_id=usuario_id
    )
    db.add(tarea)
    db.commit()
    db.refresh(tarea)
    return tarea


def update_tarea(
    db: Session,
    tarea_id: uuid.UUID,
    tarea_in: TareaUpdate,
    usuario_id: uuid.UUID
) -> Tarea:
    """
    Actualiza los datos de una tarea. Si se cambia la materia_id, valida su pertenencia.
    """
    tarea = get_tarea_by_id(db=db, tarea_id=tarea_id, usuario_id=usuario_id)

    update_data = tarea_in.model_dump(exclude_unset=True)

    if "materia_id" in update_data and update_data["materia_id"] is not None:
        _validar_materia_propietario(db=db, materia_id=update_data["materia_id"], usuario_id=usuario_id)

    for field, value in update_data.items():
        if isinstance(value, str):
            setattr(tarea, field, value.strip())
        else:
            setattr(tarea, field, value)

    db.commit()
    db.refresh(tarea)
    return tarea


def delete_tarea(
    db: Session,
    tarea_id: uuid.UUID,
    usuario_id: uuid.UUID
) -> None:
    """
    Elimina una tarea existente perteneciente al usuario autenticado.
    """
    tarea = get_tarea_by_id(db=db, tarea_id=tarea_id, usuario_id=usuario_id)
    db.delete(tarea)
    db.commit()
