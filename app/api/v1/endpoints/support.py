from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID
from app.schemas.notification import NotificationResponse, NotificationsListResponse, MessageResponse
from app.schemas.support import CreateTicketRequest, TicketResponse, FAQResponse, FAQsListResponse
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.notification import Notification
from app.models.support_ticket import SupportTicket, TicketStatus
from app.models.faq import FAQ

router = APIRouter(prefix="/notifications", tags=["Notifications"], include_in_schema=True)


@router.get("", response_model=NotificationsListResponse)
async def get_notifications(current_user: User = Depends(get_current_user)):
    try:
        notifications = await Notification.find(
            Notification.user_id == current_user.id
        ).sort(-Notification.created_at).to_list()
        
        notification_responses = [
            NotificationResponse(
                id=str(notification.id),
                title=notification.title,
                message=notification.message,
                isRead=notification.is_read,
                createdAt=notification.created_at
            )
            for notification in notifications
        ]
        
        return NotificationsListResponse(notifications=notification_responses)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications"
        )


@router.post("/{notificationId}/read", response_model=MessageResponse)
async def mark_notification_read(
    notificationId: UUID,
    current_user: User = Depends(get_current_user)
):
    try:
        notification = await Notification.get(notificationId)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        if notification.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this notification"
            )
        
        notification.is_read = True
        await notification.save()
        
        return MessageResponse(success=True, message="Notification marked as read")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read"
        )


support_router = APIRouter(prefix="/support", tags=["Support"])


@support_router.get("/faqs", response_model=FAQsListResponse)
async def get_faqs():
    try:
        faqs = await FAQ.find_all().to_list()
        
        faq_responses = [
            FAQResponse(
                id=str(faq.id),
                question=faq.question,
                answer=faq.answer,
                category=faq.category
            )
            for faq in faqs
        ]
        
        return FAQsListResponse(faqs=faq_responses)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch FAQs"
        )


@support_router.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    request: CreateTicketRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        ticket = SupportTicket(
            user_id=current_user.id,
            subject=request.subject,
            message=request.message,
            status=TicketStatus.OPEN
        )
        await ticket.insert()
        
        return TicketResponse(
            id=str(ticket.id),
            subject=ticket.subject,
            message=ticket.message,
            status=ticket.status.value,
            createdAt=ticket.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create support ticket"
        )
