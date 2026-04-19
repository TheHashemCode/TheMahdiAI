from datetime import datetime
import uuid
from sqlmodel import SQLModel, Field

def generate_uuid():
    return uuid.uuid4()

class BaseModel(SQLModel):
    id: uuid.UUID = Field(default_factory=generate_uuid, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
