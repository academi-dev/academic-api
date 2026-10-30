"""
Modelo de datos para la entidad Usuario.
Define la tabla 'users' con clave primaria UUID, autenticación y roles.
"""
import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship

from app.database import Base, GUID


class UserRole(str, enum.Enum):
    """Enumeración de roles permitidos en el sistema."""
    ESTUDIANTE = "estudiante"
    ADMIN = "admin"


class User(Base):
    """
    Modelo SQLAlchemy de la entidad Usuario.
    Almacena credenciales, rol y relaciones con materias y tareas.
    """
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    nombre = Column(String(150), nullable=False)
    rol = Column(
        Enum(UserRole, values_callable=lambda obj: [e.value for e in obj]),
        default=UserRole.ESTUDIANTE,
        nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relaciones con materias y tareas
    materias = relationship("Materia", back_populates="usuario", cascade="all, delete-orphan")
    tareas = relationship("Tarea", back_populates="usuario", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} rol={self.rol}>"
