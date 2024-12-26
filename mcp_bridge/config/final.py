from typing import Annotated, Literal, Union, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field

from mcp.client.stdio import StdioServerParameters


class InferenceServer(BaseModel):
    base_url: str = Field(description="Base URL of the inference server")
    api_key: str = Field(
        default="unauthenticated", description="API key for the inference server"
    )


class Logging(BaseModel):
    log_level: Literal["INFO", "DEBUG"] = Field("INFO", description="default log level")
    log_server_pings: bool = Field(False, description="log server pings")


class SSEMCPServer(BaseModel):
    # TODO: expand this once I find a good definition for this
    url: str = Field(description="URL of the MCP server")


MCPServer = Annotated[
    Union[StdioServerParameters, SSEMCPServer],
    Field(description="MCP server configuration"),
]


class Network(BaseModel):
    host: str = Field("0.0.0.0", description="Host of the network")
    port: int = Field(8000, description="Port of the network")


class SQLiteConfig(BaseModel):
    database: str = Field(default="monitoring.db", description="SQLite database path")


class PostgresConfig(BaseModel):
    host: str = Field(default="localhost", description="PostgreSQL host")
    port: int = Field(default=45432, description="PostgreSQL port")
    username: str = Field(default="postgres", description="PostgreSQL username")
    password: str = Field(default="password", description="PostgreSQL password")
    database: str = Field(default="monitoring", description="PostgreSQL database name")


class DatabaseConfig(BaseModel):
    type: Literal["sqlite", "postgres"] = Field(
        default="sqlite",
        description="Database type to use"
    )
    sqlite: SQLiteConfig = Field(
        default_factory=SQLiteConfig,
        description="SQLite configuration"
    )
    postgres: Optional[PostgresConfig] = Field(
        default_factory=PostgresConfig,
        description="PostgreSQL configuration"
    )


class UIConfig(BaseModel):
    bootstrap_css_url: str = Field(
        default="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
        description="URL for Bootstrap CSS"
    )
    bootstrap_js_url: str = Field(
        default="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js",
        description="URL for Bootstrap JavaScript"
    )


class Settings(BaseSettings):
    inference_server: InferenceServer = Field(
        description="Inference server configuration"
    )

    mcp_servers: dict[str, MCPServer] = Field(
        default_factory=dict, description="MCP servers configuration"
    )

    logging: Logging = Field(
        default_factory=lambda: Logging.model_construct(),
        description="logging config",
    )

    network: Network = Field(
        default_factory=lambda: Network.model_construct(),
        description="network config",
    )

    database: DatabaseConfig = Field(
        default_factory=DatabaseConfig,
        description="Database configuration"
    )

    ui: UIConfig = Field(
        default_factory=UIConfig,
        description="UI configuration"
    )

    model_config = SettingsConfigDict(
        env_prefix="MCP_BRIDGE__",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        cli_parse_args=True,
        cli_avoid_json=True,
    )
