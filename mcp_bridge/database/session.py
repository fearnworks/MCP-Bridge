from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from .models import Base
from .db_config import get_database_config
from loguru import logger

class DatabaseSession:
    def __init__(self):
        self.engine = None
        self.session_maker = None

    async def initialize(self):
        config = get_database_config()
        logger.info(f"Initializing database connection using {config['type'].upper()}")
        logger.info(f"Database URL: {config['url']}")

        # Base engine arguments
        engine_args = {
            'echo': False,
        }

        # Add pooling configuration only for PostgreSQL
        if config['type'].lower() == 'postgres':
            engine_args.update({
                'pool_size': 5,
                'max_overflow': 10
            })

        self.engine = create_async_engine(
            config['url'],
            **engine_args
        )

        # Create all tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")

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