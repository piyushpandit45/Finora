from pydantic import BaseModel
from typing import List
from datetime import datetime
from uuid import UUID


class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    isRead: bool
    createdAt: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


class NotificationsListResponse(BaseModel):
    notifications: List[NotificationResponse]


class MessageResponse(BaseModel):
    success: bool
    message: str
