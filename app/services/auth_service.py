from typing import Optional
from uuid import UUID
import logging

from app.models.user import User
from app.models.user_profile import UserProfile
from app.core.security import create_access_token
from app.services.otp_service import otp_service

logger = logging.getLogger(__name__)


class AuthService:
    async def send_otp(self, mobile: str) -> dict:
        otp = await otp_service.generate_and_store_otp(mobile)
        logger.info(f"OTP sent to {mobile}: {otp}")
        return {
            "success": True,
            "message": "OTP sent successfully",
            "expiresIn": 120
        }

    async def verify_otp(self, mobile: str, otp: str) -> dict:
        is_valid = await otp_service.verify_otp(mobile, otp)

        if not is_valid:
            raise ValueError("Invalid OTP. Use 4554")

        user = await User.find_one(User.mobile == mobile)

        if not user:
            user = User(mobile=mobile)
            await user.insert()
            logger.info(f"New user created: {mobile}")

            user_profile = UserProfile(user_id=user.id)
            await user_profile.insert()
            logger.info(f"User profile created for: {mobile}")
        else:
            if not user.is_active:
                raise ValueError("User account is inactive")

        user_profile = await UserProfile.find_one(UserProfile.user_id == user.id)

        token_data = {"sub": str(user.id), "mobile": mobile}
        access_token = create_access_token(token_data)

        return {
            "success": True,
            "token": access_token,
            "user": {
                "id": str(user.id),
                "mobile": user.mobile,
                "name": user_profile.name if user_profile else None
            }
        }

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        return await User.get(user_id)

    async def get_user_profile(self, user_id: UUID) -> Optional[UserProfile]:
        return await UserProfile.find_one(UserProfile.user_id == user_id)


auth_service = AuthService()
