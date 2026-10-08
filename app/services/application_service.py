from typing import Optional
from uuid import UUID
from datetime import datetime
import logging

from app.models.loan_application import LoanApplication, ApplicationStatus, ApplicationStep, LoanType
from app.models.user_profile import UserProfile
from app.models.kyc_details import KYCDetails
from app.models.income_details import IncomeDetails, EmploymentType, IncomeMode
from app.models.credit_score import CreditScore, CreditScoreMethod
from app.core.security import encrypt_pan

logger = logging.getLogger(__name__)


class ApplicationService:
    async def create_application(
        self,
        user_id: UUID,
        loan_type: str,
        name: str,
        email: Optional[str],
        loan_amount: float
    ) -> dict:
        print(f"[DB DEBUG] Creating application for user: {user_id}")
        print(f"[DB DEBUG] Loan type: {loan_type}, amount: {loan_amount}")

        # Sanitize and convert string to LoanType enum with fallback
        loan_type_upper = str(loan_type).upper().strip()
        if "HOME" in loan_type_upper:
            loan_type_clean = "HOME"
        elif "BUSINESS" in loan_type_upper:
            loan_type_clean = "BUSINESS"
        else:
            loan_type_clean = "PERSONAL"  # default safe fallback

        try:
            loan_type_enum = LoanType(loan_type_clean)
        except ValueError:
            # Should never happen due to sanitization, but safety fallback
            loan_type_enum = LoanType.PERSONAL

        application = LoanApplication(
            user_id=user_id,
            loan_type=loan_type_enum,
            loan_amount=loan_amount,
            status=ApplicationStatus.DRAFT,
            current_step=ApplicationStep.PERSONAL_DETAILS,
            completion_percentage=25
        )
        await application.insert()
        print(f"[MONGODB WRITE SUCCESS] Saved application {application.id} for user {user_id} to MongoDB Atlas")

        user_profile = await UserProfile.find_one(UserProfile.user_id == user_id)
        if user_profile:
            if not user_profile.name and name:
                user_profile.name = name
            if not user_profile.email and email:
                user_profile.email = email
            user_profile.updated_at = datetime.utcnow()
            await user_profile.save()
            print(f"[DB SUCCESS] User profile updated: {user_id}")
        else:
            # Create profile if it doesn't exist
            new_profile = UserProfile(
                user_id=user_id,
                name=name,
                email=email
            )
            await new_profile.insert()
            print(f"[DB SUCCESS] User profile created: {user_id}")

        return {
            "success": True,
            "applicationId": str(application.id),
            "status": application.status.value
        }

    async def save_kyc(
        self,
        application_id: UUID,
        user_id: UUID,
        pan: str,
        age: int,
        pincode: str
    ) -> dict:
        print(f"[DB DEBUG] Saving KYC for application: {application_id}")
        application = await LoanApplication.get(application_id)
        if not application:
            print(f"[DB ERROR] Application not found: {application_id}")
            raise ValueError("Application not found")

        if application.user_id != user_id:
            print(f"[DB ERROR] Unauthorized access: {user_id} != {application.user_id}")
            raise ValueError("Unauthorized access to application")

        existing_kyc = await KYCDetails.find_one(KYCDetails.application_id == application_id)
        pan_encrypted = encrypt_pan(pan)

        if existing_kyc:
            existing_kyc.pan_encrypted = pan_encrypted
            existing_kyc.age = age
            existing_kyc.pincode = pincode
            await existing_kyc.save()
            print(f"[DB SUCCESS] KYC details updated for application: {application_id}")
        else:
            kyc = KYCDetails(
                application_id=application_id,
                pan_encrypted=pan_encrypted,
                age=age,
                pincode=pincode
            )
            await kyc.insert()
            print(f"[DB SUCCESS] KYC details created for application: {application_id}")

        application.current_step = ApplicationStep.KYC
        application.completion_percentage = 50
        application.updated_at = datetime.utcnow()
        await application.save()

        return {
            "success": True,
            "message": "KYC details saved"
        }

    async def save_income(
        self,
        application_id: UUID,
        user_id: UUID,
        employment_type: str,
        monthly_income: float,
        income_mode: str
    ) -> dict:
        print(f"[DB DEBUG] Saving income for application: {application_id}")
        application = await LoanApplication.get(application_id)
        if not application:
            print(f"[DB ERROR] Application not found: {application_id}")
            raise ValueError("Application not found")

        if application.user_id != user_id:
            print(f"[DB ERROR] Unauthorized access: {user_id} != {application.user_id}")
            raise ValueError("Unauthorized access to application")

        # Safe enum conversion with fallback
        try:
            employment_type_enum = EmploymentType(employment_type)
        except ValueError:
            employment_type_enum = EmploymentType.SALARIED
            print(f"[DB WARNING] Invalid employment_type '{employment_type}', defaulting to SALARIED")

        try:
            income_mode_enum = IncomeMode(income_mode)
        except ValueError:
            income_mode_enum = IncomeMode.BANK_ACCOUNT
            print(f"[DB WARNING] Invalid income_mode '{income_mode}', defaulting to BANK_ACCOUNT")

        existing_income = await IncomeDetails.find_one(IncomeDetails.application_id == application_id)

        if existing_income:
            existing_income.employment_type = employment_type_enum
            existing_income.monthly_income = monthly_income
            existing_income.income_mode = income_mode_enum
            await existing_income.save()
            print(f"[DB SUCCESS] Income details updated for application: {application_id}")
        else:
            income = IncomeDetails(
                application_id=application_id,
                employment_type=employment_type_enum,
                monthly_income=monthly_income,
                income_mode=income_mode_enum
            )
            await income.insert()
            print(f"[DB SUCCESS] Income details created for application: {application_id}")

        application.current_step = ApplicationStep.INCOME
        application.completion_percentage = 75
        application.updated_at = datetime.utcnow()
        await application.save()

        return {
            "success": True,
            "message": "Income details saved"
        }

    async def save_credit_score(
        self,
        application_id: UUID,
        user_id: UUID,
        method: str,
        score: Optional[int] = None
    ) -> dict:
        print(f"[DB DEBUG] Saving credit score for application: {application_id}")
        application = await LoanApplication.get(application_id)
        if not application:
            print(f"[DB ERROR] Application not found: {application_id}")
            raise ValueError("Application not found")

        if application.user_id != user_id:
            print(f"[DB ERROR] Unauthorized access: {user_id} != {application.user_id}")
            raise ValueError("Unauthorized access to application")

        # Safe enum conversion with fallback
        try:
            credit_score_method = CreditScoreMethod(method)
        except ValueError:
            credit_score_method = CreditScoreMethod.BUREAU
            print(f"[DB WARNING] Invalid credit method '{method}', defaulting to BUREAU")

        if credit_score_method == CreditScoreMethod.MANUAL and score is None:
            raise ValueError("Score is required for manual method")

        if credit_score_method == CreditScoreMethod.BUREAU:
            score = 750
            bureau_reference = "BUREAU_DEFAULT"
        else:
            bureau_reference = None

        existing_score = await CreditScore.find_one(CreditScore.application_id == application_id)

        if existing_score:
            existing_score.method = credit_score_method
            existing_score.score = score
            existing_score.bureau_reference = bureau_reference
            existing_score.fetched_at = datetime.utcnow()
            await existing_score.save()
            print(f"[DB SUCCESS] Credit score updated for application: {application_id}")
        else:
            credit_score = CreditScore(
                application_id=application_id,
                method=credit_score_method,
                score=score,
                bureau_reference=bureau_reference
            )
            await credit_score.insert()
            print(f"[DB SUCCESS] Credit score created for application: {application_id}")

        application.current_step = ApplicationStep.CREDIT_SCORE
        application.completion_percentage = 100
        application.updated_at = datetime.utcnow()
        await application.save()

        return {
            "success": True,
            "message": "Credit score recorded"
        }

    async def get_application(self, application_id: UUID, user_id: UUID) -> dict:
        application = await LoanApplication.get(application_id)
        if not application:
            raise ValueError("Application not found")

        if application.user_id != user_id:
            raise ValueError("Unauthorized access to application")

        # Handle both enum and string values due to use_enum_values=True
        status_value = application.status if isinstance(application.status, str) else application.status.value
        step_value = application.current_step if isinstance(application.current_step, str) else application.current_step.value

        return {
            "id": str(application.id),
            "status": status_value,
            "currentStep": step_value,
            "completionPercentage": application.completion_percentage
        }

    async def submit_application(self, application_id: UUID, user_id: UUID) -> dict:
        application = await LoanApplication.get(application_id)
        if not application:
            raise ValueError("Application not found")

        if application.user_id != user_id:
            raise ValueError("Unauthorized access to application")

        kyc = await KYCDetails.find_one(KYCDetails.application_id == application_id)
        income = await IncomeDetails.find_one(IncomeDetails.application_id == application_id)
        credit_score = await CreditScore.find_one(CreditScore.application_id == application_id)

        if not kyc or not income or not credit_score:
            raise ValueError("All sections (KYC, Income, Credit Score) must be completed before submission")

        application.status = ApplicationStatus.PROCESSING
        application.current_step = ApplicationStep.MATCHING
        application.updated_at = datetime.utcnow()
        await application.save()

        logger.info(f"Application submitted: {application_id}")

        # Handle both enum and string values due to use_enum_values=True
        status_value = application.status if isinstance(application.status, str) else application.status.value
        step_value = application.current_step if isinstance(application.current_step, str) else application.current_step.value

        return {
            "success": True,
            "applicationId": str(application.id),
            "status": status_value,
            "currentStep": step_value,
            "progress": application.completion_percentage
        }


application_service = ApplicationService()
