from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class ChatCompletion(Base):
    __tablename__ = "chat_completions"

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=func.current_timestamp())
    model = Column(String)
    request = Column(JSON)
    final_response = Column(JSON)
    total_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    prompt_tokens = Column(Integer)

    # Relationship to tool calls
    tool_calls = relationship("ToolCall", back_populates="chat_completion")

class ToolCall(Base):
    __tablename__ = "tool_calls"

    id = Column(String, primary_key=True)
    chat_completion_id = Column(String, ForeignKey("chat_completions.id"))
    timestamp = Column(DateTime, default=func.current_timestamp())
    tool_name = Column(String)
    arguments = Column(JSON)
    result = Column(JSON)

    # Relationship to chat completion
    chat_completion = relationship("ChatCompletion", back_populates="tool_calls")