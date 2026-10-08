from datetime import datetime
from uuid import UUID, uuid4
from beanie import Document
from pydantic import Field
from pydantic.config import ConfigDict
from typing import List, Optional
from enum import Enum


class LoanCategory(str, Enum):
    PERSONAL = "PERSONAL"
    HOME = "HOME"
    BUSINESS = "BUSINESS"


class EmploymentType(str, Enum):
    SALARIED = "SALARIED"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    FREELANCER = "FREELANCER"
    STUDENT = "STUDENT"


class LenderProduct(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    lender_name: str = Field(..., description="Name of the lending institution")
    logo_url: str = Field(..., description="URL to lender logo")
    category: LoanCategory = Field(default=LoanCategory.PERSONAL)

    # Loan Amount & Tenure
    min_amount: float = Field(..., gt=0, description="Minimum loan amount")
    max_amount: float = Field(..., gt=0, description="Maximum loan amount")
    min_tenure_months: int = Field(default=12, gt=0, description="Minimum tenure in months")
    max_tenure_months: int = Field(default=60, gt=0, description="Maximum tenure in months")

    # Interest Rates
    interest_rate_min: float = Field(..., gt=0, description="Minimum interest rate (% per annum)")
    interest_rate_max: float = Field(..., gt=0, description="Maximum interest rate (% per annum)")

    # Fees
    processing_fee_pct: float = Field(default=1.5, ge=0, description="Processing fee as percentage of loan amount")

    # Eligibility
    min_cibil: int = Field(..., ge=300, le=900, description="Minimum CIBIL score required")
    min_monthly_income: float = Field(..., gt=0, description="Minimum monthly income in INR")
    allowed_employment: List[str] = Field(
        default_factory=lambda: ["SALARIED", "SELF_EMPLOYED"],
        description="Allowed employment types"
    )
    min_age: int = Field(default=21, ge=18, le=65, description="Minimum age")
    max_age: Optional[int] = Field(default=60, ge=18, le=65, description="Maximum age")

    # Metadata
    is_active: bool = Field(default=True, description="Whether this product is currently available")
    priority: int = Field(default=0, description="Priority for ranking (higher = more preferred)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "lender_products"
        indexes = [
            "lender_name",
            "category",
            "is_active",
            "priority",
            "min_cibil",
            "min_monthly_income",
        ]

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        use_enum_values=True
    )
