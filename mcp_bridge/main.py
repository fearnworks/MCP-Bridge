from fastapi import FastAPI
from endpoints import router as endpointRouter
from mcp_endpoints import router as api_router
from web.router import router as web_router
from mcpManagement import router as mcpRouter
from health import router as healthRouter
from lifespan import lifespan
from openapi_tags import tags_metadata

app = FastAPI(
    title="MCP Bridge",
    description="A middleware application to add MCP support to openai compatible apis",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

app.include_router(endpointRouter)
app.include_router(api_router)
app.include_router(healthRouter)
app.include_router(web_router)

if __name__ == "__main__":
    import uvicorn
    from config import config

    uvicorn.run(app, host=config.network.host, port=config.network.port)
