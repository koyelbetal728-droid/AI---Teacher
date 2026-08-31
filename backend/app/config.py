# config.py
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# backend/
BASE_DIR = Path(__file__).resolve().parent.parent

# ai-teacher/
PROJECT_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------

    app_name: str = "AI Teacher"
    app_env: str = "development"
    debug: bool = True

    host: str = "0.0.0.0"
    port: int = 8000

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------

    database_url: str = "sqlite:///./ai_teacher.db"

    # ---------------------------------------------------------
    # Ollama / Local LLM
    # ---------------------------------------------------------

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # ---------------------------------------------------------
    # Data directories
    # ---------------------------------------------------------

    upload_dir: str = "../data/uploads"
    processed_dir: str = "../data/processed"
    vector_store_dir: str = "../data/vector_store"

    generated_audio_dir: str = "../data/generated_audio"
    generated_visuals_dir: str = "../data/generated_visuals"
    generated_videos_dir: str = "../data/generated_videos"

    # ---------------------------------------------------------
    # Upload settings
    # ---------------------------------------------------------

    max_upload_size_mb: int = 25

    # ---------------------------------------------------------
    # Security
    # ---------------------------------------------------------

    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # ---------------------------------------------------------
    # Environment file
    # ---------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # ---------------------------------------------------------
    # Helper
    # ---------------------------------------------------------

    def get_absolute_path(self, path: str) -> Path:
        """
        Convert a relative project path into an absolute path.
        """

        path_object = Path(path)

        if path_object.is_absolute():
            return path_object

        return (PROJECT_ROOT / path_object).resolve()


# Global settings instance
settings = Settings()