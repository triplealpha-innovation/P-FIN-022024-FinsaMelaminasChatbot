"""
dependencies/limiter.py

Este módulo configura un limitador de peticiones para la API utilizando SlowAPI.

Responsabilidades principales:
- Configurar un limitador de peticiones para la API.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
