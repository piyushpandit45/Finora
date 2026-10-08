from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID


class SendOTPRequest(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=10)

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        import re
        if not re.match(r"^[6-9]\d{9}$", v):
            raise ValueError("Invalid Indian mobile number")
        return v


class VerifyOTPRequest(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=10)
    otp: str = Field(..., min_length=4, max_length=6)

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        import re
        if not re.match(r"^[6-9]\d{9}$", v):
            raise ValueError("Invalid Indian mobile number")
        return v


class OTPResponse(BaseModel):
    success: bool
    message: str
    expiresIn: int


class UserResponse(BaseModel):
    id: str
    mobile: str
    name: Optional[str] = None

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    success: bool
    token: str
    user: UserResponse
