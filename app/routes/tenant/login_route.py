from fastapi import APIRouter, Depends
from app.adapter.tenant_adapter import validate_tenant
from app.controller.tenant import login_controller
from app.model.tenant.user import ForgotPasswordRequest, ResetPasswordRequest, UserLogin

login_router = APIRouter(prefix="/auth")


@login_router.post("/login")  # Changed to POST for login requests
def login_route(user_data: UserLogin, tenant: dict = Depends(validate_tenant)):
    login_status = login_controller.login_user_controller(
        user_data, tenant.get("db_cred")
    )
    return login_status


@login_router.post("/forgot-password")  # Changed to POST for login requests
def forgot_password(
    request: ForgotPasswordRequest, tenant: dict = Depends(validate_tenant)
):
    password_status = login_controller.forgot_password_controller(request.email, tenant)
    return password_status


@login_router.post("/reset-password")  # Changed to POST for login requests
def reset_password(
    request: ResetPasswordRequest, token: str, tenant: dict = Depends(validate_tenant)
):
    password = login_controller.reset_password_controller(
        token, request.new_password, request.confirm_password, tenant.get("db_cred")
    )
    print(f"Password Status: {password}")  # Debugging line
    return password
