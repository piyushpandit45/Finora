from datetime import datetime
from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field
from pydantic.config import ConfigDict


class Lender(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    name: str = Field(...)
    min_score: int = Field(..., ge=300, le=900)
    min_income: float = Field(..., gt=0)
    min_age: int = Field(..., ge=18, le=65)
    base_roi: float = Field(..., gt=0)
    processing_fee: float = Field(..., ge=0)
    is_active: bool = True

    class Settings:
        name = "lenders"
        indexes = [
            "min_score",
            "min_income",
            "min_age",
            "is_active",
        ]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
