from typing import Dict, Type
from .engine_interface import DatabaseEngineInterface
from .sqlite.engine import SQLiteEngine
from .postgres.engine import PostgresEngine

class DatabaseEngineFactory:
    _engines: Dict[str, Type[DatabaseEngineInterface]] = {
        "sqlite": SQLiteEngine,
        "postgresql": PostgresEngine
    }

    @classmethod
    def register_engine(cls, name: str, engine_class: Type[DatabaseEngineInterface]):
        """Register a new database engine type"""
        cls._engines[name] = engine_class

    @classmethod
    def create_engine(cls, engine_type: str) -> DatabaseEngineInterface:
        """Create an instance of the specified engine type"""
        if engine_type not in cls._engines:
            raise ValueError(f"Unsupported database type: {engine_type}")
        
        return cls._engines[engine_type]()

    @classmethod
    def get_supported_engines(cls) -> list[str]:
        """Get list of supported database engines"""
        return list(cls._engines.keys())