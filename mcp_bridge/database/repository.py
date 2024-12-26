from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import ChatCompletion, ToolCall
from typing import Optional, List, Dict, Any

class ChatCompletionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_completion(
        self,
        completion_id: str,
        model: str,
        request: Dict,
        response: Dict,
    ) -> ChatCompletion:
        completion = ChatCompletion(
            id=completion_id,
            model=model,
            request=request,
            final_response=response,
            total_tokens=response.get("usage", {}).get("total_tokens"),
            completion_tokens=response.get("usage", {}).get("completion_tokens"),
            prompt_tokens=response.get("usage", {}).get("prompt_tokens")
        )
        self.session.add(completion)
        await self.session.commit()
        return completion

    async def create_tool_call(
        self,
        tool_call_id: str,
        completion_id: str,
        tool_name: str,
        arguments: str,
        result: Dict
    ) -> ToolCall:
        tool_call = ToolCall(
            id=tool_call_id,
            chat_completion_id=completion_id,
            tool_name=tool_name,
            arguments=arguments,
            result=result
        )
        self.session.add(tool_call)
        await self.session.commit()
        return tool_call

    async def get_recent_completions(self, limit: int = 100) -> List[ChatCompletion]:
        query = select(ChatCompletion).order_by(ChatCompletion.timestamp.desc()).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_completion_with_tools(self, completion_id: str) -> Optional[ChatCompletion]:
        query = select(ChatCompletion).where(ChatCompletion.id == completion_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()