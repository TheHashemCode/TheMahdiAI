from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from app.models.base import BaseModel

class Notebook(BaseModel, table=True):
    __tablename__ = "notebooks"
    
    external_id: str = Field(unique=True, index=True) # ID from Google NotebookLM
    title: str
    is_active: bool = Field(default=True)
    
    queries: List["NotebookQuery"] = Relationship(back_populates="notebook")

class NotebookQuery(BaseModel, table=True):
    __tablename__ = "notebook_queries"
    
    notebook_id: UUID = Field(foreign_key="notebooks.id")
    user_id: Optional[UUID] = Field(default=None, foreign_key="users.id")
    question: str
    answer: str
    source: str = Field(default="dashboard") # "dashboard" or "telegram"
    
    notebook: Notebook = Relationship(back_populates="queries")
