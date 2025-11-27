# FastAPI app + OpenTelemetry initialization

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.settings import settings
from app.api.v1.router import api_router
from app.db.session import init_cosmos, close_cosmos
from app.core.exceptions import setup_exception_handlers
from app.db.mongodb import connect_to_cosmos, close_cosmos_connection
import logging
from fastapi.responses import RedirectResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Civi Chat API...")
    
    # Connect to Azure Cosmos DB
    logger.info("Connecting to Azure Cosmos DB...")
    await connect_to_cosmos()
    logger.info("Cosmos DB connected successfully")
    
    yield
    
    # Shutdown
    try:
        close_cosmos()
    except Exception:
        logger.exception("Error closing Cosmos client on shutdown")
    logger.info("Shutting down Civi Chat API...")
    await close_cosmos_connection()
    logger.info("Cosmos DB connection closed")

app = FastAPI(
    title="Civi Chat API",
    description="AI-powered civic engagement platform with Azure Cosmos DB backend",
    version="2.0.0",
    lifespan=lifespan
)


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
