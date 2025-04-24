from fastapi import APIRouter
from app.routes.tenant.signup_route import sign_up_router
from app.routes.tenant.login_route import login_router

tenant_router = APIRouter(prefix="/tenant")
tenant_router.include_router(sign_up_router)
tenant_router.include_router(login_router)