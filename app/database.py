"""
Módulo de conexión y gestión de la base de datos con SQLAlchemy.
Proporciona el motor, el creador de sesiones, el tipo de dato GUID portable
y la dependencia get_db para inyección en los endpoints de FastAPI.
"""
import uuid
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.config import settings


class GUID(TypeDecorator):
    """
    Tipo de dato UUID independiente de la plataforma.
    En PostgreSQL utiliza el tipo nativo UUID(as_uuid=True).
    En SQLite y otros motores almacena una cadena fija CHAR(36).
    Garantiza que en Python siempre se manipulen objetos uuid.UUID.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return str(value) if isinstance(value, uuid.UUID) else value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))


# Configurar argumentos de conexión según motor
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Generador de dependencias de FastAPI para obtener una sesión de base de datos.
    Cierra la sesión automáticamente al finalizar el procesamiento de la solicitud.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
