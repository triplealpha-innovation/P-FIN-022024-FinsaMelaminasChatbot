"""
core/exceptions.py

Este archivo contiene la lógica para manejar excepciones en la aplicación.

Responsabilidades principales:
- Manejar excepciones no esperadas.
- Manejar excepciones HTTP.
- Manejar excepciones de base de datos.
"""

import traceback
from fastapi import Request, HTTPException
from sqlalchemy.exc import DataError, IntegrityError
from fastapi.responses import JSONResponse
from services.logger import configure_logger

logger = configure_logger(name='exceptions')

# Manejo de excepciones no esperadas
async def exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unexpected error: {exc}")
    tb = traceback.format_exc()
    return JSONResponse(
        status_code=500,
        content={
            "message": f"Unexpected Error: {exc.__class__.__name__}.",
            "description": str(exc),
            "traceback": tb
        }
    )

# Manejo específico de excepciones HTTP
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )
    
def handle_db_exceptions(func):
    async def wrapper(*args, **kwargs):
        self = args[0]
        try:
            return await func(*args, **kwargs)
        except (IntegrityError, DataError) as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=f"Database error: {e}")
        except HTTPException as e:
            await self.db.rollback()
            raise e
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    return wrapper
