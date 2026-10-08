from datetime import datetime
from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field
from enum import Enum
from pydantic.config import ConfigDict


class TicketStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class SupportTicket(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    user_id: UUID = Field(...)
    subject: str = Field(...)
    message: str = Field(...)
    status: TicketStatus = Field(default=TicketStatus.OPEN)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "support_tickets"
        indexes = [
            "user_id",
            "status",
            "created_at",
        ]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True
    )
