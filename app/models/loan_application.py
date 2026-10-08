from datetime import datetime
from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field
from enum import Enum
from pydantic.config import ConfigDict


class LoanType(str, Enum):
    PERSONAL = "PERSONAL"
    HOME = "HOME"
    BUSINESS = "BUSINESS"


class ApplicationStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    MATCHED = "MATCHED"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class ApplicationStep(str, Enum):
    PERSONAL_DETAILS = "PERSONAL_DETAILS"
    KYC = "KYC"
    INCOME = "INCOME"
    CREDIT_SCORE = "CREDIT_SCORE"
    MATCHING = "MATCHING"
    OFFERS = "OFFERS"


class LoanApplication(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    user_id: UUID = Field(...)
    loan_type: LoanType = Field(...)
    loan_amount: float = Field(..., gt=0)
    status: ApplicationStatus = Field(default=ApplicationStatus.DRAFT)
    current_step: ApplicationStep = Field(default=ApplicationStep.PERSONAL_DETAILS)
    completion_percentage: int = Field(default=25, ge=0, le=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "loan_applications"
        indexes = [
            "user_id",
            "status",
            "current_step",
            "created_at",
            "updated_at",
        ]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True
    )
