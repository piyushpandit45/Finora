from datetime import datetime
from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field
from typing import Optional
from enum import Enum
from pydantic.config import ConfigDict
from pymongo import IndexModel, ASCENDING


class CreditScoreMethod(str, Enum):
    BUREAU = "BUREAU"
    MANUAL = "MANUAL"


class CreditScore(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    application_id: UUID = Field(...)
    method: CreditScoreMethod = Field(...)
    score: int = Field(..., ge=300, le=900)
    bureau_reference: Optional[str] = None
    fetched_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "credit_scores"
        indexes = [
            IndexModel([("application_id", ASCENDING)], unique=True),
            "score",
            "fetched_at",
        ]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True
    )
