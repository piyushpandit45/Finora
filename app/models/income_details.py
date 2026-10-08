from datetime import datetime
from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field
from enum import Enum
from pydantic.config import ConfigDict
from pymongo import IndexModel, ASCENDING


class EmploymentType(str, Enum):
    SALARIED = "SALARIED"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    FREELANCER = "FREELANCER"
    STUDENT = "STUDENT"


class IncomeMode(str, Enum):
    BANK_ACCOUNT = "BANK_ACCOUNT"
    CHEQUE = "CHEQUE"
    CASH = "CASH"


class IncomeDetails(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    application_id: UUID = Field(...)
    employment_type: EmploymentType = Field(...)
    monthly_income: float = Field(..., gt=0)
    income_mode: IncomeMode = Field(...)

    class Settings:
        name = "income_details"
        indexes = [
            IndexModel([("application_id", ASCENDING)], unique=True),
        ]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True
    )
