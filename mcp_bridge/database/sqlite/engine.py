from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from typing import Dict, Any
from ..engine_interface import DatabaseEngineInterface

class SQLiteEngine(DatabaseEngineInterface):
    async def create_engine(self, connection_params: Dict[str, Any]) -> AsyncEngine:
        connection_string = self.get_connection_string(connection_params)
        return create_async_engine(
            connection_string,
            **self.get_engine_options()
        )

    def get_connection_string(self, connection_params: Dict[str, Any]) -> str:
        database = connection_params.get('database', 'monitoring.db')
        return f"sqlite+aiosqlite:///{database}"

    def get_engine_options(self) -> Dict[str, Any]:
        return {
            "echo": False,
            "connect_args": {
                "check_same_thread": False
            }
        }