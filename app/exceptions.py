"""
Módulo de excepciones personalizadas de la aplicación.
Proporciona la clase APIError para generar respuestas con el formato institucional:
{"error": {"codigo": "...", "mensaje": "..."}}
"""
from fastapi import HTTPException


class APIError(HTTPException):
    """
    Excepción personalizada para errores del negocio y de la API.
    Garantiza el formato unificado {"error": {"codigo": "...", "mensaje": "..."}}.
    """
    def __init__(self, status_code: int, codigo: str, mensaje: str):
        super().__init__(status_code=status_code, detail=mensaje)
        self.status_code = status_code
        self.codigo = codigo
        self.mensaje = mensaje
