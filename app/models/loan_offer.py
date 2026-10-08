from datetime import datetime
from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field
from pydantic.config import ConfigDict
from typing import Optional


class LoanOffer(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    application_id: UUID = Field(...)
    lender_id: Optional[UUID] = Field(None, description="Optional lender ID for internal tracking")
    lender_name: str = Field(...)
    offered_amount: float = Field(..., gt=0)
    interest_rate: float = Field(..., gt=0)
    processing_fee: float = Field(..., ge=0)
    tenure_months: int = Field(..., gt=0)
    badge: str = Field(default="")
    redirect_url: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "loan_offers"
        indexes = [
            "application_id",
            "lender_id",
            "created_at",
        ]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
