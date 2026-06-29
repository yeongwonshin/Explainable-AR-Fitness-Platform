from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "explainable-ar-fitness-platform"
    app_env: str = os.getenv("APP_ENV", "dev")
    model_dir: Path = Path(os.getenv("MODEL_DIR", "models"))
    visibility_threshold: float = 0.5
    cors_origins: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
