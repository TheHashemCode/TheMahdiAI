from datetime import datetime, timezone
import uuid
from sqlmodel import SQLModel, Field

def generate_uuid():
    return uuid.uuid4()

def get_utcnow():
    return datetime.now(timezone.utc)

class BaseModel(SQLModel):
    id: uuid.UUID = Field(default_factory=generate_uuid, primary_key=True)
    created_at: datetime = Field(default_factory=get_utcnow)
