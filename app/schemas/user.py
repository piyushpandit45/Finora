from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class UpdateUserProfileRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class UserProfileResponse(BaseModel):
    id: str
    mobile: str
    name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True
