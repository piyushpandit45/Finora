from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID
import uuid
import traceback
from app.schemas.loan_application import (
    CreateLoanApplicationRequest,
    KYCRequest,
    IncomeRequest,
    CreditScoreRequest,
    CreateLoanApplicationResponse,
    MessageResponse,
    LoanApplicationResponse
)
from app.api.dependencies import get_current_user, verify_application_ownership
from app.models.user import User
from app.models.loan_application import LoanApplication, LoanType, ApplicationStatus, ApplicationStep
from app.models.user_profile import UserProfile
from app.services.application_service import application_service

router = APIRouter(prefix="/loan-applications", tags=["Loan Applications"])


@router.post("", response_model=CreateLoanApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    request: CreateLoanApplicationRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        print(f"[ENDPOINT DEBUG] Creating application with loanType: {request.loanType}")
        print(f"[ENDPOINT DEBUG] User ID: {current_user.id}, Type: {type(current_user.id)}")

        # Safe user ID conversion
        user_uuid = current_user.id if isinstance(current_user.id, uuid.UUID) else uuid.UUID(str(current_user.id))
        print(f"[ENDPOINT DEBUG] Converted user UUID: {user_uuid}")

        # Sanitize loan type
        loan_type_str = str(request.loanType).upper().strip()
        if "HOME" in loan_type_str:
            loan_type_enum = LoanType.HOME
        elif "BUSINESS" in loan_type_str:
            loan_type_enum = LoanType.BUSINESS
        else:
            loan_type_enum = LoanType.PERSONAL

        print(f"[ENDPOINT DEBUG] Sanitized loan type: {loan_type_enum.value}")

        # Create application document
        new_app = LoanApplication(
            user_id=user_uuid,
            loan_type=loan_type_enum,
            loan_amount=float(request.loanAmount),
            status=ApplicationStatus.DRAFT,
            current_step=ApplicationStep.PERSONAL_DETAILS,
            completion_percentage=25
        )
        await new_app.insert()
        print(f"[MONGODB WRITE SUCCESS] Saved application {new_app.id} for user {user_uuid} to MongoDB Atlas")

        # Update or create user profile
        profile = await UserProfile.find_one(UserProfile.user_id == user_uuid)
        if profile:
            print(f"[ENDPOINT DEBUG] Found existing profile for user {user_uuid}")
            if not profile.name and request.name:
                profile.name = request.name
            if not profile.email and request.email:
                profile.email = request.email
            await profile.save()
            print(f"[ENDPOINT DEBUG] Updated existing profile")
        else:
            print(f"[ENDPOINT DEBUG] Creating new profile for user {user_uuid}")
            new_profile = UserProfile(
                user_id=user_uuid,
                name=request.name,
                email=request.email
            )
            await new_profile.insert()
            print(f"[ENDPOINT DEBUG] Created new profile")

        # Return response in format expected by frontend
        # Beanie with use_enum_values=True returns strings, not enums
        status_value = new_app.status if isinstance(new_app.status, str) else new_app.status.value
        step_value = new_app.current_step if isinstance(new_app.current_step, str) else new_app.current_step.value

        return {
            "success": True,
            "applicationId": str(new_app.id),
            "status": status_value,
            "currentStep": step_value,
            "progress": new_app.completion_percentage
        }

    except Exception as e:
        print(f"[ENDPOINT ERROR] Failed to create application: {str(e)}")
        print(f"[ENDPOINT ERROR] Exception type: {type(e).__name__}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create loan application: {str(e)}"
        )


@router.put("/{applicationId}/kyc", response_model=MessageResponse)
async def save_kyc(
    applicationId: UUID,
    request: KYCRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        await verify_application_ownership(applicationId, current_user)
        result = await application_service.save_kyc(
            application_id=applicationId,
            user_id=current_user.id,
            pan=request.pan,
            age=request.age,
            pincode=request.pincode
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save KYC details"
        )


@router.put("/{applicationId}/income", response_model=MessageResponse)
async def save_income(
    applicationId: UUID,
    request: IncomeRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        print(f"[ENDPOINT DEBUG] Saving income for application: {applicationId}")
        print(f"[ENDPOINT DEBUG] Employment type: {request.employmentType}")
        print(f"[ENDPOINT DEBUG] Monthly income: {request.monthlyIncome}")
        print(f"[ENDPOINT DEBUG] Income mode: {request.incomeMode}")

        await verify_application_ownership(applicationId, current_user)
        result = await application_service.save_income(
            application_id=applicationId,
            user_id=current_user.id,
            employment_type=request.employmentType,
            monthly_income=request.monthlyIncome,
            income_mode=request.incomeMode
        )
        print(f"[ENDPOINT DEBUG] Income saved successfully: {result}")
        return result
    except ValueError as e:
        print(f"[ENDPOINT ERROR] ValueError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ENDPOINT ERROR] Failed to save income: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save income details"
        )


@router.put("/{applicationId}/credit-score", response_model=MessageResponse)
async def save_credit_score(
    applicationId: UUID,
    request: CreditScoreRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        await verify_application_ownership(applicationId, current_user)
        result = await application_service.save_credit_score(
            application_id=applicationId,
            user_id=current_user.id,
            method=request.method,
            score=request.score
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save credit score"
        )


@router.get("/{applicationId}", response_model=LoanApplicationResponse)
async def get_application(
    applicationId: UUID,
    current_user: User = Depends(get_current_user)
):
    try:
        await verify_application_ownership(applicationId, current_user)
        result = await application_service.get_application(applicationId, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch application"
        )


@router.post("/{applicationId}/submit", response_model=CreateLoanApplicationResponse)
async def submit_application(
    applicationId: UUID,
    current_user: User = Depends(get_current_user)
):
    try:
        print(f"[ENDPOINT DEBUG] Submitting application: {applicationId}")
        await verify_application_ownership(applicationId, current_user)
        result = await application_service.submit_application(applicationId, current_user.id)
        print(f"[ENDPOINT DEBUG] Application submitted successfully: {result}")
        return result
    except ValueError as e:
        print(f"[ENDPOINT ERROR] ValueError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ENDPOINT ERROR] Failed to submit application: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit application"
        )
