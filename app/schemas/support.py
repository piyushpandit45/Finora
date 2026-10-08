from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from uuid import UUID


class CreateTicketRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)


class TicketResponse(BaseModel):
    id: str
    subject: str
    message: str
    status: str
    createdAt: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class FAQResponse(BaseModel):
    id: str
    question: str
    answer: str
    category: str

    class Config:
        from_attributes = True


class FAQsListResponse(BaseModel):
    faqs: List[FAQResponse]


class MessageResponse(BaseModel):
    success: bool
    message: str
