from datetime import datetime
from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field
from pydantic.config import ConfigDict
from pymongo import IndexModel, ASCENDING


class KYCDetails(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    application_id: UUID = Field(...)
    pan_encrypted: str = Field(...)
    age: int = Field(..., ge=18, le=65)
    pincode: str = Field(..., min_length=6, max_length=6)
    is_verified: bool = False

    class Settings:
        name = "kyc_details"
        indexes = [
            IndexModel([("application_id", ASCENDING)], unique=True),
            "is_verified",
        ]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
