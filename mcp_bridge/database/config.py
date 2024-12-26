from functools import lru_cache
from config import config

@lru_cache()
def get_database_config():
    """Get database configuration from main config"""
    db_config = config.database
    
    if db_config.type == "sqlite":
        return {
            "type": "sqlite",
            "url": f"sqlite+aiosqlite:///{db_config.sqlite.database}"
        }
    elif db_config.type == "postgres":
        if not db_config.postgres:
            raise ValueError("PostgreSQL configuration is required when using postgres database type")
        return {
            "type": "postgres",
            "url": f"postgresql+asyncpg://{db_config.postgres.username}:{db_config.postgres.password}@{db_config.postgres.host}:{db_config.postgres.port}/{db_config.postgres.database}"
        }
    raise ValueError(f"Unsupported database type: {db_config.type}")