from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from typing import Dict, Any
from ..engine_interface import DatabaseEngineInterface

class PostgresEngine(DatabaseEngineInterface):
    async def create_engine(self, connection_params: Dict[str, Any]) -> AsyncEngine:
        connection_string = self.get_connection_string(connection_params)
        return create_async_engine(
            connection_string,
            **self.get_engine_options()
        )

    def get_connection_string(self, connection_params: Dict[str, Any]) -> str:
        host = connection_params.get('host', 'localhost')
        port = connection_params.get('port', 5432)
        username = connection_params.get('username', '')
        password = connection_params.get('password', '')
        database = connection_params.get('database', 'monitoring')
        
        return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"

    def get_engine_options(self) -> Dict[str, Any]:
        return {
            "echo": False,
            "pool_size": 5,
            "max_overflow": 10
        }