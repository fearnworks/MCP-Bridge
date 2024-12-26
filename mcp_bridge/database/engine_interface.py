from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncEngine
from typing import Dict, Any

class DatabaseEngineInterface(ABC):
    """Interface for database engine implementations"""
    
    @abstractmethod
    async def create_engine(self, connection_params: Dict[str, Any]) -> AsyncEngine:
        """Create and configure a database engine"""
        pass

    @abstractmethod
    def get_connection_string(self, connection_params: Dict[str, Any]) -> str:
        """Get the connection string for this database type"""
        pass

    @abstractmethod
    def get_engine_options(self) -> Dict[str, Any]:
        """Get database-specific engine options"""
        pass