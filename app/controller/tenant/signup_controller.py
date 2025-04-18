from fastapi import BackgroundTasks
from fastapi.encoders import jsonable_encoder
from app.core.constants.error_constants import ERROR_ENUMS, ErrorStatusCodes
from app.core.constants.resp_constants import RESPONSE_CONSTANT
from app.core.error_handler import ExceptionHandler, custom_exception_handler
from app.core.response_handler import resp_handler
from app.model.tenant.signup_model import SignUpWizardReqModel
from app.services.tenant import signup_services


def signup_mentor_controller(data, background_tasks):
    try:
        # is_turnstile_request_verify = signup_services.verify_turnstile(data.token)
        # if not is_turnstile_request_verify["success"]:
        #     return custom_exception_handler(
        #         ERROR_ENUMS["SECURITY_CHECK_FAILED"]["ErrorCode"],
        #         ERROR_ENUMS["SECURITY_CHECK_FAILED"]["ErrorMessage"],
        #     )
        is_email_exist = signup_services.verify_email(data.email)
        if is_email_exist is not None:
            return custom_exception_handler(
                ERROR_ENUMS["EMAIL_ALREADY_EXIST"]["ErrorCode"],
                ERROR_ENUMS["EMAIL_ALREADY_EXIST"]["ErrorMessage"],
            )
        save_mentor = signup_services.insert_mentor_data(data)
        if not save_mentor.acknowledged:
            raise ValueError(ERROR_ENUMS["COMMON"])

        background_tasks.add_task(
            signup_services.send_signup_verification_email, save_mentor, data
        )
        return resp_handler(
            RESPONSE_CONSTANT["sign_up"].get("msg"),
            [],
            response_status_code=RESPONSE_CONSTANT["sign_up"].get("code"),
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

def validate_sign_up_email_link(verification_code: str):
    tenant_info = signup_services.validate_tenant_sign_up_link(
        {"verification_link": verification_code}
    )
    if tenant_info is None:
        return custom_exception_handler(
            ERROR_ENUMS["INVALID_VERIFICATION_CODE"]["ErrorCode"],
            ERROR_ENUMS["INVALID_VERIFICATION_CODE"]["ErrorMessage"],
        )
    return resp_handler(
        RESPONSE_CONSTANT["validate_link"].get("msg"),
        jsonable_encoder(tenant_info),
        response_status_code=RESPONSE_CONSTANT["validate_link"].get("code"),
    )
    
def sign_up_wizard_controller(
    data: SignUpWizardReqModel, logo, background_tasks: BackgroundTasks
):
    try:
        is_link_valid = signup_services.validate_tenant_sign_up_link(
            {"verification_link": data.verification_code}
        )
        if is_link_valid is None:
            return custom_exception_handler(
                ERROR_ENUMS["INVALID_VERIFICATION_CODE"]["ErrorCode"],
                ERROR_ENUMS["INVALID_VERIFICATION_CODE"]["ErrorMessage"],
            )

        is_tenant_code_valid = signup_services.check_duplicate_tenant_data(
            data.tenant_url_code
        )
        if is_tenant_code_valid is not None:
            return custom_exception_handler(
                ERROR_ENUMS["INVALID_TENANT_URL_CODE"]["ErrorCode"],
                ERROR_ENUMS["INVALID_TENANT_URL_CODE"]["ErrorMessage"],
            )
        file_name = signup_services.store_company_logo(logo, data.model_dump())
        data.logo = file_name.get("unique_filename")
        tenant_info = signup_services.insert_signup_wizard_data(data)

        background_tasks.add_task(
            signup_services.signup_wizard_background_tasks,
            tenant_url_code=tenant_info.get("tenant_url_code"),
            person_name=tenant_info.get("first_name"),
            tenant_info=tenant_info,
            password=data.password,
        )

        return resp_handler(
            RESPONSE_CONSTANT["sign_up_wizard"].get("msg"),
            jsonable_encoder(tenant_info),
            response_status_code=RESPONSE_CONSTANT["sign_up_wizard"].get("code"),
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