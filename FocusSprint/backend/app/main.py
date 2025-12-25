"""
Main FastAPI application entry point.
Configures middleware, routers, and startup events.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.core.database import init_db
from app.api.v1 import auth, content, analytics, gamification

# Configure Centralized Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("FocusSprint")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    logger.info(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    
    # Initialize Database
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise e
        
    # Create upload directory
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"📂 Serving uploads from: {upload_dir.absolute()}")
    
    yield
    
    logger.info("🛑 Shutting down application...")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FocusSprint API - ADHD Learning Platform",
    lifespan=lifespan
)

# 1. CORS Configuration
origins = settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Include Routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"]
)
app.include_router(
    content.router,
    prefix=f"{settings.API_V1_PREFIX}/content",
    tags=["Content"]
)
app.include_router(
    analytics.router,
    prefix=f"{settings.API_V1_PREFIX}/analytics",
    tags=["Analytics"]
)
app.include_router(
    gamification.router,
    prefix=f"{settings.API_V1_PREFIX}/gamification",
    tags=["Gamification"]
)

# ADHD Learning Features (NEW)
from app.api.v1 import adhd_learning
app.include_router(
    adhd_learning.router,
    prefix=f"{settings.API_V1_PREFIX}/adhd-learning",
    tags=["ADHD Learning"]
)

# WebSocket for Real-Time Updates
from app.api.v1 import websocket
app.include_router(
    websocket.router,
    prefix="/ws",
    tags=["WebSocket"]
)

# 3. Mount Static Files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

@app.get("/")
async def root():
    """
    Health check root endpoint.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "status": "active",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )