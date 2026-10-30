"""
Esquemas Pydantic para la entidad Materia.
Define los contratos de datos para creación, actualización y respuestas paginadas.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class MateriaBase(BaseModel):
    """Atributos base comunes para una materia académica."""
    nombre: str = Field(..., min_length=2, max_length=200, description="Nombre de la asignatura")
    codigo: str = Field(..., min_length=1, max_length=50, description="Código de la materia (ej. MAT-101)")
    descripcion: Optional[str] = Field(None, description="Descripción detallada de la materia")
    semestre: str = Field(..., min_length=1, max_length=50, description="Semestre o período académico (ej. 2026-1)")


class MateriaCreate(MateriaBase):
    """Esquema para la creación de una nueva materia."""
    pass


class MateriaUpdate(BaseModel):
    """Esquema para la actualización parcial o total de una materia."""
    nombre: Optional[str] = Field(None, min_length=2, max_length=200, description="Nombre de la asignatura")
    codigo: Optional[str] = Field(None, min_length=1, max_length=50, description="Código de la materia")
    descripcion: Optional[str] = Field(None, description="Descripción de la materia")
    semestre: Optional[str] = Field(None, min_length=1, max_length=50, description="Semestre o período académico")


class MateriaResponse(MateriaBase):
    """Esquema de respuesta detallada de una materia."""
    id: uuid.UUID = Field(..., description="Identificador único UUID de la materia")
    usuario_id: uuid.UUID = Field(..., description="UUID del usuario propietario")
    created_at: datetime = Field(..., description="Fecha y hora de registro en UTC")

    model_config = ConfigDict(from_attributes=True)


class PaginatedMateriasResponse(BaseModel):
    """Esquema de respuesta paginada para listas de materias."""
    total: int = Field(..., description="Número total de registros disponibles")
    limite: int = Field(..., description="Cantidad máxima de registros solicitados")
    desplazamiento: int = Field(..., description="Cantidad de registros omitidos")
    items: List[MateriaResponse] = Field(..., description="Lista de materias en la página actual")
