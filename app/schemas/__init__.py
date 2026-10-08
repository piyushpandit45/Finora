from app.schemas.auth import (
    SendOTPRequest,
    VerifyOTPRequest,
    OTPResponse,
    UserResponse,
    AuthResponse,
)
from app.schemas.user import UpdateUserProfileRequest, UserProfileResponse
from app.schemas.loan_application import (
    LoanType,
    CreateLoanApplicationRequest,
    KYCRequest,
    IncomeRequest,
    CreditScoreRequest,
    CreateLoanApplicationResponse,
    MessageResponse,
    LoanApplicationResponse,
)
from app.schemas.offer import OfferResponse, OffersListResponse, OfferDetailResponse
from app.schemas.dashboard import DashboardResponse, ActiveApplicationSummary, LoanCategory
from app.schemas.notification import NotificationResponse, NotificationsListResponse
from app.schemas.support import (
    CreateTicketRequest,
    TicketResponse,
    FAQResponse,
    FAQsListResponse,
)

__all__ = [
    "SendOTPRequest",
    "VerifyOTPRequest",
    "OTPResponse",
    "UserResponse",
    "AuthResponse",
    "UpdateUserProfileRequest",
    "UserProfileResponse",
    "LoanType",
    "CreateLoanApplicationRequest",
    "KYCRequest",
    "IncomeRequest",
    "CreditScoreRequest",
    "CreateLoanApplicationResponse",
    "MessageResponse",
    "LoanApplicationResponse",
    "OfferResponse",
    "OffersListResponse",
    "OfferDetailResponse",
    "DashboardResponse",
    "ActiveApplicationSummary",
    "LoanCategory",
    "NotificationResponse",
    "NotificationsListResponse",
    "CreateTicketRequest",
    "TicketResponse",
    "FAQResponse",
    "FAQsListResponse",
]
