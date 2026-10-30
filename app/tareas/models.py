"""
Modelo de datos para la entidad Tarea.
Define la tabla 'tareas' con clave primaria UUID, enums de prioridad y estado,
y relaciones con Materia y Usuario.
"""
import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database import Base, GUID


class TareaPrioridad(str, enum.Enum):
    """Niveles de prioridad para una tarea académica."""
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class TareaEstado(str, enum.Enum):
    """Estados del ciclo de vida de una tarea."""
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"


class Tarea(Base):
    """
    Modelo SQLAlchemy de la entidad Tarea.
    Representa una actividad o entrega académica vinculada a una materia.
    """
    __tablename__ = "tareas"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_entrega = Column(DateTime(timezone=True), nullable=True)
    prioridad = Column(
        Enum(TareaPrioridad, values_callable=lambda obj: [e.value for e in obj]),
        default=TareaPrioridad.MEDIA,
        nullable=False
    )
    estado = Column(
        Enum(TareaEstado, values_callable=lambda obj: [e.value for e in obj]),
        default=TareaEstado.PENDIENTE,
        nullable=False
    )
    materia_id = Column(GUID, ForeignKey("materias.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relaciones
    usuario = relationship("User", back_populates="tareas")
    materia = relationship("Materia", back_populates="tareas")

    def __repr__(self) -> str:
        return f"<Tarea id={self.id} titulo={self.titulo} estado={self.estado}>"
