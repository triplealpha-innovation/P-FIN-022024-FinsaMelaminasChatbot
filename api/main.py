from db.schemas import UserInput
from services.workflow import app_workflow
from core import config
from core.exceptions import exception_handler, http_exception_handler
from services.limiter import limiter
from services.utils import save_context

from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, RedirectResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.security.api_key import APIKeyHeader

app = FastAPI(
    title=config.PROJECT_NAME,
    version=config.VERSION,
    debug=config.DEBUG,
    contact={'email':'adosil@triplealpha.in'},
)

# ----------------------------------------------------------------
# Configuración de límites de velocidad
# ----------------------------------------------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ----------------------------------------------------------------
# Middleware para permitir CORS
# ----------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------
# Middleware para redirigir HTTP a HTTPS
# ----------------------------------------------------------------
@app.middleware("http")
async def https_redirect(request: Request, call_next):
    if request.headers.get("x-forwarded-proto") == "http":
        url = request.url.replace(scheme="https")
        return RedirectResponse(url)
    response = await call_next(request)
    return response

# ----------------------------------------------------------------
# Protege /docs y /redoc con api_key
# ----------------------------------------------------------------
# Definir el encabezado para la API Key

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

@app.middleware("http")
async def check_api_key(request: Request, call_next):
    if request.url.path in ["/docs", "/redoc"]:
        api_key = request.query_params.get("api_key")

        if not api_key:
            return JSONResponse(status_code=401, content={"detail": "Para acceder a /docs y /redoc, se requiere una API Key, la cual hay que pasarla como parámetro 'api_key' en la URL. Ejemplo: /docs?api_key=API"})
        if api_key != config.DOCS_API_KEY:
            return JSONResponse(status_code=401, content={"detail": "API Key incorrecta."})

    response = await call_next(request)
    return response

# Función para validar la API Key para endpoints
async def validate_api_key(api_key: str = Depends(api_key_header)):
    if api_key is None or api_key != config.X_API_KEY:
        raise HTTPException(status_code=401, detail="API Key inválida o no proporcionada.")
    return api_key

# ----------------------------------------------------------------
# Manejo de excepciones
# ----------------------------------------------------------------
app.add_exception_handler(Exception, exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# ----------------------------------------------------------------
# Rutas
# ----------------------------------------------------------------
@app.get("/process_question/")
@limiter.limit("5/minute")
async def process_question(
    question: str, 
    request: Request, 
    uuid_sesion: str = None,  # Agregar uuid_sesion como parámetro de la URL
    str = Depends(validate_api_key)  # 🔒 Protección con API Key
):
    try:
        # Llamada al flujo de trabajo, incluyendo uuid_sesion
        result = app_workflow.invoke({"question": question, "uuid_sesion": uuid_sesion, "attempts": 0})
        return {"result": result}
    except RateLimitExceeded as e:
        raise HTTPException(status_code=429, detail="Límite de peticiones excedido, por favor espera un momento.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
@app.get("/save_context/")
@limiter.limit("60/minute")
async def process_question(
    context: str, 
    request: Request, 
    uuid_sesion: str = None,  # Agregar uuid_sesion como parámetro de la URL
    str = Depends(validate_api_key)  # 🔒 Protección con API Key
):
    try:
        # Llamada al flujo de trabajo, incluyendo uuid_sesion
        result = save_context({"context": context, "uuid_sesion": uuid_sesion, "attempts": 0})
        return {"result": result}
    except RateLimitExceeded as e:
        raise HTTPException(status_code=429, detail="Límite de peticiones excedido, por favor espera un momento.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")