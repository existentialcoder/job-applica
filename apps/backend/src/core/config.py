from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    AUTH_SECRET: str
    BACKEND_CORS_ORIGINS: list[str] = []
    LOG_LEVEL: str = 'INFO'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = '.env'
        case_sensitive = True


settings = Settings()
