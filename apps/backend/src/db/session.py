from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from ..core.config import settings

_url = settings.DATABASE_URL
# Coerce bare postgresql:// → postgresql+asyncpg:// so create_async_engine picks the right driver
if _url.startswith('postgresql://') or _url.startswith('postgres://'):
    _url = _url.replace('://', '+asyncpg://', 1)
DATABASE_URL = _url

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.LOG_LEVEL == 'debug',
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
