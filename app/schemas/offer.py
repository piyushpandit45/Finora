from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class OfferResponse(BaseModel):
    id: str
    lenderName: str
    logoUrl: Optional[str] = None
    loanAmount: float
    interestRate: float
    tenureMonths: int
    monthlyEmi: float
    processingFee: float
    matchPercentage: int
    badge: str
    category: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class OffersListResponse(BaseModel):
    success: bool
    totalMatches: int
    applicationId: str
    offers: List[OfferResponse]


class OfferDetailResponse(BaseModel):
    id: str
    applicationId: str
    lenderName: str
    logoUrl: Optional[str] = None
    loanAmount: float
    interestRate: float
    tenureMonths: int
    monthlyEmi: float
    processingFee: float
    matchPercentage: int
    badge: str
    category: Optional[str] = None
    redirectUrl: str

    class Config:
        from_attributes = True
        populate_by_name = True
