# FastAPI app + OpenTelemetry initialization

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import settings
#from app.config.telemetry import setup_opentelemetry
from app.api.v1.router import api_router
from app.core.exceptions import setup_exception_handlers
import logging
from fastapi.responses import RedirectResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Civi Chat API...")
    yield
    # Shutdown
    logger.info("Shutting down Civi Chat API...")

app = FastAPI(
    title="Civi Chat API",
    description="AI-powered civic engagement platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure OpenTelemetry
'''
tracer, meter = setup_opentelemetry(
    app=app,
    service_name=settings.SERVICE_NAME,
    otlp_endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT
)
'''
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include API routers
app.include_router(api_router, prefix="/api/v1")



@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "civi-chat-api"}
