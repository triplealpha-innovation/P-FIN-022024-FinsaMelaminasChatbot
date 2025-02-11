from db.schemas import UserInput
from services.workflow import app_workflow
from core import config
from core.exceptions import exception_handler, http_exception_handler
from services.limiter import limiter

from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

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
async def process_question(question: str, request: Request = None):
    try:
        # Llamamos al workflow con los datos de la petición
        result = app_workflow.invoke({"question": question, "attempts": 0})
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))