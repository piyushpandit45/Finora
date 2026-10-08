import re
from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Static test OTP for development/testing
STATIC_TEST_OTP = "4554"

# Simple in-memory OTP store (zero external dependencies)
MOCK_OTP_STORE: Dict[str, dict] = {}


class OTPService:
    def __init__(self):
        pass

    async def connect(self) -> None:
        logger.info("OTP Service initialized (in-memory mode)")

    async def disconnect(self) -> None:
        logger.info("OTP Service disconnected")

    def _validate_mobile(self, mobile: str) -> bool:
        """Validate Indian mobile number format (10 digits starting with 6-9)"""
        return bool(re.match(r'^[6-9]\d{9}$', mobile))

    async def generate_and_store_otp(self, mobile: str) -> str:
        """Generate and store OTP - responds in <5ms with zero timeout"""
        if not self._validate_mobile(mobile):
            raise ValueError("Invalid mobile number format")

        # Store OTP with timestamp
        MOCK_OTP_STORE[mobile] = {
            "otp": STATIC_TEST_OTP,
            "timestamp": datetime.utcnow()
        }

        print(f"[AUTH LOG] OTP sent to {mobile}: {STATIC_TEST_OTP}")
        logger.info(f"[AUTH LOG] OTP sent to {mobile}: {STATIC_TEST_OTP}")

        return STATIC_TEST_OTP

    async def verify_otp(self, mobile: str, otp: str) -> bool:
        """Verify OTP - accepts only static test OTP"""
        if otp == STATIC_TEST_OTP:
            # Clean up after successful verification
            if mobile in MOCK_OTP_STORE:
                del MOCK_OTP_STORE[mobile]
            return True

        return False


otp_service = OTPService()
