# Finora Backend API

A production-ready Python FastAPI backend for the Finora loan application system.

## Tech Stack

- **Framework**: FastAPI 0.109.0
- **Server**: Uvicorn
- **Database**: MongoDB Atlas with async Motor driver
- **ODM**: Beanie (built on Motor and Pydantic v2)
- **Caching**: Redis (with in-memory fallback)
- **Authentication**: JWT with Bearer scheme
- **Security**: Fernet encryption for PAN, bcrypt for passwords
- **Validation**: Pydantic v2

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── dependencies.py          # Auth dependencies
│   │   └── v1/
│   │       ├── endpoints/           # API route handlers
│   │       │   ├── auth.py
│   │       │   ├── users.py
│   │       │   ├── applications.py
│   │       │   ├── offers.py
│   │       │   ├── dashboard.py
│   │       │   └── support.py
│   │       └── router.py            # API router aggregation
│   ├── core/
│   │   ├── config.py                # Configuration via pydantic-settings
│   │   ├── database.py              # MongoDB connection manager
│   │   └── security.py              # JWT, encryption helpers
│   ├── middlewares/
│   │   ├── cors.py                  # CORS middleware
│   │   └── exception_handler.py     # Global exception handlers
│   ├── models/                      # Beanie document models
│   │   ├── user.py
│   │   ├── user_profile.py
│   │   ├── loan_application.py
│   │   ├── kyc_details.py
│   │   ├── income_details.py
│   │   ├── credit_score.py
│   │   ├── lender.py
│   │   ├── loan_offer.py
│   │   ├── notification.py
│   │   ├── support_ticket.py
│   │   └── faq.py
│   ├── schemas/                     # Pydantic request/response DTOs
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── loan_application.py
│   │   ├── offer.py
│   │   ├── dashboard.py
│   │   ├── notification.py
│   │   └── support.py
│   └── services/                    # Business logic layer
│       ├── otp_service.py
│       ├── auth_service.py
│       ├── application_service.py
│       ├── bureau_adapter.py
│       └── match_engine.py
├── main.py                          # Application entry point
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and update with your credentials:

```bash
cp .env.example .env
```

Update the following values in `.env`:
- `MONGODB_URL`: Your MongoDB Atlas connection string
- `DATABASE_NAME`: Your database name (default: finora_db)
- `REDIS_URL`: Redis connection string (optional, falls back to in-memory)
- `JWT_SECRET`: Generate a secure random string for JWT signing
- `PAN_ENCRYPTION_KEY`: Generate a secure 32-byte key for PAN encryption

### 3. Generate Encryption Keys

For PAN encryption, generate a Fernet-compatible key:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

Use the output as your `PAN_ENCRYPTION_KEY` in `.env`.

### 4. Run the Server

Development mode with auto-reload:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Production mode:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Authentication (`/api/v1/auth`)

- `POST /api/v1/auth/send-otp` - Send OTP to mobile number
- `POST /api/v1/auth/verify-otp` - Verify OTP and get JWT token
- `POST /api/v1/auth/resend-otp` - Resend OTP

### User Profile (`/api/v1/users`)

- `GET /api/v1/users/me` - Get current user profile (requires JWT)
- `PUT /api/v1/users/me` - Update user profile (requires JWT)

### Loan Applications (`/api/v1/loan-applications`)

- `POST /api/v1/loan-applications` - Create new loan application
- `PUT /api/v1/loan-applications/{applicationId}/kyc` - Save KYC details
- `PUT /api/v1/loan-applications/{applicationId}/income` - Save income details
- `PUT /api/v1/loan-applications/{applicationId}/credit-score` - Save credit score
- `GET /api/v1/loan-applications/{applicationId}` - Get application details
- `POST /api/v1/loan-applications/{applicationId}/submit` - Submit application

### Offers (`/api/v1/loan-applications`)

- `GET /api/v1/loan-applications/{applicationId}/offers` - Get matched offers
- `GET /api/v1/offers/{offerId}` - Get offer details

### Dashboard (`/api/v1/dashboard`)

- `GET /api/v1/dashboard` - Get dashboard summary

### Notifications (`/api/v1/notifications`)

- `GET /api/v1/notifications` - Get user notifications
- `POST /api/v1/notifications/{notificationId}/read` - Mark notification as read

### Support (`/api/v1/support`)

- `GET /api/v1/support/faqs` - Get FAQs
- `POST /api/v1/support/tickets` - Create support ticket

## Security Features

- **JWT Authentication**: Bearer token authentication with configurable expiration
- **PAN Encryption**: Fernet encryption for sensitive PAN data
- **Rate Limiting**: OTP requests limited to 3 attempts per 10 minutes per mobile
- **Authorization**: User ownership verification for all application accesses
- **CORS**: Configured for React Native Expo origins
- **Input Validation**: Pydantic v2 validation on all endpoints

## Database Collections

The application initializes the following MongoDB collections:

1. `users` - User accounts
2. `user_profiles` - User profile information
3. `loan_applications` - Loan application records
4. `kyc_details` - KYC information (encrypted PAN)
5. `income_details` - Income and employment details
6. `credit_scores` - Credit score records
7. `lenders` - Lender eligibility rules
8. `loan_offers` - Generated loan offers
9. `notifications` - User notifications
10. `support_tickets` - Support tickets
11. `faqs` - FAQ database

All collections have appropriate indexes for performance.

## Initial Data Seeding

On first startup, the application automatically seeds:
- 5 sample lenders with different eligibility criteria
- 8 FAQs covering common questions

## Redis Configuration

Redis is used for:
- OTP storage with TTL (120 seconds)
- Rate limiting (3 attempts per 10 minutes)

If Redis is not available, the application falls back to an in-memory store.

## Development Notes

- The application uses Beanie ODM for MongoDB with async/await
- All database operations are non-blocking
- Error responses follow a consistent JSON format
- Logging is configured for debugging and monitoring

## Testing the API

Once the server is running, visit:
- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc
- Health check: http://localhost:8000/health
