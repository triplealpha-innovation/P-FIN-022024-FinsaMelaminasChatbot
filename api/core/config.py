"""
core/config.py

Este archivo contiene la configuración global de la aplicación. Aquí se definen las variables de entorno y constantes

Responsabilidades principales:
- Definir las variables de entorno y constantes globales de la aplicación.
- Configurar la base de datos y otros servicios externos.
- Definir las rutas y versiones de la API.
- Establecer las claves y tokens de autenticación.
- Definir las variables de configuración de los servicios de mensajería y notificaciones.
"""
import os

DOCS_API_KEY = os.environ.get('DOCS_API_KEY')

API_PREFIX: str = "/api"
VERSION: str = "1.0.0"
PROJECT_NAME: str = "API Chatbot Finsa"
DEBUG: bool = False

# Base de datos producción
usernameDB = os.environ.get('usernameDB')
passwordDB = os.environ.get('passwordDB')
servernameDB = os.environ.get('servernameDB')
databasenameDB = os.environ.get('databasenameDB')

