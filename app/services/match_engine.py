from typing import List, Dict, Any
from uuid import UUID
import logging
import math

from app.models.loan_application import LoanApplication, ApplicationStatus, ApplicationStep
from app.models.lender_product import LenderProduct
from app.models.loan_offer import LoanOffer
from app.models.kyc_details import KYCDetails
from app.models.income_details import IncomeDetails, EmploymentType
from app.models.credit_score import CreditScore

logger = logging.getLogger(__name__)


class MatchEngine:
    def __init__(self):
        self.default_tenure_months = 36  # Default 3 years for EMI calculation

    def calculate_emi(self, principal: float, annual_rate: float, tenure_months: int) -> float:
        """
        Calculate EMI using reducing balance method.
        EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
        where r = monthly interest rate, n = tenure in months
        """
        monthly_rate = annual_rate / 12 / 100
        if monthly_rate == 0:
            return principal / tenure_months

        emi = principal * monthly_rate * (1 + monthly_rate) ** tenure_months / ((1 + monthly_rate) ** tenure_months - 1)
        return round(emi, 2)

    def calculate_match_percentage(
        self,
        user_cibil: int,
        required_cibil: int,
        user_income: float,
        required_income: float
    ) -> int:
        """
        Calculate eligibility match percentage based on how far user exceeds minimums.
        """
        cibil_diff = user_cibil - required_cibil
        income_ratio = user_income / required_income if required_income > 0 else 1

        # CIBIL score impact (max 50 points)
        cibil_score = min(50, max(0, cibil_diff / 10))

        # Income ratio impact (max 50 points)
        income_score = min(50, max(0, (income_ratio - 1) * 20))

        match_pct = 60 + cibil_score + income_score  # Base 60% for meeting minimums
        return min(100, int(match_pct))

    async def match_application(self, application_id: UUID) -> List[Dict[str, Any]]:
        """
        Match application against all lender products and return calculated offers.
        """
        application = await LoanApplication.get(application_id)
        if not application:
            raise ValueError("Application not found")

        kyc = await KYCDetails.find_one(KYCDetails.application_id == application_id)
        income = await IncomeDetails.find_one(IncomeDetails.application_id == application_id)
        credit_score = await CreditScore.find_one(CreditScore.application_id == application_id)

        if not kyc or not income or not credit_score:
            raise ValueError("Incomplete application data - KYC, Income, and Credit Score required")

        user_cibil = credit_score.score or 650  # Default to 650 if missing
        user_income = income.monthly_income
        user_employment = income.employment_type if isinstance(income.employment_type, str) else income.employment_type.value
        user_age = kyc.age
        requested_amount = application.loan_amount

        print(f"[MATCH ENGINE] User Profile: CIBIL={user_cibil}, Income={user_income}, Employment={user_employment}, Age={user_age}")

        # Fetch all active lender products
        lender_products = await LenderProduct.find(LenderProduct.is_active == True).to_list()
        print(f"[MATCH ENGINE] Found {len(lender_products)} active lender products")

        matched_offers = []
        for product in lender_products:
            # Check eligibility criteria
            meets_cibil = user_cibil >= product.min_cibil
            meets_income = user_income >= product.min_monthly_income
            meets_employment = user_employment in product.allowed_employment
            meets_age = product.min_age <= user_age <= (product.max_age or 65)
            meets_amount = requested_amount <= product.max_amount

            if all([meets_cibil, meets_income, meets_employment, meets_age, meets_amount]):
                # Calculate personalized offer
                approved_amount = min(requested_amount, product.max_amount)

                # Use min interest rate for better match, or interpolate based on CIBIL
                if user_cibil >= 750:
                    interest_rate = product.interest_rate_min
                elif user_cibil >= 700:
                    interest_rate = product.interest_rate_min + (product.interest_rate_max - product.interest_rate_min) * 0.3
                else:
                    interest_rate = product.interest_rate_min + (product.interest_rate_max - product.interest_rate_min) * 0.6

                tenure = min(self.default_tenure_months, product.max_tenure_months)
                monthly_emi = self.calculate_emi(approved_amount, interest_rate, tenure)
                processing_fee = approved_amount * (product.processing_fee_pct / 100)
                match_pct = self.calculate_match_percentage(
                    user_cibil, product.min_cibil,
                    user_income, product.min_monthly_income
                )

                # Determine badge
                badge = ""
                if match_pct >= 95:
                    badge = "Best Match"
                elif match_pct >= 85:
                    badge = "Instant Approval"
                elif match_pct >= 75:
                    badge = "Quick Approval"

                offer = {
                    "id": str(product.id),
                    "lenderName": product.lender_name,
                    "logoUrl": product.logo_url,
                    "loanAmount": approved_amount,
                    "interestRate": round(interest_rate, 2),
                    "tenureMonths": tenure,
                    "monthlyEmi": monthly_emi,
                    "processingFee": round(processing_fee, 2),
                    "matchPercentage": match_pct,
                    "badge": badge,
                    "category": product.category if isinstance(product.category, str) else product.category.value,
                    "priority": product.priority
                }
                matched_offers.append(offer)
                print(f"[MATCH ENGINE] ✓ Matched: {product.lender_name} - ₹{approved_amount:,.0f} @ {interest_rate:.2f}% (Match: {match_pct}%)")

        # Sort by match percentage and priority
        matched_offers.sort(key=lambda x: (-x["matchPercentage"], -x.get("priority", 0)), reverse=False)

        # If no matches, provide a fallback starter offer
        if not matched_offers:
            print("[MATCH ENGINE] No strict matches found, providing starter offer")
            starter_offer = {
                "id": "starter-offer",
                "lenderName": "Finora Starter",
                "logoUrl": "https://via.placeholder.com/100x100/4CAF50/FFFFFF?text=FINORA",
                "loanAmount": min(requested_amount, 50000),
                "interestRate": 18.00,
                "tenureMonths": 12,
                "monthlyEmi": self.calculate_emi(min(requested_amount, 50000), 18.00, 12),
                "processingFee": round(min(requested_amount, 50000) * 0.03, 2),
                "matchPercentage": 60,
                "badge": "Starter Offer",
                "category": "PERSONAL",
                "priority": 0
            }
            matched_offers.append(starter_offer)

        # Save only real offers to database (exclude starter offer)
        real_offers = [offer for offer in matched_offers if offer.get("id") != "starter-offer"]
        await self._save_offers_to_db(application_id, real_offers)

        # Update application status
        application.status = ApplicationStatus.MATCHED
        application.current_step = ApplicationStep.OFFERS
        await application.save()

        logger.info(f"Matched {len(matched_offers)} offers for application: {application_id}")
        return matched_offers

    async def _save_offers_to_db(self, application_id: UUID, offers: List[Dict[str, Any]]):
        """Save calculated offers to database for persistence."""
        # Clear existing offers for this application
        await LoanOffer.find(LoanOffer.application_id == application_id).delete()

        # Insert new offers
        for offer in offers:
            db_offer = LoanOffer(
                application_id=application_id,
                lender_id=UUID(offer["id"]) if offer["id"] != "starter-offer" else None,
                lender_name=offer["lenderName"],
                offered_amount=offer["approvedAmount"],
                interest_rate=offer["interestRate"],
                processing_fee=offer["processingFee"],
                tenure_months=offer["tenureMonths"],
                badge=offer["badge"],
                redirect_url=f"https://finora.app/apply/{application_id}?lender={offer['lenderName']}"
            )
            await db_offer.insert()

    async def get_offers_by_application(self, application_id: UUID) -> List[Dict[str, Any]]:
        """Retrieve calculated offers for an application."""
        # First check if we have persisted offers
        db_offers = await LoanOffer.find(LoanOffer.application_id == application_id).to_list()

        if db_offers:
            # Convert to API format
            offers = []
            for db_offer in db_offers:
                offer = {
                    "id": str(db_offer.id),
                    "lenderName": db_offer.lender_name,
                    "loanAmount": db_offer.offered_amount,
                    "interestRate": db_offer.interest_rate,
                    "tenureMonths": db_offer.tenure_months,
                    "monthlyEmi": self.calculate_emi(
                        db_offer.offered_amount,
                        db_offer.interest_rate,
                        db_offer.tenure_months
                    ),
                    "processingFee": db_offer.processing_fee,
                    "matchPercentage": 85,  # Default for historical offers
                    "badge": db_offer.badge,
                    "logoUrl": "https://via.placeholder.com/100x100/CCCCCC/666666?text=" + db_offer.lender_name[:3].upper(),
                    "category": "PERSONAL"
                }
                offers.append(offer)
            return offers

        # If no persisted offers, run matching
        return await self.match_application(application_id)

    async def get_offer_by_id(self, offer_id: UUID) -> LoanOffer:
        offer = await LoanOffer.get(offer_id)
        if not offer:
            raise ValueError("Offer not found")
        return offer


match_engine = MatchEngine()
