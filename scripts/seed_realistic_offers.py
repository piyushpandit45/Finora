"""
Seed script to populate MongoDB Atlas with realistic lender products
from major Indian banks and NBFCs with diverse eligibility criteria.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import database
from app.core.config import settings
from app.models.lender_product import LenderProduct, LoanCategory
from beanie import init_beanie


REALISTIC_LENDER_PRODUCTS = [
    # PRIME BANKS (High CIBIL, High Income requirements)
    {
        "lender_name": "HDFC Bank",
        "logo_url": "https://via.placeholder.com/100x100/0066CC/FFFFFF?text=HDFC",
        "category": "PERSONAL",
        "min_amount": 50000,
        "max_amount": 4000000,
        "min_tenure_months": 12,
        "max_tenure_months": 60,
        "interest_rate_min": 10.50,
        "interest_rate_max": 14.00,
        "processing_fee_pct": 2.50,
        "min_cibil": 730,
        "min_monthly_income": 40000,
        "allowed_employment": ["SALARIED", "SELF_EMPLOYED"],
        "min_age": 21,
        "max_age": 60,
        "priority": 100,
        "is_active": True
    },
    {
        "lender_name": "ICICI Bank",
        "logo_url": "https://via.placeholder.com/100x100/FF6600/FFFFFF?text=ICICI",
        "category": "PERSONAL",
        "min_amount": 25000,
        "max_amount": 5000000,
        "min_tenure_months": 12,
        "max_tenure_months": 72,
        "interest_rate_min": 10.75,
        "interest_rate_max": 16.00,
        "processing_fee_pct": 2.25,
        "min_cibil": 720,
        "min_monthly_income": 35000,
        "allowed_employment": ["SALARIED", "SELF_EMPLOYED"],
        "min_age": 21,
        "max_age": 58,
        "priority": 95,
        "is_active": True
    },
    {
        "lender_name": "Axis Bank",
        "logo_url": "https://via.placeholder.com/100x99/A61C00/FFFFFF?text=AXIS",
        "category": "PERSONAL",
        "min_amount": 50000,
        "max_amount": 4000000,
        "min_tenure_months": 12,
        "max_tenure_months": 60,
        "interest_rate_min": 11.00,
        "interest_rate_max": 15.50,
        "processing_fee_pct": 2.00,
        "min_cibil": 710,
        "min_monthly_income": 30000,
        "allowed_employment": ["SALARIED", "SELF_EMPLOYED"],
        "min_age": 21,
        "max_age": 60,
        "priority": 90,
        "is_active": True
    },
    {
        "lender_name": "Kotak Mahindra Bank",
        "logo_url": "https://via.placeholder.com/100x100/E32C2C/FFFFFF?text=KOTAK",
        "category": "PERSONAL",
        "min_amount": 75000,
        "max_amount": 3500000,
        "min_tenure_months": 12,
        "max_tenure_months": 60,
        "interest_rate_min": 10.99,
        "interest_rate_max": 16.00,
        "processing_fee_pct": 2.50,
        "min_cibil": 700,
        "min_monthly_income": 35000,
        "allowed_employment": ["SALARIED", "SELF_EMPLOYED"],
        "min_age": 21,
        "max_age": 58,
        "priority": 88,
        "is_active": True
    },

    # MID-TIER NBFCs (Moderate CIBIL, Moderate Income)
    {
        "lender_name": "Bajaj Finserv",
        "logo_url": "https://via.placeholder.com/100x100/003366/FFFFFF?text=BAJAJ",
        "category": "PERSONAL",
        "min_amount": 10000,
        "max_amount": 3500000,
        "min_tenure_months": 12,
        "max_tenure_months": 60,
        "interest_rate_min": 11.00,
        "interest_rate_max": 20.00,
        "processing_fee_pct": 2.00,
        "min_cibil": 650,
        "min_monthly_income": 25000,
        "allowed_employment": ["SALARIED", "SELF_EMPLOYED"],
        "min_age": 21,
        "max_age": 58,
        "priority": 85,
        "is_active": True
    },
    {
        "lender_name": "Tata Capital",
        "logo_url": "https://via.placeholder.com/100x100/000080/FFFFFF?text=TATA",
        "category": "PERSONAL",
        "min_amount": 75000,
        "max_amount": 3500000,
        "min_tenure_months": 12,
        "max_tenure_months": 72,
        "interest_rate_min": 10.99,
        "interest_rate_max": 18.00,
        "processing_fee_pct": 2.50,
        "min_cibil": 680,
        "min_monthly_income": 30000,
        "allowed_employment": ["SALARIED", "SELF_EMPLOYED"],
        "min_age": 22,
        "max_age": 58,
        "priority": 82,
        "is_active": True
    },
    {
        "lender_name": "Aditya Birla Finance",
        "logo_url": "https://via.placeholder.com/100x100/8B0000/FFFFFF?text=ABF",
        "category": "PERSONAL",
        "min_amount": 50000,
        "max_amount": 3000000,
        "min_tenure_months": 12,
        "max_tenure_months": 60,
        "interest_rate_min": 11.50,
        "interest_rate_max": 19.00,
        "processing_fee_pct": 2.25,
        "min_cibil": 660,
        "min_monthly_income": 28000,
        "allowed_employment": ["SALARIED", "SELF_EMPLOYED"],
        "min_age": 21,
        "max_age": 58,
        "priority": 80,
        "is_active": True
    },

    # DIGITAL LENDERS (Lower CIBIL, Lower Income, Faster processing)
    {
        "lender_name": "Navi Finserv",
        "logo_url": "https://via.placeholder.com/100x100/FF6B35/FFFFFF?text=NAVI",
        "category": "PERSONAL",
        "min_amount": 10000,
        "max_amount": 2000000,
        "min_tenure_months": 3,
        "max_tenure_months": 60,
        "interest_rate_min": 12.00,
        "interest_rate_max": 24.00,
        "processing_fee_pct": 1.50,
        "min_cibil": 620,
        "min_monthly_income": 18000,
        "allowed_employment": ["SALARIED", "SELF_EMPLOYED"],
        "min_age": 21,
        "max_age": 55,
        "priority": 75,
        "is_active": True
    },
    {
        "lender_name": "KreditBee",
        "logo_url": "https://via.placeholder.com/100x100/FFC107/000000?text=KB",
        "category": "PERSONAL",
        "min_amount": 1000,
        "max_amount": 500000,
        "min_tenure_months": 3,
        "max_tenure_months": 18,
        "interest_rate_min": 15.00,
        "interest_rate_max": 29.99,
        "processing_fee_pct": 2.00,
        "min_cibil": 600,
        "min_monthly_income": 15000,
        "allowed_employment": ["SALARIED"],
        "min_age": 21,
        "max_age": 56,
        "priority": 70,
        "is_active": True
    },
    {
        "lender_name": "MoneyTap",
        "logo_url": "https://via.placeholder.com/100x100/00AEEF/FFFFFF?text=MT",
        "category": "PERSONAL",
        "min_amount": 3000,
        "max_amount": 500000,
        "min_tenure_months": 2,
        "max_tenure_months": 36,
        "interest_rate_min": 13.00,
        "interest_rate_max": 24.00,
        "processing_fee_pct": 2.50,
        "min_cibil": 630,
        "min_monthly_income": 20000,
        "allowed_employment": ["SALARIED", "SELF_EMPLOYED"],
        "min_age": 23,
        "max_age": 55,
        "priority": 65,
        "is_active": True
    },
    {
        "lender_name": "CASHe",
        "logo_url": "https://via.placeholder.com/100x100/4CAF50/FFFFFF?text=CASHe",
        "category": "PERSONAL",
        "min_amount": 1000,
        "max_amount": 400000,
        "min_tenure_months": 2,
        "max_tenure_months": 12,
        "interest_rate_min": 18.00,
        "interest_rate_max": 36.00,
        "processing_fee_pct": 3.00,
        "min_cibil": 600,
        "min_monthly_income": 12000,
        "allowed_employment": ["SALARIED"],
        "min_age": 21,
        "max_age": 56,
        "priority": 60,
        "is_active": True
    },

    # SUB-PRIME / NEW TO CREDIT (Very low requirements)
    {
        "lender_name": "EarlySalary",
        "logo_url": "https://via.placeholder.com/100x100/9C27B0/FFFFFF?text=ES",
        "category": "PERSONAL",
        "min_amount": 2000,
        "max_amount": 500000,
        "min_tenure_months": 3,
        "max_tenure_months": 24,
        "interest_rate_min": 18.00,
        "interest_rate_max": 30.00,
        "processing_fee_pct": 2.50,
        "min_cibil": 580,
        "min_monthly_income": 10000,
        "allowed_employment": ["SALARIED"],
        "min_age": 21,
        "max_age": 55,
        "priority": 55,
        "is_active": True
    },
    {
        "lender_name": "LazyPay",
        "logo_url": "https://via.placeholder.com/100x100/FF5722/FFFFFF?text=LP",
        "category": "PERSONAL",
        "min_amount": 1000,
        "max_amount": 300000,
        "min_tenure_months": 3,
        "max_tenure_months": 12,
        "interest_rate_min": 20.00,
        "interest_rate_max": 36.00,
        "processing_fee_pct": 3.50,
        "min_cibil": 570,
        "min_monthly_income": 8000,
        "allowed_employment": ["SALARIED"],
        "min_age": 18,
        "max_age": 55,
        "priority": 50,
        "is_active": True
    },
]


async def seed_lender_products():
    """Seed MongoDB with realistic lender products."""
    print("Connecting to MongoDB...")
    await database.connect()

    print("Initializing Beanie...")
    await init_beanie(
        database=database.client[settings.database_name],
        document_models=[LenderProduct]
    )

    # Clear existing products
    print("Clearing existing lender products...")
    await LenderProduct.delete_all()

    # Insert new products
    print(f"Inserting {len(REALISTIC_LENDER_PRODUCTS)} lender products...")
    for product_data in REALISTIC_LENDER_PRODUCTS:
        product = LenderProduct(**product_data)
        await product.insert()
        print(f"  [OK] {product.lender_name}: INR {product.min_amount:,.0f} - INR {product.max_amount:,.0f} @ {product.interest_rate_min}%-{product.interest_rate_max}%")

    print(f"\n[SUCCESS] Successfully seeded {len(REALISTIC_LENDER_PRODUCTS)} lender products!")
    print("\nProduct Summary:")
    print(f"  Prime Banks (CIBIL 700+): 4 offers")
    print(f"  Mid-Tier NBFCs (CIBIL 650+): 3 offers")
    print(f"  Digital Lenders (CIBIL 620+): 3 offers")
    print(f"  Sub-Prime (CIBIL 570+): 2 offers")

    await database.disconnect()


if __name__ == "__main__":
    asyncio.run(seed_lender_products())
