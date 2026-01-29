"""Main FastAPI application for NYVO Insurance Advisor Chatbot"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core import settings
from app.models import init_db
from app.api import router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events"""
    # Startup
    logger.info("Starting NYVO Insurance Advisor Chatbot...")
    init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NYVO Insurance Advisor Chatbot...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="""
    ## NYVO Insurance Advisor Chatbot API
    
    AI-powered insurance advisor helping customers in India understand and purchase insurance products.
    
    ### Features:
    - 💬 **Chat Interface**: Natural language conversations about insurance
    - 🎯 **Smart Recommendations**: Personalized policy suggestions based on user needs
    - 📚 **Knowledge Base**: Educational content about insurance in India
    - 🔍 **Policy Comparison**: Compare multiple policies side by side
    
    ### Supported Insurance Types:
    - Health Insurance (Individual, Family Floater, Senior Citizen)
    - Term Life Insurance
    - Coming Soon: Motor, Travel Insurance
    
    ### Usage:
    1. Start a conversation using `/api/v1/chat`
    2. Get personalized recommendations via `/api/v1/recommend/health` or `/api/v1/recommend/term`
    3. Compare policies with `/api/v1/policy/compare`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS - allow all origins for API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["Insurance Advisor"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "description": "AI-powered insurance advisor for India",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
