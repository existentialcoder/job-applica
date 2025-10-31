from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    BACKEND_CORS_ORIGINS: list[str] = []
    LOG_LEVEL: str = 'INFO'

    class Config:
        env_file = '.env'
        case_sensitive = True


settings = Settings()
