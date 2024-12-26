from lmos_openai_types import (
    CreateChatCompletionRequest,
    CreateChatCompletionResponse,
    ChatCompletionRequestMessage,
)

from .utils import call_tool, chat_completion_add_tools
from .genericHttpxClient import client
from mcp_clients.McpClientManager import ClientManager
from tool_mappers import mcp2openai
from loguru import logger
import json
import sqlite3
import aiosqlite
import uuid
import asyncio


class ChatCompletionMonitor:
    def __init__(self, db_path="monitoring.db"):
        self.db_path = db_path
        # Create tables immediately using synchronous sqlite3
        with sqlite3.connect(self.db_path) as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS chat_completions (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    model TEXT,
                    request JSON,
                    final_response JSON,
                    total_tokens INTEGER,
                    completion_tokens INTEGER,
                    prompt_tokens INTEGER
                )
            """)
            
            db.execute("""
                CREATE TABLE IF NOT EXISTS tool_calls (
                    id TEXT PRIMARY KEY,
                    chat_completion_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tool_name TEXT,
                    arguments JSON,
                    result JSON,
                    FOREIGN KEY(chat_completion_id) REFERENCES chat_completions(id)
                )
            """)
            db.commit()

    async def log_chat_completion(self, completion_id: str, model: str, request: dict, response: dict):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO chat_completions (id, model, request, final_response, total_tokens, completion_tokens, prompt_tokens)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                completion_id,
                model,
                json.dumps(request),
                json.dumps(response),
                response.get("usage", {}).get("total_tokens"),
                response.get("usage", {}).get("completion_tokens"),
                response.get("usage", {}).get("prompt_tokens")
            ))
            await db.commit()

    async def log_tool_call(self, completion_id: str, tool_call: dict, result: dict):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO tool_calls (id, chat_completion_id, tool_name, arguments, result)
                VALUES (?, ?, ?, ?, ?)
            """, (
                tool_call.id,
                completion_id,
                tool_call.function.name,
                tool_call.function.arguments,
                json.dumps(result)
            ))
            await db.commit()

# Initialize monitor
monitor = ChatCompletionMonitor()

async def chat_completions(
    request: CreateChatCompletionRequest,
) -> CreateChatCompletionResponse:
    """performs a chat completion using the inference server"""
    
    # Generate unique ID for this completion
    completion_id = str(uuid.uuid4())
    
    request = await chat_completion_add_tools(request)

    while True:
        # logger.debug(request.model_dump_json())

        text = (
            await client.post(
                "/chat/completions",
                json=request.model_dump(
                    exclude_defaults=True, exclude_none=True, exclude_unset=True
                ),
            )
        ).text
        logger.debug(text)
        try:
            response = CreateChatCompletionResponse.model_validate_json(text)
        except Exception:
            logger.error(f"Failed to validate response: {text}")
            return

        msg = response.choices[0].message
        msg = ChatCompletionRequestMessage(
            role="assistant",
            content=msg.content,
            tool_calls=msg.tool_calls,
        )  # type: ignore
        request.messages.append(msg)

        logger.debug(f"finish reason: {response.choices[0].finish_reason}")
        if response.choices[0].finish_reason.value in ["stop", "length"]:
            logger.debug("no tool calls found")
            # Add monitoring
            await monitor.log_chat_completion(
                completion_id,
                request.model,
                request.model_dump(),
                response.model_dump()
            )
            return response

        logger.debug("tool calls found")
        for tool_call in response.choices[0].message.tool_calls.root:
            logger.debug(
                f"tool call: {tool_call.function.name} arguments: {json.loads(tool_call.function.arguments)}"
            )

            # FIXME: this can probably be done in parallel using asyncio gather
            tool_call_result = await call_tool(
                tool_call.function.name, tool_call.function.arguments
            )
            if tool_call_result is None:
                continue

            logger.debug(
                f"tool call result for {tool_call.function.name}: {tool_call_result.model_dump()}"
            )
            logger.debug(f"tool call result content: {tool_call_result.content}")

            # Add monitoring for tool call
            await monitor.log_tool_call(
                completion_id,
                tool_call,
                tool_call_result.model_dump()
            )

            tools_content = [
                {"type": "text", "text": part.text}
                for part in filter(lambda x: x.type == "text", tool_call_result.content)
            ]
            if len(tools_content) == 0:
                tools_content = [
                    {"type": "text", "text": "the tool call result is empty"}
                ]
            request.messages.append(
                ChatCompletionRequestMessage.model_validate(
                    {
                        "role": "tool",
                        "content": tools_content,
                        "tool_call_id": tool_call.id,
                    }
                )
            )

            logger.debug("sending next iteration of chat completion request")
