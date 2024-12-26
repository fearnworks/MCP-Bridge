# Database Module

This module provides database integration for MCP-Bridge using SQLAlchemy's URL system.

## Currently Supported Databases

- SQLite (default)
- PostgreSQL

## Architecture

The database module uses SQLAlchemy's built-in URL system for database connections and configuration.

## Usage

The database can be configured through the config.json file:

```json
{
    "database": {
        "type": "postgresql",
        "postgres": {
            "host": "localhost",
            "port": 45432,
            "user": "postgres",
            "password": "password",
            "database": "monitoring"
        }
    }
}
```