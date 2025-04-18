from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from jose import JWTError, jwt
from app.config import get_config
from app.model.tenant.role_model import TokenData

config = get_config()

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict, token_expiry_minutes=ACCESS_TOKEN_EXPIRE_MINUTES):
    """
    Create a JWT token with expiration time.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=token_expiry_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    """
    Verify the JWT token and decode it.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        user_name: str = payload.get("name")
        user_email: str = payload.get("email")
        role_id: str = payload.get("role_id")
        if user_id is None or user_email is None or user_name is None:
            raise credentials_exception
        data = {"id": user_id, "name": user_name,
                "email": user_email, "role_id": role_id}
        token_data = TokenData(**data)
        return token_data
    except JWTError as exc:
        raise credentials_exception from exc
