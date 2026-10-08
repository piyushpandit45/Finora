from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID
from app.schemas.offer import OffersListResponse, OfferDetailResponse, OfferResponse
from app.api.dependencies import get_current_user, verify_application_ownership
from app.models.user import User
from app.models.loan_application import LoanApplication
from app.services.match_engine import match_engine

router = APIRouter(prefix="/loan-applications", tags=["Offers"])


@router.get("/{applicationId}/offers", response_model=OffersListResponse)
async def get_offers(
    applicationId: UUID,
    current_user: User = Depends(get_current_user)
):
    try:
        await verify_application_ownership(applicationId, current_user)

        application = await LoanApplication.get(applicationId)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )

        print(f"[OFFERS ENDPOINT] Fetching offers for application: {applicationId}")

        offers = await match_engine.get_offers_by_application(applicationId)

        if not offers:
            print(f"[OFFERS ENDPOINT] No existing offers, running match engine")
            offers = await match_engine.match_application(applicationId)

        offer_responses = [
            OfferResponse(**offer)
            for offer in offers
        ]

        print(f"[OFFERS ENDPOINT] Returning {len(offer_responses)} offers")

        return OffersListResponse(
            success=True,
            totalMatches=len(offer_responses),
            applicationId=str(applicationId),
            offers=offer_responses
        )
    except ValueError as e:
        print(f"[OFFERS ERROR] ValueError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[OFFERS ERROR] Exception: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch offers"
        )


@router.get("/offers/{offerId}", response_model=OfferDetailResponse)
async def get_offer(
    offerId: UUID,
    current_user: User = Depends(get_current_user)
):
    try:
        offer = await match_engine.get_offer_by_id(offerId)

        application = await LoanApplication.get(offer.application_id)
        if application.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this offer"
            )

        # Calculate EMI dynamically
        monthly_emi = match_engine.calculate_emi(
            offer.offered_amount,
            offer.interest_rate,
            offer.tenure_months
        )

        return OfferDetailResponse(
            id=str(offer.id),
            applicationId=str(offer.application_id),
            lenderName=offer.lender_name,
            logoUrl="https://via.placeholder.com/100x100/CCCCCC/666666?text=" + offer.lender_name[:3].upper(),
            loanAmount=offer.offered_amount,
            interestRate=offer.interest_rate,
            tenureMonths=offer.tenure_months,
            monthlyEmi=monthly_emi,
            processingFee=offer.processing_fee,
            matchPercentage=85,  # Default for historical offers
            badge=offer.badge,
            category="PERSONAL",
            redirectUrl=offer.redirect_url
        )
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
            detail="Failed to fetch offer"
        )
