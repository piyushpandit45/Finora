from fastapi import APIRouter, HTTPException, status, Depends
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.loan_application import LoanApplication
from app.models.loan_offer import LoanOffer
from app.models.notification import Notification
from app.models.user_profile import UserProfile

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
async def get_dashboard(current_user: User = Depends(get_current_user)):
    try:
        # Safe user profile lookup
        user_profile = await UserProfile.find_one(UserProfile.user_id == current_user.id)
        user_name = "User"
        if user_profile and user_profile.name:
            user_name = user_profile.name

        # Safe loan application lookup
        active_application = None
        active_application_summary = None
        try:
            from beanie.operators import In
            active_application = await LoanApplication.find_one(
                LoanApplication.user_id == current_user.id,
                In(LoanApplication.status, ["DRAFT", "PROCESSING", "MATCHED"])
            )
            if active_application:
                active_application_summary = {
                    "id": str(active_application.id),
                    "status": str(active_application.status),
                    "currentStep": str(active_application.current_step),
                    "progress": active_application.completion_percentage
                }
        except Exception as app_error:
            import traceback
            print(f"Error fetching active application: {str(app_error)}")
            print(traceback.format_exc())
            active_application_summary = None

        # Static categories - always return these
        loan_categories = [
            {"id": "personal", "title": "Personal Loan", "icon": "person"},
            {"id": "home", "title": "Home Loan", "icon": "home"},
            {"id": "business", "title": "Business Loan", "icon": "briefcase"}
        ]

        # Safe offer count lookup - default to 0 for new users
        offer_count = 0

        # Safe notification count lookup - default to 0 for new users
        unread_notification_count = 0

        return {
            "greeting": f"Hi, {user_name}",
            "name": user_name,
            "application": active_application_summary,
            "categories": loan_categories,
            "offersCount": offer_count,
            "unreadNotifications": unread_notification_count
        }
    except Exception as e:
        import traceback
        print(f"Dashboard error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard data"
        )
