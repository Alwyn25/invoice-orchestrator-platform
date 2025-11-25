from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Manages application settings and configurations."""

    # MCP Service Configuration
    MCP_HOST: str = "localhost"
    MCP_PORT: int = 50051

    # Agent Services Configuration
    EXTRACTION_AGENT_HOST: str = "localhost"
    EXTRACTION_AGENT_PORT: int = 6001

    MAPPING_AGENT_HOST: str = "localhost"
    MAPPING_AGENT_PORT: int = 6002

    VALIDATION_AGENT_HOST: str = "localhost"
    VALIDATION_AGENT_PORT: int = 6003

    REPORT_AGENT_HOST: str = "localhost"
    REPORT_AGENT_PORT: int = 6004

    CONVERSION_AGENT_HOST: str = "localhost"
    CONVERSION_AGENT_PORT: int = 6005

    INTEGRATION_AGENT_HOST: str = "localhost"
    INTEGRATION_AGENT_PORT: int = 6006

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

@lru_cache()
def get_settings():
    """Returns a cached instance of the Settings."""
    return Settings()
