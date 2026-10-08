from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, applications, offers, dashboard, support

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(applications.router)
api_router.include_router(offers.router)
api_router.include_router(dashboard.router)
api_router.include_router(support.router)
api_router.include_router(support.support_router, prefix="/support")
