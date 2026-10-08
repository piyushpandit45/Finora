from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field, EmailStr
from pydantic.config import ConfigDict
from pymongo import IndexModel, ASCENDING


class UserProfile(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    user_id: UUID = Field(...)
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "user_profiles"
        indexes = [
            IndexModel([("user_id", ASCENDING)], unique=True),
            IndexModel([("email", ASCENDING)], sparse=True),
            "updated_at",
        ]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
