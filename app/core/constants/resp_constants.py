from typing import TypedDict


# Define a type for the response structure
class ResponseType(TypedDict):
    code: int
    msg: str


# Define the combined response constants dictionary
RESPONSE_CONSTANT: dict[str, ResponseType] = {
    "sign_up": {
        "code": 200,
        "msg": "Sign up successfully. Please check your email for verification.",
    },
    "sign_up_verification": {
        "code": 200,
        "msg": "Sign up verification successfully.",
    },
    "sign_up_verification_failed": {
        "code": 400,
        "msg": "Sign up verification failed.",
    },
    "sign_up_verification_expired": {
        "code": 400,
        "msg": "Sign up verification link expired.",
    },
    "sign_up_verification_invalid": {
        "code": 400,
        "msg": "Sign up verification link is invalid.",
    },
    "validate_link": {
        "code": 200,
        "msg": "Sign up link is valid.",
    },
    "sign_up_wizard_institute": {
        "code": 200,
        "msg": "Institute sign up wizard completed successfully.",
    },
    "login": {
        "code": 200,
        "msg": "Login successfully.",
    },  
}
    
    