"""
Servicio de lógica de negocio para la gestión de materias.
Asegura el aislamiento de datos por usuario y la validación de reglas de negocio.
"""
import uuid
from typing import Tuple, List, Optional
from sqlalchemy.orm import Session
from fastapi import status

from app.exceptions import APIError
from app.materias.models import Materia
from app.materias.schemas import MateriaCreate, MateriaUpdate


def get_materias(
    db: Session,
    usuario_id: uuid.UUID,
    limite: int = 10,
    desplazamiento: int = 0
) -> Tuple[List[Materia], int]:
    """
    Obtiene la lista paginada de materias pertenecientes al usuario especificado.
    Retorna una tupla (lista_materias, total_registros).
    """
    query = db.query(Materia).filter(Materia.usuario_id == usuario_id)
    total = query.count()
    materias = query.order_by(Materia.created_at.desc()).offset(desplazamiento).limit(limite).all()
    return materias, total


def get_materia_by_id(
    db: Session,
    materia_id: uuid.UUID,
    usuario_id: uuid.UUID
) -> Materia:
    """
    Obtiene una materia por su ID, garantizando que pertenezca al usuario autenticado.
    Lanza APIError 404 si la materia no existe o pertenece a otro usuario.
    """
    materia = db.query(Materia).filter(
        Materia.id == materia_id,
        Materia.usuario_id == usuario_id
    ).first()

    if not materia:
        raise APIError(
            status_code=status.HTTP_404_NOT_FOUND,
            codigo="RECURSO_NO_ENCONTRADO",
            mensaje=f"No se encontró la materia con identificador '{materia_id}'."
        )
    return materia


def create_materia(
    db: Session,
    materia_in: MateriaCreate,
    usuario_id: uuid.UUID
) -> Materia:
    """
    Registra una nueva materia vinculada al usuario autenticado.
    """
    materia = Materia(
        id=uuid.uuid4(),
        nombre=materia_in.nombre.strip(),
        codigo=materia_in.codigo.strip().upper(),
        descripcion=materia_in.descripcion.strip() if materia_in.descripcion else None,
        semestre=materia_in.semestre.strip(),
        usuario_id=usuario_id
    )
    db.add(materia)
    db.commit()
    db.refresh(materia)
    return materia


def update_materia(
    db: Session,
    materia_id: uuid.UUID,
    materia_in: MateriaUpdate,
    usuario_id: uuid.UUID
) -> Materia:
    """
    Actualiza los datos de una materia existente perteneciente al usuario.
    """
    materia = get_materia_by_id(db=db, materia_id=materia_id, usuario_id=usuario_id)

    update_data = materia_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "codigo" and value is not None:
            setattr(materia, field, value.strip().upper())
        elif isinstance(value, str):
            setattr(materia, field, value.strip())
        else:
            setattr(materia, field, value)

    db.commit()
    db.refresh(materia)
    return materia


def delete_materia(
    db: Session,
    materia_id: uuid.UUID,
    usuario_id: uuid.UUID
) -> None:
    """
    Elimina una materia y sus tareas asociadas en cascada.
    """
    materia = get_materia_by_id(db=db, materia_id=materia_id, usuario_id=usuario_id)
    db.delete(materia)
    db.commit()
