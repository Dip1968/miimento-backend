# signup_model.py
from datetime import datetime, timezone
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field


class SignUpReqModel(BaseModel):
    name: str
    email: str
    phone_number: str
    user_type: Literal["mentor", "institute"]


class MentorSignUpWizardReqModel(BaseModel):
    profile: Optional[str] = None
    photo: Optional[str] = None
    city: Optional[str] = None
    school_name_10: Optional[str] = None
    school_name_12: Optional[str] = None
    college_name: Optional[str] = None
    degree: Optional[str] = None
    passing_year: Optional[int] = None
    job_position: Optional[str] = None
    company_or_self_employed: Optional[str] = None
    total_experience: Optional[float] = None
    certificates: Optional[str] = None
    achievements: Optional[str] = None
    linkedin_link: Optional[str] = None
    verification_code: str


class InstituteSignUpWizardReqModel(BaseModel):
    verification_code: str
    password: str
    org_name: str
    address: str
    tenant_url_code: str
    logo: Optional[str] = None
    coordinator_name: Optional[str] = None
    coordinator_email: Optional[str] = None
    coordinator_phone: Optional[str] = None


class InsertUserModel(BaseModel):
    name: str
    email: str
    phone_number: str
    user_type: str
    org_name: Optional[str] = None
    address: Optional[str] = None
    coordinator_name: Optional[str] = None
    coordinator_email: Optional[str] = None
    coordinator_phone: Optional[str] = None
    is_email_verified: bool = Field(default=False)
    is_reg_pending: bool = Field(default=True)
    is_tenant_db_generated: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InsertMentorWizardModel(BaseModel):
    profile: Optional[str] = None
    photo: Optional[str] = None
    city: Optional[str] = None
    school_name_10: Optional[str] = None
    school_name_12: Optional[str] = None
    college_name: Optional[str] = None
    degree: Optional[str] = None
    passing_year: Optional[int] = None
    job_position: Optional[str] = None
    company_or_self_employed: Optional[str] = None
    total_experience: Optional[float] = None
    certificates: Optional[str] = None
    achievements: Optional[str] = None
    linkedin_link: Optional[str] = None
    is_email_verified: bool = Field(default=True)
    is_reg_pending: bool = Field(default=False)
    is_tenant_db_generated: bool = Field(default=False)
    is_active: bool = Field(default=True)
    plan_id: int


class InsertInstituteWizardModel(BaseModel):
    org_name: str
    logo: Optional[str] = None
    address: str
    tenant_url_code: str
    coordinator_name: Optional[str] = None
    coordinator_email: Optional[str] = None
    coordinator_phone: Optional[str] = None
    is_email_verified: bool = Field(default=True)
    is_reg_pending: bool = Field(default=False)
    is_tenant_db_generated: bool = Field(default=False)
    is_active: bool = Field(default=True)
