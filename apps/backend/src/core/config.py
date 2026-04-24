from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    AUTH_SECRET: str
    BACKEND_CORS_ORIGINS: list[str] = ['http://localhost:5173', 'http://localhost:8000']
    LOG_LEVEL: str = 'INFO'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OAuth
    GOOGLE_CLIENT_ID: str = ''
    GOOGLE_CLIENT_SECRET: str = ''
    LINKEDIN_CLIENT_ID: str = ''
    LINKEDIN_CLIENT_SECRET: str = ''
    FRONTEND_URL: str = 'http://localhost:5173'
    BACKEND_URL: str = 'http://localhost:8000'

    class Config:
        env_file = '.env'
        case_sensitive = True


settings = Settings()
