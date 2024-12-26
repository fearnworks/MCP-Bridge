from typing import Literal, Optional
from pydantic import BaseModel, Field
from functools import lru_cache
import os

DatabaseType = Literal["sqlite", "postgresql"]

class DatabaseConfig(BaseModel):
    type: DatabaseType = Field(
        default="sqlite",
        description="Database type to use"
    )
    host: Optional[str] = Field(
        default=None,
        description="Database host (PostgreSQL only)"
    )
    port: Optional[int] = Field(
        default=None,
        description="Database port (PostgreSQL only)"
    )
    username: Optional[str] = Field(
        default=None,
        description="Database username (PostgreSQL only)"
    )
    password: Optional[str] = Field(
        default=None,
        description="Database password (PostgreSQL only)"
    )
    database: str = Field(
        default="monitoring.db",
        description="Database name or path"
    )

    def get_connection_string(self) -> str:
        """Generate the database connection string based on configuration"""
        if self.type == "sqlite":
            return f"sqlite+aiosqlite:///{self.database}"
        elif self.type == "postgresql":
            return (
                f"postgresql+asyncpg://{self.username}:{self.password}"
                f"@{self.host}:{self.port}/{self.database}"
            )
        raise ValueError(f"Unsupported database type: {self.type}")

@lru_cache()
def get_database_config() -> DatabaseConfig:
    """Get database configuration from environment variables"""
    return DatabaseConfig(
        type=os.getenv("DB_TYPE", "sqlite"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        username=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE", "monitoring.db")
    )