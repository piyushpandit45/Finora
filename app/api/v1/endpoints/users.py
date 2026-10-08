from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID
from app.schemas.user import UpdateUserProfileRequest, UserProfileResponse
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.user_profile import UserProfile
from app.services.auth_service import auth_service
from datetime import datetime

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    try:
        user_profile = await auth_service.get_user_profile(current_user.id)
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return UserProfileResponse(
            id=str(current_user.id),
            mobile=current_user.mobile,
            name=user_profile.name,
            email=user_profile.email
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )


@router.put("/me", response_model=UserProfileResponse)
async def update_user_profile(
    request: UpdateUserProfileRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        user_profile = await UserProfile.find_one(UserProfile.user_id == current_user.id)
        if not user_profile:
            user_profile = UserProfile(user_id=current_user.id)
            await user_profile.insert()
        
        if request.name is not None:
            user_profile.name = request.name
        if request.email is not None:
            user_profile.email = request.email
        
        user_profile.updated_at = datetime.utcnow()
        await user_profile.save()
        
        return UserProfileResponse(
            id=str(current_user.id),
            mobile=current_user.mobile,
            name=user_profile.name,
            email=user_profile.email
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
