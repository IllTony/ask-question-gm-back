from src.core.settings import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Создаём движок и подключение к БД
async_engine = create_async_engine(
    url=settings.database_url_async, echo=settings.DB_ECHO, future=True
)

# Создаём фабрику асинхронных сессий
async_session_maker = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session():
    async with async_session_maker() as session:
        yield session
