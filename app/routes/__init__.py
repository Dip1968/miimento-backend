from fastapi import APIRouter

from app.routes.tenant import tenant_router
from app.routes.admin import admin_router

router = APIRouter(prefix="/api/v1")

router.include_router(tenant_router)
router.include_router(admin_router)

