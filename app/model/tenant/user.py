from pydantic import BaseModel, EmailStr


class UserEmail(BaseModel):
    email: str


class UserLogin(BaseModel):
    email: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    new_password: str
    confirm_password: str
