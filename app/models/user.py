from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field
from pydantic.config import ConfigDict
from pymongo import IndexModel, ASCENDING


class User(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    mobile: str = Field(..., min_length=10, max_length=10)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [
            IndexModel([("mobile", ASCENDING)], unique=True),
            "is_active",
            "created_at",
        ]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
