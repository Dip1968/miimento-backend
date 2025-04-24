# controller.py
from fastapi import BackgroundTasks, UploadFile
from fastapi.encoders import jsonable_encoder
from app.core.constants.error_constants import ERROR_ENUMS, ErrorStatusCodes
from app.core.constants.resp_constants import RESPONSE_CONSTANT
from app.core.error_handler import ExceptionHandler, custom_exception_handler
from app.core.response_handler import resp_handler
from app.model.tenant.signup_model import (
    MentorSignUpWizardReqModel, 
    InstituteSignUpWizardReqModel
)
from app.services.tenant import signup_services


def signup_controller(data, background_tasks):
    try:
        is_email_exist = signup_services.verify_email(data.email)
        if is_email_exist is not None:
            return custom_exception_handler(
                ERROR_ENUMS["EMAIL_ALREADY_EXIST"]["ErrorCode"],
                ERROR_ENUMS["EMAIL_ALREADY_EXIST"]["ErrorMessage"],
            )
        save_user = signup_services.insert_user_data(data)
        if not save_user.acknowledged:
            raise ValueError(ERROR_ENUMS["COMMON"])

        background_tasks.add_task(
            signup_services.send_signup_verification_email, save_user, data
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
    user_info = signup_services.validate_sign_up_link(
        {"verification_link": verification_code}
    )
    if user_info is None:
        return custom_exception_handler(
            ERROR_ENUMS["INVALID_VERIFICATION_CODE"]["ErrorCode"],
            ERROR_ENUMS["INVALID_VERIFICATION_CODE"]["ErrorMessage"],
        )
    return resp_handler(
        RESPONSE_CONSTANT["validate_link"].get("msg"),
        jsonable_encoder(user_info),
        response_status_code=RESPONSE_CONSTANT["validate_link"].get("code"),
    )


def sign_up_wizard_mentor_controller(
    data: MentorSignUpWizardReqModel, photo: UploadFile, background_tasks: BackgroundTasks
):
    try:
        is_link_valid = signup_services.validate_sign_up_link(
            {"verification_link": data.verification_code}
        )
        if is_link_valid is None:
            return custom_exception_handler(
                ERROR_ENUMS["INVALID_VERIFICATION_CODE"]["ErrorCode"],
                ERROR_ENUMS["INVALID_VERIFICATION_CODE"]["ErrorMessage"],
            )
        
        if photo:
            file_name = signup_services.store_photo(photo, data.model_dump())
            data.photo = file_name.get("unique_filename")
            
        user_info = signup_services.insert_mentor_wizard_data(data)

        background_tasks.add_task(
            signup_services.signup_wizard_background_tasks,
            tenant_url_code=user_info.get("tenant_url_code"),
            person_name=user_info.get("name"),
            user_info=user_info,
            user_type="mentor"
        )

        return resp_handler(
            RESPONSE_CONSTANT["sign_up_wizard"].get("msg"),
            jsonable_encoder(user_info),
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


def sign_up_wizard_institute_controller(
    data: InstituteSignUpWizardReqModel, logo: UploadFile, background_tasks: BackgroundTasks
):
    try:
        is_link_valid = signup_services.validate_sign_up_link(
            {"verification_link": data.verification_code}
        )
        if is_link_valid is None:
            return custom_exception_handler(
                ERROR_ENUMS["INVALID_VERIFICATION_CODE"]["ErrorCode"],
                ERROR_ENUMS["INVALID_VERIFICATION_CODE"]["ErrorMessage"],
            )
        
        if logo:
            file_name = signup_services.store_institute_logo(logo, data.model_dump())
            data.logo = file_name.get("unique_filename")
            
        user_info = signup_services.insert_institute_wizard_data(data)

        background_tasks.add_task(
            signup_services.signup_wizard_background_tasks,
            tenant_url_code=user_info.get("tenant_url_code"),
            person_name=user_info.get("name"),
            user_info=user_info,
            user_type="institute",
            password=data.password,

        )

        return resp_handler(
            RESPONSE_CONSTANT["sign_up_wizard_institute"].get("msg"),
            jsonable_encoder(user_info),
            response_status_code=RESPONSE_CONSTANT["sign_up_wizard_institute"].get("code"),
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