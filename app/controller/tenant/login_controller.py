from app.adapter.mongodb_adapter import get_tenant_db_conn
from app.core.constants.error_constants import ERROR_ENUMS, ErrorStatusCodes
from app.core.constants.resp_constants import RESPONSE_CONSTANT
from app.core.error_handler import ExceptionHandler, custom_exception_handler
from app.core.response_handler import resp_handler
from app.model.tenant.user import UserLogin
from app.services.tenant import login_services


def login_user_controller(user_data: UserLogin, tenant):
    try:
        # Await for connection
        db_conn = get_tenant_db_conn(tenant)
        # Await for service call
        resp, err = login_services.login_user(
            user_data.email, user_data.password, db_conn
        )

        if err:
            return custom_exception_handler(
                ERROR_ENUMS[err]["ErrorCode"],
                ERROR_ENUMS[err]["ErrorMessage"],
            )

        if not resp:
            return custom_exception_handler(
                ERROR_ENUMS["LOGIN"]["ErrorCode"],
                ERROR_ENUMS["LOGIN"]["ErrorMessage"],
            )

        return resp_handler(
            RESPONSE_CONSTANT["login"].get("msg"),
            resp,
            response_status_code=RESPONSE_CONSTANT["login"].get("code"),
        )
    except Exception as e:
        raise ExceptionHandler(
            status_code=ErrorStatusCodes.get("UNCAUGHT_ERROR"),
            detail={
                "ErrorMessage": ERROR_ENUMS["COMMON"]["ErrorMessage"],
                "ErrorCode": ERROR_ENUMS["COMMON"]["ErrorCode"],
                "ExceptionLog": str(e),
            },
        ) from e


def forgot_password_controller(email, tenant):
    try:
        # Await for connection
        db_conn = get_tenant_db_conn(tenant.get("db_cred"))
        # Await for service call
        resp, link_already_sent = login_services.forgot_password(tenant, email, db_conn)
        if link_already_sent:
            return custom_exception_handler(
                ERROR_ENUMS["RESET_PASSWORD_LINK_ALREADY_SENT"]["ErrorCode"],
                ERROR_ENUMS["RESET_PASSWORD_LINK_ALREADY_SENT"]["ErrorMessage"],
            )

        if not resp:
            return custom_exception_handler(
                ERROR_ENUMS["FORGOT_PASSWORD"]["ErrorCode"],
                ERROR_ENUMS["FORGOT_PASSWORD"]["ErrorMessage"],
            )

        return resp_handler(
            RESPONSE_CONSTANT["forgot_password"].get("msg"),
            resp,
            response_status_code=RESPONSE_CONSTANT["forgot_password"].get("code"),
        )
    except Exception as e:
        raise ExceptionHandler(
            status_code=ErrorStatusCodes.get("UNCAUGHT_ERROR"),
            detail={
                "ErrorMessage": ERROR_ENUMS["COMMON"]["ErrorMessage"],
                "ErrorCode": ERROR_ENUMS["COMMON"]["ErrorCode"],
                "ExceptionLog": str(e),
            },
        ) from e


def reset_password_controller(token, new_password, conf_password, tenant):
    try:
        # Await for connection
        db_conn = get_tenant_db_conn(tenant)
        is_link_valid = login_services.validate_reset_password_link(token, db_conn)
        if not is_link_valid:
            return custom_exception_handler(
                ERROR_ENUMS["RESET_PASSWORD_LINK_EXPIRED"]["ErrorCode"],
                ERROR_ENUMS["RESET_PASSWORD_LINK_EXPIRED"]["ErrorMessage"],
            )

        # Await for service call
        resp = login_services.reset_password(
            token, new_password, conf_password, db_conn
        )
        if not resp:
            return custom_exception_handler(
                ERROR_ENUMS["RESET_PASSWORD"]["ErrorCode"],
                ERROR_ENUMS["RESET_PASSWORD"]["ErrorMessage"],
            )

        return resp_handler(
            RESPONSE_CONSTANT["reset_password"].get("msg"),
            resp,
            response_status_code=RESPONSE_CONSTANT["reset_password"].get("code"),
        )

    except Exception as e:
        raise ExceptionHandler(
            status_code=ErrorStatusCodes.get("UNCAUGHT_ERROR"),
            detail={
                "ErrorMessage": ERROR_ENUMS["COMMON"]["ErrorMessage"],
                "ErrorCode": ERROR_ENUMS["COMMON"]["ErrorCode"],
                "ExceptionLog": str(e),
            },
        ) from e
