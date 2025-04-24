import bcrypt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.adapter.tenant_adapter import get_tenant_info
from app.utils.jwt_utils import verify_token
from starlette.status import HTTP_403_FORBIDDEN

# Initialize OAuth2PasswordBearer with the token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Dependency to get the current user based on the token


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Verify the token and return the user
        user_email = verify_token(token)
        return user_email  # Or fetch user details from database using the email
    except JWTError as exc:
        raise credentials_exception from exc


def hash_password(password: str) -> str:
    """
    Hash a password for storing.

    Args:
    password (str): The plaintext password to hash.

    Returns:
    str: The hashed password.
    """
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    print(bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    ))
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def validate_tenant_api_key(request: Request, token: str = Depends(oauth2_scheme)):
    tenant_id = request.headers.get("x-tenant")
    if not tenant_id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Tenant not found")
    tenant = get_tenant_info(tenant_id)
    if not tenant:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Tenant not found")
    if tenant.get("api_key") != token:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key.")
    return tenant


def is_password_invalid(password: str) -> bool:
    """
    Checks if a password is invalid based on these rules:
    - Length must be at least 8 characters.
    - Must contain at least one digit.
    - Must contain at least one letter.
    - Must contain at least one special character (!@#$%^&*).

    Returns:
        bool: True if the password is invalid, False if valid.
    """
    if len(password) < 8:
        return True
    if not any(c.isdigit() for c in password):
        return True
    if not any(c.isalpha() for c in password):
        return True
    if not any(c in "!@#$%^&*" for c in password):
        return True
    return False
