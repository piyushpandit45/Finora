from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.core.config import settings
from app.core.database import database
from app.models import (
    User,
    UserProfile,
    LoanApplication,
    KYCDetails,
    IncomeDetails,
    CreditScore,
    Lender,
    LenderProduct,
    LoanOffer,
    Notification,
    SupportTicket,
    FAQ,
)
from app.api.v1.router import api_router
from app.middlewares.cors import add_cors_middleware
from app.middlewares.exception_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from app.services.otp_service import otp_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    
    await database.connect()
    await database.init_beanie([
        User,
        UserProfile,
        LoanApplication,
        KYCDetails,
        IncomeDetails,
        CreditScore,
        Lender,
        LenderProduct,
        LoanOffer,
        Notification,
        SupportTicket,
        FAQ,
    ])
    
    await otp_service.connect()
    
    await seed_initial_data()
    
    logger.info("Application startup complete")
    
    yield
    
    logger.info("Shutting down application...")
    await otp_service.disconnect()
    await database.disconnect()
    logger.info("Application shutdown complete")


async def seed_initial_data():
    from app.models.lender import Lender
    from app.models.faq import FAQ
    
    lender_count = await Lender.count()
    if lender_count == 0:
        logger.info("Seeding initial lenders...")
        lenders = [
            Lender(
                name="HDFC Bank",
                min_score=650,
                min_income=25000,
                min_age=21,
                base_roi=12.5,
                processing_fee=2000,
                is_active=True
            ),
            Lender(
                name="ICICI Bank",
                min_score=600,
                min_income=20000,
                min_age=21,
                base_roi=13.0,
                processing_fee=1500,
                is_active=True
            ),
            Lender(
                name="Axis Bank",
                min_score=700,
                min_income=30000,
                min_age=22,
                base_roi=11.5,
                processing_fee=2500,
                is_active=True
            ),
            Lender(
                name="Kotak Mahindra Bank",
                min_score=650,
                min_income=25000,
                min_age=21,
                base_roi=12.0,
                processing_fee=1800,
                is_active=True
            ),
            Lender(
                name="Bajaj Finserv",
                min_score=550,
                min_income=15000,
                min_age=20,
                base_roi=14.0,
                processing_fee=1000,
                is_active=True
            ),
        ]
        for lender in lenders:
            await lender.insert()
        logger.info(f"Seeded {len(lenders)} lenders")
    
    faq_count = await FAQ.count()
    if faq_count == 0:
        logger.info("Seeding initial FAQs...")
        faqs = [
            FAQ(
                question="What documents are required for a loan application?",
                answer="You will need to provide your PAN card, proof of identity (Aadhaar/Passport), proof of address, income proof (salary slips or IT returns), and bank statements for the last 3 months.",
                category="Documentation"
            ),
            FAQ(
                question="How long does it take to get loan approval?",
                answer="Loan approval typically takes 24-48 hours after submission of all required documents. Some lenders offer instant approval within a few hours.",
                category="Process"
            ),
            FAQ(
                question="What is the minimum credit score required?",
                answer="The minimum credit score required varies by lender, typically ranging from 550 to 700. A higher credit score improves your chances of approval and may get you better interest rates.",
                category="Eligibility"
            ),
            FAQ(
                question="Can I prepay my loan?",
                answer="Yes, most lenders allow loan prepayment. However, some may charge a prepayment fee, typically 2-5% of the outstanding principal amount.",
                category="Repayment"
            ),
            FAQ(
                question="What happens if I miss an EMI payment?",
                answer="Missing an EMI payment can negatively impact your credit score and may attract late payment charges. It's important to inform your lender in advance if you anticipate any payment difficulties.",
                category="Repayment"
            ),
            FAQ(
                question="How is the interest rate determined?",
                answer="Interest rates are determined based on your credit score, income, employment stability, loan amount, and tenure. Lenders may also consider the lender's internal policies and market conditions.",
                category="Interest"
            ),
            FAQ(
                question="What is a processing fee?",
                answer="A processing fee is a one-time charge levied by lenders to cover the cost of processing your loan application. It typically ranges from 0.5% to 3% of the loan amount.",
                category="Fees"
            ),
            FAQ(
                question="Can I apply for a loan if I'm self-employed?",
                answer="Yes, self-employed individuals can apply for loans. You will need to provide business registration documents, income tax returns, and bank statements to verify your income.",
                category="Eligibility"
            ),
        ]
        for faq in faqs:
            await faq.insert()
        logger.info(f"Seeded {len(faqs)} FAQs")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Finora Loan Application Backend API",
    lifespan=lifespan,
)

add_cors_middleware(app)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "message": "Finora Backend API",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if database.client else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
