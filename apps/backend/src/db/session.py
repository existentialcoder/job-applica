from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=settings.LOG_LEVEL == 'debug',
    future=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
