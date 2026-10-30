"""
Fixtures compartidas para las pruebas de Academic API.

Usa SQLite en memoria con StaticPool para que todas las sesiones compartan
la misma conexión, y reemplaza la dependencia get_db de FastAPI.
"""
import os

# Debe definirse ANTES de importar la app, porque el engine se crea al importar.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "clave_de_pruebas_solo_para_tests_1234567890"

from typing import Callable, Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

engine_test = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Crea un esquema limpio para cada prueba y lo destruye al terminar."""
    Base.metadata.create_all(bind=engine_test)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine_test)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Cliente HTTP de pruebas con la base de datos de prueba inyectada."""

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def registrar_y_autenticar(client: TestClient) -> Callable[..., Dict[str, str]]:
    """Fábrica que registra un usuario, inicia sesión y devuelve los headers Bearer."""

    def _crear(email: str = "estudiante@academic.dev", password: str = "secreto123",
               nombre: str = "Estudiante Prueba") -> Dict[str, str]:
        respuesta = client.post(
            "/api/v1/auth/registro",
            json={"email": email, "password": password, "nombre": nombre},
        )
        assert respuesta.status_code == 201, respuesta.text
        login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login.status_code == 200, login.text
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

    return _crear


@pytest.fixture()
def auth_headers(registrar_y_autenticar: Callable[..., Dict[str, str]]) -> Dict[str, str]:
    """Headers de autorización de un usuario estándar."""
    return registrar_y_autenticar()


@pytest.fixture()
def materia_creada(client: TestClient, auth_headers: Dict[str, str]) -> dict:
    """Crea una materia para el usuario estándar y devuelve su JSON."""
    respuesta = client.post(
        "/api/v1/materias",
        json={"nombre": "Cálculo Diferencial", "codigo": "mat-101", "semestre": "2026-2"},
        headers=auth_headers,
    )
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()
