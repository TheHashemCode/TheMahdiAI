from typing import Optional
from sqlmodel import Field
import uuid
from app.models.base import BaseModel
from decimal import Decimal

class TokenLog(BaseModel, table=True):
    __tablename__ = "token_logs"
    
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    session_id: Optional[uuid.UUID] = Field(default=None, foreign_key="chat_sessions.id")
    
    provider: str = Field(index=True) # openai | anthropic | groq
    model_name: str # e.g. gpt-4o
    
    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)
    
    cost_usd: Decimal = Field(default=0, max_digits=10, decimal_places=6)
    latency_ms: int = Field(default=0)
    
    is_failover: bool = Field(default=False)
    failover_reason: Optional[str] = None
