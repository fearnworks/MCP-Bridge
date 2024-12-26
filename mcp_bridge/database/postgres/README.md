# PostgreSQL Support

This module provides PostgreSQL database support for MCP-Bridge.

## Quick Start

1. Start the PostgreSQL database using Docker Compose from the project root:
```bash
docker compose -f mcp_bridge/database/postgres/postgres-compose.yml up -d
```

2. Configure MCP-Bridge to use PostgreSQL in your config.json:
```

## Dependencies

Ensure you have the required PostgreSQL dependency installed:
```bash
pip install asyncpg
```


## Troubleshooting

1. Verify database connection:
```bash
docker compose -f mcp_bridge/database/postgres/docker-compose.yml ps
```

2. View database logs:
```bash
docker compose -f mcp_bridge/database/postgres/docker-compose.yml logs postgres
```

To add with defaults from the compose file add this section to your config.json:
```json
"database": {
    "engine": "postgresql",
    "postgresql": {
        "host": "localhost",
        "port": 45432,
        "username": "postgres",
        "password": "password",
        "database": "monitoring"
    }
}
```
