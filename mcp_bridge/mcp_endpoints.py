from fastapi import APIRouter, HTTPException
from mcp_clients.McpClientManager import ClientManager
from mcp.types import ListToolsResult, ListResourcesResult
from openapi_tags import Tag

router = APIRouter(prefix="/mcp", tags=[Tag.mcp_management])


@router.get("/tools")
async def get_tools() -> dict[str, ListToolsResult]:
    """Get all tools from all MCP clients"""

    tools = {}

    for name, client in ClientManager.get_clients():
        tools[name] = await client.list_tools()

    return tools

@router.get("/resources")
async def get_resources() -> dict[str, ListResourcesResult]:
    """Get all resources from all MCP clients"""

    resources = {}

    for name, client in ClientManager.get_clients():
        resources[name] = await client.list_resources()

    return resources

@router.get("/servers")
async def get_servers() -> list[str]:
    """List all enabled MCP servers"""
    return [name for name, _ in ClientManager.get_clients()]

@router.get("/servers/all")
async def get_all_servers() -> list[dict[str, bool | str]]:
    """List all MCP servers (both enabled and disabled) with their status"""
    return [
        {
            "name": name,
            "enabled": ClientManager.is_client_enabled(name)
        }
        for name in ClientManager.clients.keys()
    ]

@router.post("/tools/{tool_name}/disable")
async def disable_tool(tool_name: str) -> dict[str, bool]:
    """Disable a specific tool"""
    # Verify tool exists
    client = await ClientManager.get_client_from_tool(tool_name)
    if not client:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    success = ClientManager.disable_tool(tool_name)
    return {"success": success}

@router.post("/tools/{tool_name}/enable")
async def enable_tool(tool_name: str) -> dict[str, bool]:
    """Enable a specific tool"""
    # Verify tool exists
    client = await ClientManager.get_client_from_tool(tool_name)
    if not client:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    success = ClientManager.enable_tool(tool_name)
    return {"success": success}

@router.get("/tools/{tool_name}/status")
async def get_tool_status(tool_name: str) -> dict[str, bool]:
    """Get the enabled/disabled status of a tool"""
    # Verify tool exists
    client = await ClientManager.get_client_from_tool(tool_name)
    if not client:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    return {"enabled": ClientManager.is_tool_enabled(tool_name)}
