from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from mcp_clients.McpClientManager import ClientManager
from database.session import get_db
from database.models import ChatCompletion, ToolCall

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
async def view_logs(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # Get completions with tool counts using SQLAlchemy
    stmt = (
        select(ChatCompletion)
        .options(selectinload(ChatCompletion.tool_calls))
        .order_by(ChatCompletion.timestamp.desc())
        .limit(100)
    )
    
    result = await db.execute(stmt)
    completions = result.scalars().all()
    
    return templates.TemplateResponse(
        "logs.html",
        {
            "request": request,
            "completions": [
                {
                    "id": c.id,
                    "timestamp": c.timestamp,
                    "model": c.model,
                    "total_tokens": c.total_tokens,
                    "tool_count": len(c.tool_calls) if c.tool_calls else 0
                }
                for c in completions
            ]
        }
    )

@router.get("/logs/{completion_id}")
async def get_completion_details(
    completion_id: str,
    db: AsyncSession = Depends(get_db)
):
    # Get completion with related tool calls
    stmt = (
        select(ChatCompletion)
        .options(selectinload(ChatCompletion.tool_calls))
        .where(ChatCompletion.id == completion_id)
    )
    
    result = await db.execute(stmt)
    completion = result.scalar_one_or_none()
    
    if not completion:
        return JSONResponse(
            {"error": f"Completion '{completion_id}' not found"},
            status_code=404
        )
    
    # Format the response to match the expected structure
    return JSONResponse({
        "completion": {
            "id": completion.id,
            "timestamp": completion.timestamp.isoformat(),
            "model": completion.model,
            "request": completion.request,
            "final_response": completion.final_response,
            "total_tokens": completion.total_tokens,
            "completion_tokens": completion.completion_tokens,
            "prompt_tokens": completion.prompt_tokens,
        },
        "tool_calls": [
            {
                "id": t.id,
                "tool_name": t.tool_name,
                "arguments": t.arguments,  # This should already be a JSON string
                "result": t.result,       # This should be a dict
                "timestamp": t.timestamp.isoformat() if t.timestamp else None
            }
            for t in sorted(completion.tool_calls, key=lambda x: x.timestamp or "")
        ]
    })