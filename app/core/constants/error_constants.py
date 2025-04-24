

from fastapi import status
from pydantic import BaseModel


class ErrorStatusCodesModel(BaseModel):
    UNCAUGHT_ERROR: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    VALIDATION_ERROR: int = status.HTTP_422_UNPROCESSABLE_ENTITY
    CUSTOM_ERROR: int = status.HTTP_412_PRECONDITION_FAILED


ErrorStatusCodes = ErrorStatusCodesModel().model_dump()

ERROR_ENUMS = {
    "SECURITY_CHECK_FAILED": {
        "ErrorCode": 1001,
        "ErrorMessage": "Security check failed",
    },
    "EMAIL_ALREADY_EXIST": {
        "ErrorCode": 1002,
        "ErrorMessage": "Email already exists",
    },
    "COMMON": {
        "ErrorCode": 1003,
        "ErrorMessage": "An error occurred",
    },
    "LOGIN": {  
        "ErrorCode": 1004,
        "ErrorMessage": "Login failed",
    },
}