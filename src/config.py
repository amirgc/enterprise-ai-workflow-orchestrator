"""Application configuration loaded from environment variables.

Uses Pydantic's BaseSettings to:
1. Load values from a .env file automatically
2. Validate types (e.g., ensure LOG_LEVEL is a valid choice)
3. Provide type hints so your editor gives autocomplete
"""

from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    """Valid log levels. Inheriting from str lets you compare with plain strings."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Provider(str, Enum):
    """Supported LLM providers."""
    CLAUDE = "claude"
    OPENAI = "openai"


class Settings(BaseSettings):
    """All app configuration in one place.

    Pydantic reads each field from the environment variable with the SAME NAME
    (case-insensitive). The 'default' value is used if the env var isn't set.
    """

    model_config = SettingsConfigDict(
        env_file=".env",        # load variables from .env file
        env_file_encoding="utf-8",
        case_sensitive=False,   # ANTHROPIC_API_KEY == anthropic_api_key
    )

    # API keys — no defaults, so the app errors if they're missing
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Provider settings
    default_provider: Provider = Provider.CLAUDE
    claude_model: str = "claude-sonnet-4-20250514"
    openai_model: str = "gpt-4o"

    # App settings
    log_level: LogLevel = LogLevel.INFO


# Create a single shared instance — import this everywhere
# Example: from src.config import settings
settings = Settings()
