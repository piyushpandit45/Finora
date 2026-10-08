from pydantic import BaseModel
from typing import Optional, List


class ActiveApplicationSummary(BaseModel):
    id: str
    status: str
    currentStep: str
    progress: int

    class Config:
        from_attributes = True
        populate_by_name = True


class LoanCategory(BaseModel):
    id: str
    title: str
    icon: str


class DashboardResponse(BaseModel):
    greeting: str
    name: str
    application: Optional[ActiveApplicationSummary] = None
    categories: List[LoanCategory]
    offersCount: int
    unreadNotifications: int
