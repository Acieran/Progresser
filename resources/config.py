from pydantic import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost"

    class Config:
        env_file = ".env"


class Settings(BaseSettings):
    # Database
    DB_URL: PostgresDsn = Field(..., env="DATABASE_URL")
    DB_POOL_SIZE: int = 5

    # Auth
    SECRET_KEY: str = Field(..., min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # App
    DEBUG: bool = False
    ALLOWED_HOSTS: list[str] = ["localhost"]

    # Pydantic Config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra env vars
        case_sensitive=True
    )


# Singleton instance
settings = Settings()