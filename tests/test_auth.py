"""Pruebas de los endpoints de autenticación: registro, login y refresh."""
from fastapi.testclient import TestClient


def test_registro_exitoso_devuelve_usuario_sin_password(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/auth/registro",
        json={"email": "Nuevo@Academic.dev", "password": "secreto123", "nombre": "Jean Mena"},
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["email"] == "nuevo@academic.dev"
    assert cuerpo["rol"] == "estudiante"
    assert "password" not in cuerpo and "hashed_password" not in cuerpo


def test_registro_no_permite_autoasignarse_admin(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/auth/registro",
        json={"email": "pillo@academic.dev", "password": "secreto123",
              "nombre": "Intento Admin", "rol": "admin"},
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["rol"] == "estudiante"


def test_registro_correo_duplicado_devuelve_409(client: TestClient) -> None:
    datos = {"email": "dup@academic.dev", "password": "secreto123", "nombre": "Duplicado"}
    assert client.post("/api/v1/auth/registro", json=datos).status_code == 201
    respuesta = client.post("/api/v1/auth/registro", json=datos)
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["codigo"] == "CORREO_REGISTRADO"


def test_registro_datos_invalidos_usa_formato_de_error(client: TestClient) -> None:
    respuesta = client.post(
        "/api/v1/auth/registro",
        json={"email": "no-es-correo", "password": "123", "nombre": "X"},
    )
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "DATOS_INVALIDOS"


def test_login_exitoso_devuelve_tokens(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/registro",
        json={"email": "login@academic.dev", "password": "secreto123", "nombre": "Login"},
    )
    respuesta = client.post(
        "/api/v1/auth/login", json={"email": "login@academic.dev", "password": "secreto123"}
    )
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["token_type"] == "bearer"
    assert cuerpo["access_token"] and cuerpo["refresh_token"]


def test_login_password_incorrecta_devuelve_401(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/registro",
        json={"email": "malpass@academic.dev", "password": "secreto123", "nombre": "Mal"},
    )
    respuesta = client.post(
        "/api/v1/auth/login", json={"email": "malpass@academic.dev", "password": "otra-cosa"}
    )
    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["codigo"] == "CREDENCIALES_INVALIDAS"


def test_refresh_emite_nuevos_tokens(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/registro",
        json={"email": "refresh@academic.dev", "password": "secreto123", "nombre": "Refresh"},
    )
    login = client.post(
        "/api/v1/auth/login", json={"email": "refresh@academic.dev", "password": "secreto123"}
    ).json()
    respuesta = client.post("/api/v1/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert respuesta.status_code == 200
    assert respuesta.json()["access_token"]


def test_refresh_rechaza_access_token(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/registro",
        json={"email": "tipo@academic.dev", "password": "secreto123", "nombre": "Tipo"},
    )
    login = client.post(
        "/api/v1/auth/login", json={"email": "tipo@academic.dev", "password": "secreto123"}
    ).json()
    respuesta = client.post("/api/v1/auth/refresh", json={"refresh_token": login["access_token"]})
    assert respuesta.status_code == 401


def test_endpoint_protegido_sin_token_es_rechazado(client: TestClient) -> None:
    respuesta = client.get("/api/v1/materias")
    assert respuesta.status_code in (401, 403)
    assert "error" in respuesta.json()
