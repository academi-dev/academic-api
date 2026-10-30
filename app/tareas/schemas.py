"""
Esquemas Pydantic para la entidad Tarea.
Define los contratos de datos para creación, actualización, respuestas y paginación.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.tareas.models import TareaPrioridad, TareaEstado


class TareaBase(BaseModel):
    """Atributos comunes para una tarea."""
    titulo: str = Field(..., min_length=2, max_length=200, description="Título o nombre de la tarea")
    descripcion: Optional[str] = Field(None, description="Descripción detallada de la tarea")
    fecha_entrega: Optional[datetime] = Field(None, description="Fecha y hora límite de entrega en formato ISO 8601 UTC")
    prioridad: TareaPrioridad = Field(default=TareaPrioridad.MEDIA, description="Nivel de prioridad: alta, media, baja")
    estado: TareaEstado = Field(default=TareaEstado.PENDIENTE, description="Estado actual: pendiente, en_progreso, completada")
    materia_id: uuid.UUID = Field(..., description="UUID de la materia a la cual pertenece la tarea")


class TareaCreate(TareaBase):
    """Esquema para la creación de una nueva tarea."""
    pass


class TareaUpdate(BaseModel):
    """Esquema para la actualización parcial o total de una tarea."""
    titulo: Optional[str] = Field(None, min_length=2, max_length=200, description="Título de la tarea")
    descripcion: Optional[str] = Field(None, description="Descripción de la tarea")
    fecha_entrega: Optional[datetime] = Field(None, description="Fecha y hora límite de entrega")
    prioridad: Optional[TareaPrioridad] = Field(None, description="Nivel de prioridad")
    estado: Optional[TareaEstado] = Field(None, description="Estado de la tarea")
    materia_id: Optional[uuid.UUID] = Field(None, description="UUID de la materia asociada")


class TareaResponse(TareaBase):
    """Esquema de respuesta pública con los datos completos de una tarea."""
    id: uuid.UUID = Field(..., description="Identificador único UUID de la tarea")
    usuario_id: uuid.UUID = Field(..., description="UUID del usuario propietario")
    created_at: datetime = Field(..., description="Fecha y hora de registro en UTC")

    model_config = ConfigDict(from_attributes=True)


class PaginatedTareasResponse(BaseModel):
    """Esquema de respuesta paginada para la lista de tareas."""
    total: int = Field(..., description="Número total de registros coincidentes con los filtros")
    limite: int = Field(..., description="Cantidad máxima de registros retornados")
    desplazamiento: int = Field(..., description="Cantidad de registros omitidos")
    items: List[TareaResponse] = Field(..., description="Lista de tareas de la página actual")
