from lmos_openai_types import (
    CreateChatCompletionRequest,
    CreateChatCompletionResponse,
    ChatCompletionRequestMessage,
    FinishReason1,
)
from .utils import call_tool, chat_completion_add_tools
from .genericHttpxClient import client
from mcp_clients.McpClientManager import ClientManager
from tool_mappers import mcp2openai
from loguru import logger
from database.session import get_db
from database.repository import ChatCompletionRepository
import json
import uuid

async def log_completion_to_db(
    repo: ChatCompletionRepository,
    completion_id: str,
    request: CreateChatCompletionRequest,
    response: CreateChatCompletionResponse,
    tool_call=None,
    tool_result=None
) -> None:
    """Helper function to handle all DB logging operations"""
    try:
        if tool_call and tool_result:
            # Log tool call
            await repo.create_tool_call(
                tool_call.id,
                completion_id,
                tool_call.function.name,
                tool_call.function.arguments,
                tool_result.model_dump()
            )
        else:
            # Log completion
            await repo.create_completion(
                completion_id,
                response.model,
                request.model_dump(),
                response.choices[0].message.model_dump(),
                response.usage.total_tokens,
                response.usage.completion_tokens,
                response.usage.prompt_tokens
            )
    except Exception as e:
        logger.error(f"Failed to store to database: {e}")
        # Continue with the conversation even if storage fails
        pass

async def chat_completions(
    request: CreateChatCompletionRequest,
) -> CreateChatCompletionResponse:
    """performs a chat completion using the inference server"""
    
    completion_id = str(uuid.uuid4())
    request = await chat_completion_add_tools(request)
    stored_completion = False
    final_response = None

    async for db in get_db():
        repo = ChatCompletionRepository(db)
        
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
            response = CreateChatCompletionResponse.model_validate_json(text)

            # Log the initial completion only once
            if not stored_completion:
                await log_completion_to_db(repo, completion_id, request, response)
                stored_completion = True

            msg = response.choices[0].message
            msg = ChatCompletionRequestMessage(
                role="assistant",
                content=msg.content,
                tool_calls=msg.tool_calls,
            )
            request.messages.append(msg)

            if response.choices[0].finish_reason.value in ["stop", "length"]:
                logger.debug("no tool calls found")
                final_response = response.choices[0].message
                # Update the completion with the final response
                await repo.update_completion_response(completion_id, final_response.model_dump())
                return response

            logger.debug("tool calls found")
            for tool_call in response.choices[0].message.tool_calls.root:
                logger.debug(
                    f"tool call: {tool_call.function.name} arguments: {json.loads(tool_call.function.arguments)}"
                )

                tool_call_result = await call_tool(
                    tool_call.function.name, tool_call.function.arguments
                )
                if tool_call_result is None:
                    logger.debug(f"tool call failed for {tool_call.function.name}")
                    continue

                logger.debug(
                    f"tool call result for {tool_call.function.name}: {tool_call_result.model_dump()}"
                )
                logger.debug(f"tool call result content: {tool_call_result.content}")

                # Log tool call to DB
                await log_completion_to_db(repo, completion_id, request, response, tool_call, tool_call_result)

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
