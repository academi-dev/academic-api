# Academic API 🎓

[![CI/CD](https://img.shields.io/github/actions/workflow/status/academic-dev/academic-api/ci.yml?branch=main&style=for-the-badge&logo=github-actions&logoColor=white&label=CI%2FCD)](https://github.com/academi-dev/academic-api)
[![Python](https://img.shields.io/badge/Python-3.15-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Licencia MIT](https://img.shields.io/badge/Licencia-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Último Commit](https://img.shields.io/github/last-commit/academic-dev/academic-api?style=for-the-badge&logo=git&logoColor=white)](https://github.com/academi-dev/academic-api/commits/main)

**Academic API** es el servicio central RESTful del ecosistema **Academic**, diseñado para la gestión integral de materias, tareas y usuarios en entornos universitarios. Provee una arquitectura modular de alto rendimiento, autenticación robusta mediante JSON Web Tokens (JWT) con control de acceso basado en roles (RBAC) y persistencia relacional con PostgreSQL.

---

## 📋 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Stack Tecnológico](#-stack-tecnológico)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación y Configuración](#-instalación-y-configuración)
  - [Entorno Local](#opción-1-ejecución-en-entorno-local)
  - [Docker & Docker Compose](#opción-2-ejecución-con-docker-y-docker-compose)
- [Endpoints de la API](#-endpoints-de-la-api)
- [Documentación Interactiva](#-documentación-interactiva)
- [Pruebas Automatizadas](#-pruebas-automatizadas)
- [Capturas de Pantalla](#-capturas-de-pantalla)
- [Equipo de Desarrollo](#-equipo-de-desarrollo)
- [Licencia](#-licencia)

---

## ✨ Características Principales

- **Autenticación y Autorización Segura**: Emisión y validación de tokens JWT (Access & Refresh Tokens) con expiración configurable y cifrado seguro.
- **Control de Acceso Basado en Roles (RBAC)**: Distinción clara de permisos entre perfiles de `ADMINISTRADOR`, `DOCENTE` y `ESTUDIANTE`.
- **CRUD Completo de Materias**: Registro de asignaturas, códigos académicos, créditos, horarios y asignación de profesores/estudiantes.
- **Gestión Avanzada de Tareas**: Creación, seguimiento de estado (pendiente, entregada, calificada), ponderaciones y fechas límite con validación estricta de zonas horarias.
- **Migraciones con Alembic**: Versionado sistemático del esquema relacional de la base de datos sin pérdida de datos.
- **Validación Estricta de Esquemas**: Contratos de datos tipados mediante Pydantic v2 para garantizar integridad en request y response.
- **Contenerización Lista para Producción**: Configuración optimizada multi-stage con Dockerfile y orquestación con Docker Compose.

---

## 🛠 Stack Tecnológico

| Tecnología | Versión | Propósito / Descripción |
| :--- | :--- | :--- |
| **Python** | 3.15 | Lenguaje principal de desarrollo backend |
| **FastAPI** | 0.115+ | Framework web asíncrono de alto rendimiento para APIs REST |
| **SQLAlchemy** | 2.0+ | ORM asíncrono para mapeo objeto-relacional y consultas optimizadas |
| **Alembic** | 1.13+ | Herramienta de control de versiones y migraciones de esquemas en PostgreSQL |
| **PostgreSQL** | 16 | Motor de base de datos relacional para almacenamiento transaccional |
| **PyJWT** | 2.9+ | Generación, firma y verificación de JSON Web Tokens |
| **Pydantic** | 2.8+ | Modelado, parsing y validación de datos basada en tipos |
| **Uvicorn** | 0.30+ | Servidor ASGI ultrarrápido para la ejecución de la aplicación |
| **Docker & Compose** | 24+ / 2.20+ | Contenerización y orquestación de servicios en entornos reproducibles |
| **Pytest** | 8.0+ | Suite de pruebas unitarias y de integración asíncronas |

---

## 📂 Estructura del Proyecto

```text
academic-api/
├── app/
│   ├── main.py                  # Punto de entrada de la aplicación FastAPI y middlewares
│   ├── config.py                # Gestión de variables de entorno y settings (Pydantic BaseSettings)
│   ├── database.py              # Configuración de la sesión de base de datos SQLAlchemy
│   ├── auth/                    # Módulo de autenticación y seguridad
│   │   ├── router.py            # Endpoints: registro, login, refresh token
│   │   ├── schemas.py           # Esquemas Pydantic para credenciales y tokens
│   │   ├── service.py           # Lógica de hashing de contraseñas y generación de JWT
│   │   └── dependencies.py      # Inyección de dependencias para validación de usuario actual
│   ├── materias/                # Módulo de gestión académica de asignaturas
│   │   ├── router.py            # Rutas CRUD de materias
│   │   ├── schemas.py           # Esquemas de entrada y salida para materias
│   │   ├── service.py           # Reglas de negocio y operaciones de persistencia
│   │   └── models.py            # Modelo relacional SQLAlchemy para materias
│   ├── tareas/                  # Módulo de administración de tareas y entregas
│   │   ├── router.py            # Rutas CRUD de tareas
│   │   ├── schemas.py           # Validaciones de asignaciones y fechas de entrega
│   │   ├── service.py           # Lógica para filtrado, asignación y cambio de estados
│   │   └── models.py            # Modelo relacional SQLAlchemy para tareas
│   └── users/                   # Módulo de gestión de usuarios
│       ├── models.py            # Entidad User con roles y relaciones
│       └── schemas.py           # Esquemas de serialización de usuarios
├── alembic/                     # Scripts de migración del esquema de base de datos
│   ├── versions/
│   └── env.py
├── tests/                       # Banco de pruebas unitarias y de integración
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_materias.py
│   └── test_tareas.py
├── Dockerfile                   # Definición de contenedor Docker multi-stage
├── docker-compose.yml           # Configuración de servicios (API + PostgreSQL)
├── requirements.txt             # Dependencias del proyecto
├── .env.example                 # Plantilla de variables de configuración
└── alembic.ini                  # Configuración del motor Alembic
```

---

## ⚙️ Requisitos Previos

- **Python 3.15** o superior instalado en el sistema.
- **PostgreSQL 16** (si se ejecuta en entorno local sin Docker).
- **Docker** y **Docker Compose** (recomendado para desarrollo y despliegue homogéneo).
- **Git** para clonar el repositorio.

---

## 🚀 Instalación y Configuración

### Configuración de Variables de Entorno

Antes de iniciar la aplicación, configure el archivo de variables de entorno a partir de la plantilla:

```bash
cp .env.example .env
```

Ajuste los valores en `.env` según su configuración:

```ini
PROJECT_NAME="Academic API"
ENVIRONMENT="development"
SECRET_KEY="tu_clave_secreta_super_segura_para_firmar_jwt"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

POSTGRES_SERVER="localhost"
POSTGRES_PORT=5432
POSTGRES_USER="academic_user"
POSTGRES_PASSWORD="academic_password"
POSTGRES_DB="academic_db"
DATABASE_URL="postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}:${POSTGRES_PORT}/${POSTGRES_DB}"
```

---

### Opción 1: Ejecución en Entorno Local

1. **Crear y activar un entorno virtual:**

   ```bash
   python -m venv venv
   # En Linux / macOS:
   source venv/bin/activate
   # En Windows:
   .\venv\Scripts\activate
   ```

2. **Instalar dependencias:**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Ejecutar migraciones de base de datos:**

   ```bash
   alembic upgrade head
   ```

4. **Lanzar el servidor de desarrollo:**

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

La API estará accesible en `http://localhost:8000`.

---

### Opción 2: Ejecución con Docker y Docker Compose

La forma recomendada de ejecutar la API junto con su instancia de PostgreSQL es mediante Docker Compose:

1. **Construir e iniciar los contenedores:**

   ```bash
   docker compose up -d --build
   ```

2. **Verificar el estado de los servicios:**

   ```bash
   docker compose ps
   ```

3. **Verificar los logs del servicio:**

   ```bash
   docker compose logs -f api
   ```

4. **Detener los servicios:**

   ```bash
   docker compose down
   ```

---

## 🔌 Endpoints de la API

Todos los endpoints principales operan bajo el prefijo `/api/v1`.

### 🔐 Módulo de Autenticación (`/api/v1/auth`)

| Método | Endpoint | Roles Permitidos | Descripción |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/registro` | Público | Registra un nuevo usuario en la plataforma |
| `POST` | `/api/v1/auth/login` | Público | Autentica credenciales y emite tokens JWT (Access & Refresh) |
| `POST` | `/api/v1/auth/refresh` | Autenticado | Renueva el token de acceso utilizando un refresh token válido |

### 📚 Módulo de Materias (`/api/v1/materias`)

| Método | Endpoint | Roles Permitidos | Descripción |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/materias` | Estudiante, Docente, Admin | Lista las asignaturas con filtros de paginación y búsqueda |
| `POST` | `/api/v1/materias` | Docente, Admin | Crea y da de alta una nueva materia |
| `GET` | `/api/v1/materias/{id}` | Estudiante, Docente, Admin | Obtiene el detalle completo de una materia específica |
| `PUT` | `/api/v1/materias/{id}` | Docente, Admin | Actualiza la información o prerrequisitos de una materia |
| `DELETE` | `/api/v1/materias/{id}` | Admin | Elimina una materia del catálogo académico |

### 📝 Módulo de Tareas (`/api/v1/tareas`)

| Método | Endpoint | Roles Permitidos | Descripción |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/tareas` | Estudiante, Docente, Admin | Lista tareas filtradas por materia, estado y fecha de entrega |
| `POST` | `/api/v1/tareas` | Docente, Admin | Crea y publica una nueva tarea para los alumnos inscritos |
| `GET` | `/api/v1/tareas/{id}` | Estudiante, Docente, Admin | Retorna los detalles, consigna y fecha límite de una tarea |
| `PUT` | `/api/v1/tareas/{id}` | Docente, Admin | Actualiza los datos, ponderación o fecha de vencimiento |
| `DELETE` | `/api/v1/tareas/{id}` | Docente, Admin | Elimina una tarea y sus registros asociados |

---

## 📖 Documentación Interactiva

FastAPI genera automáticamente documentación interactiva accesible directamente desde el navegador con el servidor en ejecución:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)  
  *Permite probar endpoints directamente, autorizar tokens Bearer y consultar esquemas de datos.*
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)  
  *Documentación técnica detallada y formateada para especificaciones de producción.*

---

## 🧪 Pruebas Automatizadas

El proyecto incluye pruebas automatizadas con **Pytest** que validan la capa de servicios, modelos y endpoints:

```bash
# Ejecutar todas las pruebas con reporte de cobertura
pytest -v --cov=app tests/

# Ejecutar únicamente pruebas de autenticación
pytest tests/test_auth.py
```

---

## 📸 Capturas de Pantalla

> [!NOTE]  
> En esta sección se incluirán capturas de pantalla de la interfaz interactiva de Swagger UI, consultas en Postman y ejecución de pruebas en los flujos de CI/CD.

```
+-----------------------------------------------------------------+
|                   [ Capturas de Swagger UI ]                    |
|             (Próximamente disponibles en el release)            |
+-----------------------------------------------------------------+
```

---

## 👥 Equipo de Desarrollo

Este proyecto es desarrollado y mantenido por:

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/hilton45">
        <img src="https://github.com/hilton45.png" width="100px;" alt="Jean Mena" style="border-radius:50%;"/><br />
        <sub><b>Jean Mena</b></sub>
      </a><br />
      <a href="https://github.com/hilton45">@hilton45</a>
    </td>
    <td align="center">
      <a href="https://github.com/eyfer3174-commits">
        <img src="https://github.com/eyfer3174-commits.png" width="100px;" alt="Eyfer Mena" style="border-radius:50%;"/><br />
        <sub><b>Eyfer Mena</b></sub>
      </a><br />
      <a href="https://github.com/eyfer3174-commits">@eyfer3174-commits</a>
    </td>
  </tr>
</table>

---

## 📄 Licencia

Este proyecto está distribuido bajo la Licencia **MIT**. Consulte el archivo [LICENSE](LICENSE) para obtener más información.
