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
}
    
    