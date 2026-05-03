from typing import Optional
from sqlmodel import Field
import uuid
from app.models.base import BaseModel

class BotConfig(BaseModel, table=True):
    __tablename__ = "bot_config"
    
    key: str = Field(unique=True, index=True)
    value: str
    description: Optional[str] = None
    updated_by: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
