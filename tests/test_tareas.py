"""Pruebas del CRUD de tareas, filtros y aislamiento entre usuarios."""
import uuid
from typing import Callable, Dict

from fastapi.testclient import TestClient


def _crear_tarea(client: TestClient, headers: Dict[str, str], materia_id: str, **extra) -> dict:
    datos = {"titulo": "Taller 1", "materia_id": materia_id, **extra}
    respuesta = client.post("/api/v1/tareas", json=datos, headers=headers)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def test_crear_tarea_con_valores_por_defecto(client: TestClient, auth_headers: Dict[str, str],
                                             materia_creada: dict) -> None:
    tarea = _crear_tarea(client, auth_headers, materia_creada["id"],
                         fecha_entrega="2026-11-15T23:59:00Z")
    assert tarea["estado"] == "pendiente"
    assert tarea["prioridad"] == "media"
    assert tarea["materia_id"] == materia_creada["id"]


def test_crear_tarea_en_materia_inexistente_devuelve_404(client: TestClient,
                                                         auth_headers: Dict[str, str]) -> None:
    respuesta = client.post(
        "/api/v1/tareas",
        json={"titulo": "Huérfana", "materia_id": str(uuid.uuid4())},
        headers=auth_headers,
    )
    assert respuesta.status_code == 404


def test_filtrar_tareas_por_estado(client: TestClient, auth_headers: Dict[str, str],
                                   materia_creada: dict) -> None:
    _crear_tarea(client, auth_headers, materia_creada["id"], titulo="Pendiente")
    _crear_tarea(client, auth_headers, materia_creada["id"], titulo="Lista", estado="completada")
    respuesta = client.get("/api/v1/tareas?estado=completada", headers=auth_headers)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["total"] == 1
    assert cuerpo["items"][0]["titulo"] == "Lista"


def test_filtrar_tareas_por_materia(client: TestClient, auth_headers: Dict[str, str],
                                    materia_creada: dict) -> None:
    otra = client.post(
        "/api/v1/materias",
        json={"nombre": "Física I", "codigo": "FIS-101", "semestre": "2026-2"},
        headers=auth_headers,
    ).json()
    _crear_tarea(client, auth_headers, materia_creada["id"])
    _crear_tarea(client, auth_headers, otra["id"], titulo="Laboratorio")
    respuesta = client.get(f"/api/v1/tareas?materia_id={otra['id']}", headers=auth_headers)
    assert respuesta.json()["total"] == 1
    assert respuesta.json()["items"][0]["titulo"] == "Laboratorio"


def test_actualizar_estado_de_tarea(client: TestClient, auth_headers: Dict[str, str],
                                    materia_creada: dict) -> None:
    tarea = _crear_tarea(client, auth_headers, materia_creada["id"])
    respuesta = client.put(
        f"/api/v1/tareas/{tarea['id']}", json={"estado": "en_progreso"}, headers=auth_headers
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "en_progreso"
    assert respuesta.json()["titulo"] == "Taller 1"


def test_eliminar_tarea(client: TestClient, auth_headers: Dict[str, str],
                        materia_creada: dict) -> None:
    tarea = _crear_tarea(client, auth_headers, materia_creada["id"])
    url = f"/api/v1/tareas/{tarea['id']}"
    assert client.delete(url, headers=auth_headers).status_code == 204
    assert client.get(url, headers=auth_headers).status_code == 404


def test_usuario_no_puede_crear_tarea_en_materia_ajena(
        client: TestClient, materia_creada: dict,
        registrar_y_autenticar: Callable[..., Dict[str, str]]) -> None:
    otro = registrar_y_autenticar(email="intruso@academic.dev")
    respuesta = client.post(
        "/api/v1/tareas",
        json={"titulo": "Intrusa", "materia_id": materia_creada["id"]},
        headers=otro,
    )
    assert respuesta.status_code == 404
