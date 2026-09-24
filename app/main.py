"""Aplicacion principal segura de device_systems."""

import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.auth import auth_routes
from app.core.config import settings
from app.core.rate_limit import limiter
from app.routes import device_routes, loan_routes, relationship_routes, user_routes

# Crear aplicación FastAPI
app = FastAPI(
    title="device_systems API",
    description="API REST segura para gestionar usuarios, dispositivos y prestamos en device_systems",
    version="3.0.0",
    contact={"name": "gilmaro6", "url": "https://github.com/gilmaro6/device_systems"},
    docs_url="/docs",
    redoc_url="/redoc"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(device_routes.router)
app.include_router(loan_routes.router)
app.include_router(relationship_routes.router)


@app.get(
    "/",
    response_class=HTMLResponse,
    summary="Página principal",
    description="Página de bienvenida a la API"
)
async def root():
    """
    Página principal de bienvenida a la API device_systems
    """
    return """
    <html>
        <head>
            <title>device_systems API</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background-color: #f5f5f5;
                }
                .container {
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 { color: #333; }
                p { color: #666; }
                .link { 
                    display: inline-block;
                    margin: 10px 10px 10px 0;
                    padding: 10px 15px;
                    background-color: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                }
                .link:hover { background-color: #0056b3; }
                .info { 
                    background-color: #e7f3ff;
                    padding: 15px;
                    border-left: 4px solid #007bff;
                    border-radius: 4px;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 Bienvenido a device_systems API</h1>
                <p>Esta es la API REST para la gestión de usuarios del sistema device_systems.</p>
                
                <div class="info">
                    <h3>📚 Documentación Interactiva</h3>
                    <p>Accede a la documentación y prueba los endpoints:</p>
                    <a href="/docs" class="link">Swagger UI</a>
                    <a href="/redoc" class="link">ReDoc</a>
                </div>
                
                <div class="info">
                    <h3>🔌 Endpoints Disponibles</h3>
                    <ul>
                        <li><strong>GET /users</strong> - Obtener todos los usuarios</li>
                        <li><strong>GET /users/{user_id}</strong> - Obtener usuario por ID</li>
                        <li><strong>POST /users</strong> - Crear nuevo usuario</li>
                        <li><strong>PUT /users/{user_id}</strong> - Reemplazar usuario</li>
                        <li><strong>PATCH /users/{user_id}</strong> - Actualizar parcialmente</li>
                        <li><strong>DELETE /users/{user_id}</strong> - Eliminar usuario</li>
                        <li><strong>GET /users?role=admin</strong> - Filtrar por rol</li>
                        <li><strong>GET /users?is_active=true</strong> - Filtrar por estado</li>
                    </ul>
                </div>
                
                <div class="info">
                    <h3>📦 Cabeceras HTTP Personalizadas</h3>
                    <p>Todas las respuestas incluyen:</p>
                    <ul>
                        <li><strong>X-App-Name</strong>: device_systems</li>
                        <li><strong>X-API-Version</strong>: 3.0.0</li>
                    </ul>
                </div>
            </div>
        </body>
    </html>
    """


@app.get("/health", summary="Health Check", description="Verifica que la API esté funcionando")
async def health_check():
    """
    Endpoint para verificar que la API está en línea
    """
    return {
        "status": "healthy",
        "service": "device_systems",
        "version": "3.0.0"
    }


# Middleware para agregar cabeceras personalizadas
@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    """
    Middleware que agrega cabeceras HTTP personalizadas a todas las respuestas
    """
    started_at = time.perf_counter()
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    response = await call_next(request)
    response.headers["X-App-Name"] = settings.app_name
    response.headers["X-API-Version"] = settings.api_version
    response.headers["X-Process-Time"] = f"{time.perf_counter() - started_at:.6f}"
    response.headers["X-Request-ID"] = request_id
    return response


# Manejador de excepciones global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Manejador global de excepciones
    """
    return JSONResponse(
        status_code=500,
        content={"error": True, "message": "Ocurrio un error en el servidor"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True
    )
