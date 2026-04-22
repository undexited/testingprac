from functools import lru_cache
import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


class Settings:
    app_name: str = os.getenv("APP_NAME", "TestingPrac AI v2")
    app_env: str = os.getenv("APP_ENV", "development")
    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(os.getenv("APP_PORT", "8090"))

    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-change-me-change-me-1234")
    jwt_expires_minutes: int = int(os.getenv("JWT_EXPIRES_MINUTES", "10080"))

    _local_db_default = Path(os.getenv("LOCALAPPDATA", ".")) / "testingprac-ai-v2" / "app_v2_multi.db"
    _local_db_default.parent.mkdir(parents=True, exist_ok=True)
    _db_default_url = f"sqlite:///{_local_db_default.as_posix()}"
    database_url: str = os.getenv("DATABASE_URL", _db_default_url) or _db_default_url

    default_provider: str = os.getenv("DEFAULT_PROVIDER", "openai,anthropic,builtin")
    fast_model: str = os.getenv("FAST_MODEL", "local-fast")
    think_model: str = os.getenv("THINK_MODEL", "local-think")

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")


@lru_cache
def get_settings() -> Settings:
    return Settings()
