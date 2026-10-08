from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from uuid import UUID

from app.core.security import decode_access_token
from app.models.user import User
from app.services.auth_service import auth_service

security = HTTPBearer()


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    auth_header = request.headers.get("authorization")
    print(f"[AUTH DEBUG] Received Authorization Header: {auth_header}")

    token = credentials.credentials
    print(f"[AUTH DEBUG] Token length: {len(token)} characters")

    payload = decode_access_token(token)

    if payload is None:
        print(f"[AUTH DEBUG] Token decode returned None")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user_id_str = payload.get("sub")
    if user_id_str is None:
        print(f"[AUTH DEBUG] No 'sub' in token payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    print(f"[AUTH DEBUG] User ID from token: {user_id_str}")

    try:
        user_id = UUID(user_id_str)
    except ValueError as e:
        print(f"[AUTH DEBUG] Invalid UUID format: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user = await auth_service.get_user_by_id(user_id)
    if user is None:
        print(f"[AUTH DEBUG] User not found in database for ID: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    print(f"[AUTH DEBUG] User authenticated successfully: {user.id}")
    return user


async def verify_application_ownership(
    application_id: UUID,
    current_user: User = Depends(get_current_user)
) -> None:
    from app.models.loan_application import LoanApplication
    
    application = await LoanApplication.get(application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    if application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this application"
        )
