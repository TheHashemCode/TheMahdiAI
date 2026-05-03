from datetime import datetime
from typing import Optional
from sqlmodel import Field
from sqlalchemy import BigInteger, Column
from app.models.base import BaseModel, get_utcnow

class User(BaseModel, table=True):
    __tablename__ = "users"
    
    telegram_id: int = Field(sa_column=Column(BigInteger, unique=True, index=True, nullable=False))
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    language: str = Field(default="id")
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    
    daily_token_limit: int = Field(default=100000)
    daily_token_used: int = Field(default=0)
    token_reset_date: Optional[datetime] = None
    
    updated_at: datetime = Field(default_factory=get_utcnow)
