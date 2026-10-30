"""
Modelo de datos para la entidad Materia.
Define la tabla 'materias' con clave primaria UUID, datos académicos y relaciones.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base, GUID


class Materia(Base):
    """
    Modelo SQLAlchemy de la entidad Materia.
    Representa una asignatura cursada por un estudiante.
    """
    __tablename__ = "materias"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    nombre = Column(String(200), nullable=False)
    codigo = Column(String(50), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    semestre = Column(String(50), nullable=False)
    usuario_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relaciones
    usuario = relationship("User", back_populates="materias")
    tareas = relationship("Tarea", back_populates="materia", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Materia id={self.id} codigo={self.codigo} nombre={self.nombre}>"
