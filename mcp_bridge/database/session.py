from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from .models import Base
from .config import get_database_config
from .engine_factory import DatabaseEngineFactory

class DatabaseSession:
    def __init__(self):
        self.engine = None
        self.session_maker = None

    async def initialize(self):
        config = get_database_config()
        engine_instance = DatabaseEngineFactory.create_engine(config.type)
        connection_params = config.model_dump(exclude_none=True)
        self.engine = await engine_instance.create_engine(connection_params)
        self.session_maker = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def get_session(self):
        if not self.session_maker:
            await self.initialize()
        async with self.session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

db = DatabaseSession()
get_db = db.get_session