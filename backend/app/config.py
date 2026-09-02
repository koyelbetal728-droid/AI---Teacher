# config.py
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # Application
    app_name: str = "AI Teacher"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # API
    api_prefix: str = "/api"

    # Database
    database_url: str = "sqlite:///./ai_teacher.db"

    # Security
    jwt_secret_key: str = "change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # File storage
    data_dir: str = str(BASE_DIR / "data")
    upload_dir: str = str(BASE_DIR / "data" / "uploads")
    processed_dir: str = str(BASE_DIR / "data" / "processed")
    vector_store_dir: str = str(BASE_DIR / "data" / "vector_store")
    generated_audio_dir: str = str(BASE_DIR / "data" / "generated_audio")
    generated_visuals_dir: str = str(BASE_DIR / "data" / "generated_visuals")
    generated_videos_dir: str = str(BASE_DIR / "data" / "generated_videos")

    # Upload limits
    max_upload_size_mb: int = 50
    allowed_file_types: str = "pdf,docx,pptx,txt"

    # CORS
    frontend_url: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def allowed_extensions(self) -> list[str]:
        return [
            extension.strip().lower()
            for extension in self.allowed_file_types.split(",")
            if extension.strip()
        ]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


settings = Settings()


def create_directories() -> None:
    """Create required application data directories."""
    directories = [
        settings.data_dir,
        settings.upload_dir,
        settings.processed_dir,
        settings.vector_store_dir,
        settings.generated_audio_dir,
        settings.generated_visuals_dir,
        settings.generated_videos_dir,
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


create_directories()