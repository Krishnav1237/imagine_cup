"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.core.database import init_db
from app.api.v1 import auth
from app.api.v1 import content,analytics
# from app.api.v1 import learning

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered learning platform for ADHD learners"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["authentication"]
)
app.include_router(
    content.router,
    prefix=f"{settings.API_V1_PREFIX}/content",
    tags=["content"]
)
#app.include_router(
#    learning.router,
#    prefix=f"{settings.API_V1_PREFIX}/learning",
#    tags=["learning"]
#)
app.include_router(
   analytics.router,
    prefix=f"{settings.API_V1_PREFIX}/analytics",
    tags=["analytics"]
)

# Mount static files (for local file serving)
if settings.is_local:
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/files", StaticFiles(directory=str(upload_dir)), name="files")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📍 Deployment Mode: {settings.DEPLOYMENT_MODE}")
    
    # Initialize database
    init_db()
    
    print(f"✅ Application started successfully")
    print(f"📖 API Documentation: http://localhost:8000/docs")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "mode": settings.DEPLOYMENT_MODE,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mode": settings.DEPLOYMENT_MODE,
        "version": settings.VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload in development
    )