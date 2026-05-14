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

    # Feature flags — override via env vars (FEATURE_PLUGINS=false, etc.)
    FEATURE_DASHBOARD: bool = True
    FEATURE_BOARDS: bool = True
    FEATURE_PLUGINS: bool = False
    FEATURE_GMAIL: bool = True
    FEATURE_CALENDAR: bool = True
    FEATURE_GOOGLE_OAUTH: bool = True
    FEATURE_LINKEDIN_OAUTH: bool = False
    FEATURE_BROWSER_EXTENSION: bool = True

    class Config:
        env_file = '.env'
        case_sensitive = True


settings = Settings()


def get_feature_flags() -> dict[str, bool]:
    return {
        'dashboard': settings.FEATURE_DASHBOARD,
        'boards': settings.FEATURE_BOARDS,
        'plugins': settings.FEATURE_PLUGINS,
        'gmail': settings.FEATURE_GMAIL,
        'calendar': settings.FEATURE_CALENDAR,
        'google_oauth': settings.FEATURE_GOOGLE_OAUTH,
        'linkedin_oauth': settings.FEATURE_LINKEDIN_OAUTH,
        'browser_extension': settings.FEATURE_BROWSER_EXTENSION,
    }
