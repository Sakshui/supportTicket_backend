import uvloop
import asyncio
import os
import sys
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from prometheus_fastapi_instrumentator import Instrumentator

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.settings import get_settings
from app.utility import exception_handler, ApiResponse
from app.project_schemas import APIResponse
from app.cron import start_scheduler
from app.routers import routers 

settings = get_settings()

# ------------------------------------------------ FastAPI App ----------------------------------------------
app = FastAPI(
    title=settings.app.project_name,
    description = (
        "🎫 **Support Ticket System – Streamlined Issue Management**\n\n"
        "A lightweight backend service designed for merchants and customers to capture, track, "
        "and resolve shop-related issues or queries across multiple channels.\n\n"
        "**⚙️ Core Responsibilities**\n"
        "- 🧾 Enable creation and management of customer support tickets via API\n"
        "- 🔒 Support both authenticated (merchant/agent) and unauthenticated (customer) endpoints\n"
        "- 🏷️ Generate unique ticket IDs using outlet settings like prefix and sequence number\n"
        "- 📊 Provide grouped and filtered ticket insights for efficient tracking\n"
        "- 🤝 Improve customer–merchant communication with automated issue handling\n\n"
        "_🚀 Designed for clarity, scalability, and support efficiency._"
    ),
    version=settings.app.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ----------------------------------------- OpenAPI Security Scheme ----------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token. Format: Bearer <token>"
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ----------------------------------------- Global Exception Handler ----------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = await exception_handler(exc, request)
    response = APIResponse.error(message="Internal Server Error", code=HTTP_500_INTERNAL_SERVER_ERROR)
    response.data = {"traceback": tb}
    return ApiResponse(content=response.dict())

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    response = APIResponse.error(message=exc.detail, code=exc.status_code)
    return ApiResponse(content=response.dict())

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    response = APIResponse.error(message="Validation Error", code=422)
    response.data = {"errors": exc.errors()}
    return ApiResponse(content=response.dict())


# --------------------------------------------- Prometheus Metrics ------------------------------------------
Instrumentator().instrument(app).expose(app, include_in_schema=False)

# ------------------------------------------------ Middleware -----------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allowed_origins,
    allow_methods=settings.cors.allowed_methods,
    allow_headers=settings.cors.allowed_headers,
    allow_credentials=False,
)


# -------------------------------------------------- Base Routes -------------------------------------------------
@app.get("/", tags=["root"])
async def read_root():
    return {"message": "Hello, Xircls!"}

@app.get("/health", tags=["monitoring"])
async def health_check():
    return {"status": "ok"}

# ------------------------------------------------- Routers -------------------------------------------------
routers(app)

# --------------------------------------------- Lifespan Events ---------------------------------------------
@app.on_event("startup")
async def on_startup():
    start_scheduler()
    print("🟢 App is starting up...")

@app.on_event("shutdown")
async def on_shutdown():
    print("🔴 App is shutting down...")
