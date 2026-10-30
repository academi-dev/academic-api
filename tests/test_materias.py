"""Pruebas del CRUD de materias y del aislamiento entre usuarios."""
import uuid
from typing import Callable, Dict

from fastapi.testclient import TestClient


def test_crear_materia_normaliza_codigo(client: TestClient, materia_creada: dict) -> None:
    assert materia_creada["codigo"] == "MAT-101"
    uuid.UUID(materia_creada["id"])  # Debe ser un UUID válido


def test_listar_materias_paginado(client: TestClient, auth_headers: Dict[str, str]) -> None:
    for i in range(3):
        client.post(
            "/api/v1/materias",
            json={"nombre": f"Materia {i}", "codigo": f"COD-{i}", "semestre": "2026-2"},
            headers=auth_headers,
        )
    respuesta = client.get("/api/v1/materias?limite=2&desplazamiento=0", headers=auth_headers)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["total"] == 3
    assert cuerpo["limite"] == 2
    assert len(cuerpo["items"]) == 2


def test_obtener_materia_por_id(client: TestClient, auth_headers: Dict[str, str],
                                materia_creada: dict) -> None:
    respuesta = client.get(f"/api/v1/materias/{materia_creada['id']}", headers=auth_headers)
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Cálculo Diferencial"


def test_obtener_materia_inexistente_devuelve_404(client: TestClient,
                                                  auth_headers: Dict[str, str]) -> None:
    respuesta = client.get(f"/api/v1/materias/{uuid.uuid4()}", headers=auth_headers)
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "RECURSO_NO_ENCONTRADO"


def test_actualizar_materia(client: TestClient, auth_headers: Dict[str, str],
                            materia_creada: dict) -> None:
    respuesta = client.put(
        f"/api/v1/materias/{materia_creada['id']}",
        json={"nombre": "Cálculo Integral"},
        headers=auth_headers,
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Cálculo Integral"
    assert respuesta.json()["semestre"] == "2026-2"


def test_eliminar_materia(client: TestClient, auth_headers: Dict[str, str],
                          materia_creada: dict) -> None:
    url = f"/api/v1/materias/{materia_creada['id']}"
    assert client.delete(url, headers=auth_headers).status_code == 204
    assert client.get(url, headers=auth_headers).status_code == 404


def test_usuario_no_ve_materias_de_otro(client: TestClient, materia_creada: dict,
                                        registrar_y_autenticar: Callable[..., Dict[str, str]]) -> None:
    otro = registrar_y_autenticar(email="otro@academic.dev")
    url = f"/api/v1/materias/{materia_creada['id']}"
    assert client.get(url, headers=otro).status_code == 404
    assert client.delete(url, headers=otro).status_code == 404
    assert client.get("/api/v1/materias", headers=otro).json()["total"] == 0
