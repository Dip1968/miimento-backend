from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from pymongo.database import Database
from app.core.constants.email_templates import (
    FORGOT_PASSWORD_EMAIL_VERIFICATION_TEMPLATE,
)
from app.core.constants.db_collections import TenantCollections
from app.core.constants.error_constants import ERROR_ENUMS
from app.utils.auth_utils import hash_password, verify_password
from app.utils.jwt_utils import create_access_token
from app.utils.email_utils import email_util
from app.utils.string_utils import generate_random_string
from app.config import get_config

config = get_config()


def login_user(email, password, db_conn: Database):
    user_collection = db_conn[TenantCollections.USERS]
    # Retrieve the user by email
    user = user_collection.find_one(
        {"email": email},
        {
            "_id": 1,
            "name": 1,
            "email": 1,
            "password": 1,
            "role_id": 1,
            "is_email_verified": 1,
            "role_name": 1,
        },
    )

    if not user.get("is_email_verified", True):
        return None, "USER_EMAIL_VERIFICATION_PENDING"
    if user and user["password"] and verify_password(password, user["password"]):
        # Prepare the data for the token
        token_data = {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role_id": user["role_id"],
            "role_name": user.get("role_name"),
        }
        token = create_access_token(data=token_data)

        # Return user info along with the token

        return {
            "user": {
                "name": user["name"],
                "email": user["email"],
                "role_id": user["role_id"],
                "role_name": user.get("role_name"),
            },
            "access_token": token,
        }, None
    return False, None


def forgot_password(tenant, email, db_conn: Database):
    user = db_conn[TenantCollections.USERS].find_one({"email": email})

    if not user:
        return None, False

    verification_time = user.get("verification_link_sent_at")
    if verification_time:
        # Check if the link is older than 5 Minutes
        if datetime.now() - verification_time < timedelta(minutes=5):
            return user, True

    random_string = generate_random_string(20)
    reset_link = f"{
        config.UI_HOST_URL}/auth/reset-password?token={random_string}&tenant={tenant.get("tenant_url_code")}"
    update_result = db_conn[TenantCollections.USERS].update_one(
        {"email": email},
        {
            "$set": {
                "verification_link": random_string,
                "verification_link_sent_at": datetime.now(timezone.utc),
            }
        },
    )

    if update_result.matched_count == 0:
        return None, False

    # Send an email with the reset link
    email_util.send_email(
        to_address=email,
        subject=FORGOT_PASSWORD_EMAIL_VERIFICATION_TEMPLATE.subject,
        body=FORGOT_PASSWORD_EMAIL_VERIFICATION_TEMPLATE.get_body_with_variables(
            verify_link=reset_link
        ),
        is_html=FORGOT_PASSWORD_EMAIL_VERIFICATION_TEMPLATE.is_html,
    )

    return reset_link, False


def validate_reset_password_link(token, db_conn: Database):
    # Find the user by the verification link token
    user = db_conn[TenantCollections.USERS].find_one({"verification_link": token})
    if user:
        verification_time = user.get("verification_link_sent_at")
        if verification_time:
            # Check if the link is older than 24 hours
            if datetime.now() - verification_time > timedelta(hours=24):
                return False
    return True


def reset_password(token, new_password, conf_password, db_conn: Database):
    if new_password != conf_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_ENUMS["MATCH_PASSWORD"]["ErrorMessage"],
        )

    # Find the user by the verification link token
    user = db_conn[TenantCollections.USERS].find_one({"verification_link": token})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_ENUMS["TOKEN_VALIDATION"]["ErrorMessage"],
        )

    # Hash the new password
    hashed_password = hash_password(new_password)

    # Update the user's password and remove the verification link
    result = db_conn[TenantCollections.USERS].update_one(
        {"email": user["email"]},
        {
            "$set": {"password": hashed_password},
            "$unset": {"verification_link": "", "verification_link_sent_at": ""},
        },
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_ENUMS["USER_MATCH"]["ErrorMessage"],
        )

    return True
