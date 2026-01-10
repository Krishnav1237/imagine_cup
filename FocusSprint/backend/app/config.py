"""
Configuration system that auto-detects deployment mode and loads appropriate settings.
Supports both local development (SQLite, local storage) and Azure production.
"""

import os
from enum import Enum
from typing import Optional, List
from functools import lru_cache

from pydantic_settings import BaseSettings


class DeploymentMode(str, Enum):
    LOCAL = "local"
    AZURE = "azure"


class Settings(BaseSettings):
    # -----------------------------
    # Core App
    # -----------------------------
    PROJECT_NAME: str = "FocusSprint"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    ENV: str = "development"
    DEPLOYMENT_MODE: Optional[DeploymentMode] = None

    # -----------------------------
    # Security
    # -----------------------------
    SECRET_KEY: str = "dev_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # -----------------------------
    # CORS
    # -----------------------------
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "https://focussprint.vercel.app",
    ]

    # -----------------------------
    # Database
    # -----------------------------
    DATABASE_URL: Optional[str] = None
    LOCAL_DB_PATH: str = "./focussprint.db"

    AZURE_DB_SERVER: Optional[str] = None
    AZURE_DB_NAME: Optional[str] = None
    AZURE_DB_USER: Optional[str] = None
    AZURE_DB_PASSWORD: Optional[str] = None

    # -----------------------------
    # Storage
    # -----------------------------
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100 MB

    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_CONTAINER: str = "content"

    # -----------------------------
    # AI / LLM Settings
    # -----------------------------

    # 🔹 Cloud chunking (Azure OpenAI) — disabled by default
    ENABLE_CLOUD_CHUNKING: bool = False

    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4"

    # 🔹 Local LLM (Ollama)
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b-instruct-q4_K_M"
    OLLAMA_EMBED_MODEL: str= "nomic-embed-text"
    OLLAMA_TIMEOUT_SECONDS: int = 120

    # 🔹 OpenAI / VLM
    OPENAI_API_KEY: Optional[str] = None
    VLM_MODEL: str = "gpt-4o"
    ENABLE_VLM: bool = True
    VLM_FRAME_SAMPLE_RATE: int = 2

    # Video
    MAX_VIDEO_DURATION_MINUTES: int = 60

    # -----------------------------
    # Processing thresholds
    # -----------------------------
    CHUNK_MIN_DURATION: int = 120
    CHUNK_MAX_DURATION: int = 300
    SHORT_CONTENT_THRESHOLD: int = 600

    # -----------------------------
    # Pydantic config
    # -----------------------------
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    # -----------------------------
    # Init hooks
    # -----------------------------
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._auto_detect_mode()
        self._setup_database()

    def _auto_detect_mode(self):
        if self.DEPLOYMENT_MODE:
            return

        azure_indicators = [
            self.AZURE_DB_SERVER,
            self.AZURE_STORAGE_CONNECTION_STRING,
            os.getenv("WEBSITE_SITE_NAME"),
        ]

        self.DEPLOYMENT_MODE = (
            DeploymentMode.AZURE if any(azure_indicators) else DeploymentMode.LOCAL
        )

    def _setup_database(self):
        if self.DATABASE_URL:
            return

        if self.DEPLOYMENT_MODE == DeploymentMode.LOCAL:
            db_dir = os.path.dirname(self.LOCAL_DB_PATH)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            self.DATABASE_URL = f"sqlite:///{self.LOCAL_DB_PATH}"
        else:
            if all(
                [
                    self.AZURE_DB_SERVER,
                    self.AZURE_DB_NAME,
                    self.AZURE_DB_USER,
                    self.AZURE_DB_PASSWORD,
                ]
            ):
                self.DATABASE_URL = (
                    f"postgresql://{self.AZURE_DB_USER}:{self.AZURE_DB_PASSWORD}"
                    f"@{self.AZURE_DB_SERVER}/{self.AZURE_DB_NAME}"
                )

    # -----------------------------
    # Convenience flags
    # -----------------------------
    @property
    def is_local(self) -> bool:
        return self.DEPLOYMENT_MODE == DeploymentMode.LOCAL

    @property
    def is_azure(self) -> bool:
        return self.DEPLOYMENT_MODE == DeploymentMode.AZURE


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Global singleton
settings = get_settings()
