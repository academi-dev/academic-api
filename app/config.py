"""
Módulo de configuración de la aplicación.
Carga variables de entorno utilizando pydantic-settings.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración global de la aplicación Academic API.
    Lee los valores desde el archivo .env o variables de entorno del sistema.
    """
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/academic_db"
    SECRET_KEY: str = "clave_secreta_por_defecto_para_desarrollo_local_12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
