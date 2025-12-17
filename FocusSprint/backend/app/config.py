"""
Configuration system that auto-detects deployment mode and loads appropriate settings.
Supports both local development (SQLite, local storage) and Azure production.
"""
import os
from enum import Enum
from typing import Optional, List
from pydantic_settings import BaseSettings
from functools import lru_cache

class DeploymentMode(str, Enum):
    LOCAL = "local"
    AZURE = "azure"

class Settings(BaseSettings):
    # Core settings
    PROJECT_NAME: str = "FocusSprint"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Deployment mode (auto-detect or explicit)
    DEPLOYMENT_MODE: Optional[DeploymentMode] = None
    ENV: str = "development" # fallback
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - Allow Next.js frontend
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        "http://localhost:8000",  # FastAPI dev server
        "https://focussprint.vercel.app" # Example production domain
    ]
    
    # Database settings (auto-select based on mode)
    DATABASE_URL: Optional[str] = None
    
    # Local SQLite settings
    LOCAL_DB_PATH: str = "./focussprint.db"
    
    # Azure PostgreSQL settings (Env vars usually provided by Azure App Service)
    AZURE_DB_SERVER: Optional[str] = None
    AZURE_DB_NAME: Optional[str] = None
    AZURE_DB_USER: Optional[str] = None
    AZURE_DB_PASSWORD: Optional[str] = None
    
    # Storage settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Azure Blob Storage settings
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_CONTAINER: str = "content"
    
    # --- AI Services ---
    
    # Azure OpenAI (Replacement for Anthropic/Claude)
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
    
    # Azure Speech/Whisper settings (Optional)
    AZURE_SPEECH_KEY: Optional[str] = None
    AZURE_SPEECH_REGION: Optional[str] = "eastus"
    
    # Processing settings
    CHUNK_MIN_DURATION: int = 120  # 2 minutes
    CHUNK_MAX_DURATION: int = 300  # 5 minutes
    SHORT_CONTENT_THRESHOLD: int = 600  # 10 minutes - process synchronously
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore" # Allow extra env vars without error
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-detect deployment mode if not set
        self._auto_detect_mode()
        # Set database URL based on mode
        self._setup_database()
    
    def _auto_detect_mode(self):
        """Auto-detect deployment mode based on environment variables"""
        if self.DEPLOYMENT_MODE:
            return
        
        # Check for Azure-specific env vars to verify if we are in cloud environment
        azure_indicators = [
            self.AZURE_DB_SERVER,
            self.AZURE_STORAGE_CONNECTION_STRING,
            os.getenv("WEBSITE_SITE_NAME") # Common Azure App Service var
        ]
        
        if any(azure_indicators):
            self.DEPLOYMENT_MODE = DeploymentMode.AZURE
        else:
            self.DEPLOYMENT_MODE = DeploymentMode.LOCAL
    
    def _setup_database(self):
        """Setup database URL based on deployment mode"""
        if self.DATABASE_URL:
            return  # Explicit URL provided in .env takes precedence
        
        if self.DEPLOYMENT_MODE == DeploymentMode.LOCAL:
            # SQLite for local development
            # Ensure directory exists if path uses subfolders
            db_dir = os.path.dirname(self.LOCAL_DB_PATH)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            self.DATABASE_URL = f"sqlite:///{self.LOCAL_DB_PATH}"
        else:
            # PostgreSQL for Azure
            if all([self.AZURE_DB_SERVER, self.AZURE_DB_NAME, 
                   self.AZURE_DB_USER, self.AZURE_DB_PASSWORD]):
                self.DATABASE_URL = (
                    f"postgresql://{self.AZURE_DB_USER}:{self.AZURE_DB_PASSWORD}"
                    f"@{self.AZURE_DB_SERVER}/{self.AZURE_DB_NAME}"
                )
            else:
                # Log warning or handle missing DB config for Azure
                pass
    
    @property
    def is_local(self) -> bool:
        return self.DEPLOYMENT_MODE == DeploymentMode.LOCAL
    
    @property
    def is_azure(self) -> bool:
        return self.DEPLOYMENT_MODE == DeploymentMode.AZURE

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()