from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import Field, JSON, Column
import uuid
from app.models.base import BaseModel

class ChatSession(BaseModel, table=True):
    __tablename__ = "chat_sessions"
    
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    session_key: Optional[str] = None
    
    # We use SQLAlchemy Column for JSON dict type to store recent context
    context_window: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    
    total_tokens: int = Field(default=0)
    is_active: bool = Field(default=True, index=True)
    
    closed_at: Optional[datetime] = None
