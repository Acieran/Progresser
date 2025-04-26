from pydantic import BaseSettings



class Settings(BaseSettings):
    redis_url: str = "redis://localhost"

    class Config:
        env_file = ".env"


# api/dependencies.py
def get_settings() -> Settings:
    return Settings()


def get_redis(settings: Settings = Depends(get_settings)):
    return Redis.from_url(settings.redis_url)