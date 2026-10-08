from datetime import datetime
from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field
from pydantic.config import ConfigDict


class Notification(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    user_id: UUID = Field(...)
    title: str = Field(...)
    message: str = Field(...)
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notifications"
        indexes = [
            "user_id",
            "is_read",
            "created_at",
        ]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
