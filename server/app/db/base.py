# app/db/base.py
import uuid
from pydantic import BaseModel, Field
from datetime import datetime

class Base(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        from_attributes = True
