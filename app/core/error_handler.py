from fastapi import HTTPException, Request, FastAPI
from fastapi.responses import JSONResponse

from app.core.constants.error_constants import ErrorStatusCodes
from fastapi.exceptions import RequestValidationError


class ExceptionHandler(HTTPException):
    def __init__(self, status_code: int, detail: dict):
        super().__init__(status_code=status_code, detail=detail)


def register_exception_handler(app: FastAPI):
    app.add_exception_handler(ExceptionHandler, exception_handler)
    app.add_exception_handler(RequestValidationError,
                              validation_exception_handler)

# exceptions.py


# Custom handler for validation errors
def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Customize the response format
    return JSONResponse(
        status_code=ErrorStatusCodes.get("CUSTOM_ERROR"),
        content={
            "success": False,
            "ErrorMessage": "Validation error",
            "ErrorCode": ErrorStatusCodes.get("CUSTOM_ERROR"),
            "ExceptionLog": exc.errors(),
        },
    )


def exception_handler(_: Request, exc: ExceptionHandler):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "ErrorMessage": exc.detail.get("ErrorMessage"),
            "ErrorCode": exc.detail.get("ErrorCode"),
            "ExceptionLog": exc.detail.get("ExceptionLog", None),
        },
    )


def custom_exception_handler(error_code: int, error_message: str, exception_log=None):
    return JSONResponse(
        status_code=ErrorStatusCodes.get("CUSTOM_ERROR"),
        content={
            "success": False,
            "ErrorCode": error_code,
            "ErrorMessage": error_message,
            "ExceptionLog": exception_log,
        },
    )


def handle_internal_error(error_message):
    return {
        "status": "error",
        "message": "An internal error occurred.",
        "details": error_message,
    }
