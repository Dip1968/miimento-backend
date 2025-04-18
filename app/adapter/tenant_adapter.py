from functools import lru_cache
from fastapi import HTTPException, Request
from starlette.status import HTTP_403_FORBIDDEN

from app.adapter.mongodb_adapter import super_db
from app.core.constants.db_collections import SuperAdminCollections
from app.config import get_config

config = get_config()


@lru_cache()
def get_tenant_info(tenant_id: str):
    tenant_info = super_db[SuperAdminCollections.TENANTS_CONFIG].find_one(
        {"tenant_url_code": tenant_id}
    )
    return tenant_info


def validate_tenant(request: Request):
    tenant_id = request.headers.get("x-tenant")
    if not tenant_id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Tenant not found")
    tenant = get_tenant_info(tenant_id)
    if not tenant:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Tenant not found")
    return tenant


def validate_authorization_key(request: Request):
    authorization_key = request.headers.get("authorization_key")
    cron_job_api_key = config.CRON_JOB_API_KEY
    if authorization_key != cron_job_api_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="The authorization key does not match, and we are unable to process your request.",
        )
    return authorization_key
