import re
from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import SendOTPRequest, VerifyOTPRequest, OTPResponse, AuthResponse
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


def validate_mobile(mobile: str) -> bool:
    """Validate Indian mobile number format (10 digits starting with 6-9)"""
    return bool(re.match(r'^[6-9]\d{9}$', mobile))


@router.post("/send-otp", response_model=OTPResponse)
async def send_otp(request: SendOTPRequest):
    try:
        if not validate_mobile(request.mobile):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid mobile number format"
            )

        result = await auth_service.send_otp(request.mobile)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP"
        )


@router.post("/verify-otp", response_model=AuthResponse)
async def verify_otp(request: VerifyOTPRequest):
    try:
        result = await auth_service.verify_otp(request.mobile, request.otp)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify OTP"
        )


@router.post("/resend-otp", response_model=OTPResponse)
async def resend_otp(request: SendOTPRequest):
    try:
        if not validate_mobile(request.mobile):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid mobile number format"
            )

        result = await auth_service.send_otp(request.mobile)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend OTP"
        )
