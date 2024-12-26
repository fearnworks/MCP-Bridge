from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import aiosqlite
import json
from datetime import datetime
from mcp_clients.McpClientManager import ClientManager

router = APIRouter()
templates = Jinja2Templates(directory="mcp_bridge/templates")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Get all servers
    servers = [
        {
            "name": name,
            "enabled": ClientManager.is_client_enabled(name)
        }
        for name in ClientManager.clients.keys()
    ]

    # Get all tools
    tools = {}
    tool_status = {}
    for name, client in ClientManager.get_clients():
        tools[name] = await client.list_tools()
        for tool in tools[name].tools:
            tool_status[tool.name] = ClientManager.is_tool_enabled(tool.name)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "servers": servers,
            "tools": tools,
            "tool_status": tool_status
        }
    )

@router.get("/logs", response_class=HTMLResponse)
async def view_logs(request: Request):
    async with aiosqlite.connect("monitoring.db") as db:
        db.row_factory = aiosqlite.Row
        
        # Get completions with tool counts
        cursor = await db.execute("""
            SELECT 
                c.*,
                COUNT(t.id) as tool_count
            FROM chat_completions c
            LEFT JOIN tool_calls t ON c.id = t.chat_completion_id
            GROUP BY c.id
            ORDER BY c.timestamp DESC
            LIMIT 100
        """)
        
        completions = await cursor.fetchall()
        
        return templates.TemplateResponse(
            "logs.html",
            {
                "request": request,
                "completions": [dict(row) for row in completions]
            }
        )

@router.get("/logs/{completion_id}")
async def get_completion_details(completion_id: str):
    async with aiosqlite.connect("monitoring.db") as db:
        db.row_factory = aiosqlite.Row
        
        # Get completion details
        cursor = await db.execute(
            "SELECT * FROM chat_completions WHERE id = ?",
            (completion_id,)
        )
        completion = await cursor.fetchone()
        
        # Get tool calls
        cursor = await db.execute(
            "SELECT * FROM tool_calls WHERE chat_completion_id = ?",
            (completion_id,)
        )
        tool_calls = await cursor.fetchall()
        
        return JSONResponse({
            "completion": dict(completion),
            "tool_calls": [dict(tool) for tool in tool_calls]
        })