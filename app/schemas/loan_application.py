from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from enum import Enum


class LoanType(str, Enum):
    PERSONAL = "PERSONAL"
    HOME = "HOME"
    BUSINESS = "BUSINESS"


class CreateLoanApplicationRequest(BaseModel):
    loanType: str = Field(default="PERSONAL", alias="loan_type")
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = Field(None, min_length=1, max_length=100)
    loanAmount: float = Field(..., gt=0, le=10000000, alias="loan_amount")

    @field_validator("loanType", mode="before")
    @classmethod
    def sanitize_loan_type(cls, v):
        if not v:
            return "PERSONAL"
        v_upper = str(v).upper().strip()
        if "HOME" in v_upper:
            return "HOME"
        elif "BUSINESS" in v_upper:
            return "BUSINESS"
        return "PERSONAL"  # default safe fallback

    model_config = {
        "populate_by_name": True,
        "extra": "ignore"
    }


class KYCRequest(BaseModel):
    pan: str = Field(..., min_length=10, max_length=10)
    age: int = Field(..., ge=18, le=65)
    pincode: str = Field(..., min_length=6, max_length=6)

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, v: str) -> str:
        import re
        if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", v):
            raise ValueError("Invalid PAN format")
        return v.upper()


class IncomeRequest(BaseModel):
    employmentType: str = Field(..., alias="employment_type")
    monthlyIncome: float = Field(..., gt=0, alias="monthly_income")
    incomeMode: str = Field(..., alias="income_mode")

    @field_validator("employmentType", mode="before")
    @classmethod
    def sanitize_employment_type(cls, v):
        if not v:
            return "SALARIED"
        v_upper = str(v).upper().strip()
        if "SELF" in v_upper or "EMPLOYED" in v_upper:
            return "SELF_EMPLOYED"
        elif "FREELANCE" in v_upper or "FREELANCER" in v_upper:
            return "FREELANCER"
        elif "STUDENT" in v_upper:
            return "STUDENT"
        return "SALARIED"  # default safe fallback

    @field_validator("incomeMode", mode="before")
    @classmethod
    def sanitize_income_mode(cls, v):
        if not v:
            return "BANK_ACCOUNT"
        v_upper = str(v).upper().strip()
        if "CHEQUE" in v_upper:
            return "CHEQUE"
        elif "CASH" in v_upper:
            return "CASH"
        return "BANK_ACCOUNT"  # default safe fallback

    model_config = {
        "populate_by_name": True,
        "extra": "ignore"
    }


class CreditScoreRequest(BaseModel):
    method: str = Field(...)
    score: Optional[int] = Field(None, ge=300, le=900)

    @field_validator("method", mode="before")
    @classmethod
    def sanitize_credit_method(cls, v):
        if not v:
            return "BUREAU"
        v_upper = str(v).upper().strip()
        if "MANUAL" in v_upper:
            return "MANUAL"
        return "BUREAU"  # default safe fallback

    model_config = {
        "populate_by_name": True,
        "extra": "ignore"
    }


class CreateLoanApplicationResponse(BaseModel):
    success: bool
    applicationId: str
    status: str
    currentStep: Optional[str] = None
    progress: Optional[int] = None


class MessageResponse(BaseModel):
    success: bool
    message: str


class LoanApplicationResponse(BaseModel):
    id: str
    status: str
    currentStep: str
    completionPercentage: int

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }
