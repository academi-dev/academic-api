"""
Punto de entrada principal para Academic API.
Configura la aplicación FastAPI, middleware de CORS, manejadores globales de excepciones,
ciclo de vida (lifespan) y monta los enrutadores de la API v1.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.exceptions import APIError
from app.database import engine, Base
from app.auth.router import router as auth_router
from app.materias.router import router as materias_router
from app.tareas.router import router as tareas_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gestiona el ciclo de vida de la aplicación.
    Inicializa tablas en desarrollo si es necesario y libera recursos al apagar.
    """
    # Creación automática de tablas (útil para SQLite en desarrollo/testing sin migraciones pendientes)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        print(f"[ALERTA] No se pudieron inicializar tablas en arranque: {exc}")
    yield
    # Limpieza o desconexión al apagar
    pass


app = FastAPI(
    title="Academic API",
    description=(
        "API REST para la gestión integral de vida académica universitaria: "
        "materias, tareas, entregas y usuarios con autenticación segura JWT y control de acceso."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configuración de Middleware CORS para desarrollo y producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# Manejadores de Excepciones Estandarizados
# Formato: {"error": {"codigo": "...", "mensaje": "..."}}
# ==============================================================================

@app.exception_handler(APIError)
async def custom_api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Maneja las excepciones controladas de la aplicación."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "codigo": exc.codigo,
                "mensaje": exc.mensaje
            }
        }
    )


@app.exception_handler(HTTPException)
async def standard_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Normaliza las excepciones HTTPException de FastAPI al formato institucional."""
    status_map = {
        status.HTTP_400_BAD_REQUEST: "SOLICITUD_INCORRECTA",
        status.HTTP_401_UNAUTHORIZED: "NO_AUTORIZADO",
        status.HTTP_403_FORBIDDEN: "ACCESO_DENEGADO",
        status.HTTP_404_NOT_FOUND: "RECURSO_NO_ENCONTRADO",
        status.HTTP_409_CONFLICT: "CONFLICTO",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "DATOS_INVALIDOS",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "ERROR_INTERNO",
    }
    codigo = status_map.get(exc.status_code, "ERROR_HTTP")

    mensaje = str(exc.detail) if exc.detail else "Ocurrió un error al procesar la solicitud."

    # Preservar diccionarios si el detalle ya viene estructurado
    if isinstance(exc.detail, dict):
        codigo = exc.detail.get("codigo", codigo)
        mensaje = exc.detail.get("mensaje", mensaje)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "codigo": codigo,
                "mensaje": mensaje
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Maneja y formatea los errores de validación de esquemas Pydantic."""
    error_details = []
    for err in exc.errors():
        loc = " -> ".join([str(p) for p in err.get("loc", []) if p != "body"])
        msg = err.get("msg", "Dato inválido")
        error_details.append(f"{loc}: {msg}" if loc else msg)

    mensaje_resumen = "; ".join(error_details) if error_details else "Error de validación en los datos enviados."

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "codigo": "DATOS_INVALIDOS",
                "mensaje": mensaje_resumen
            }
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Manejador global de contingencia para errores no previstos."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "codigo": "ERROR_INTERNO",
                "mensaje": "Ocurrió un error interno en el servidor. Por favor intente más tarde."
            }
        }
    )


# ==============================================================================
# Inclusión de Enrutadores de la API v1
# ==============================================================================

app.include_router(auth_router)
app.include_router(materias_router)
app.include_router(tareas_router)


# ==============================================================================
# Endpoints de Salud y Estado
# ==============================================================================

@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Salud"],
    summary="Verificar estado de la API"
)
def verificar_salud():
    """Retorna el estado de operatividad de la aplicación."""
    return {
        "status": "healthy",
        "service": "academic-api",
        "environment": settings.ENVIRONMENT
    }


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    tags=["Salud"],
    summary="Página de bienvenida"
)
def raiz():
    """Endpoint raíz que orienta al usuario hacia la documentación interactiva."""
    return {
        "mensaje": "Bienvenido a Academic API",
        "version": "1.0.0",
        "documentacion": "/docs"
    }
