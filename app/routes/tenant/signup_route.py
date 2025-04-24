# routes.py
from typing import Literal, Optional
from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile
from app.controller.tenant import signup_controller
from app.model.tenant.signup_model import (
    SignUpReqModel, 
    MentorSignUpWizardReqModel, 
    InstituteSignUpWizardReqModel
)

sign_up_router = APIRouter()


@sign_up_router.post("/signup")
def sign_up_route(data: SignUpReqModel, background_tasks: BackgroundTasks):
    return signup_controller.signup_controller(data, background_tasks)


@sign_up_router.post("/signup_wizard_mentor")
def sign_up_wizard_mentor_route(
    background_tasks: BackgroundTasks,
    verification_code: str = Form(...),
    profile: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    city: Optional[str] = Form(None),
    school_name_10: Optional[str] = Form(None),
    school_name_12: Optional[str] = Form(None),
    college_name: Optional[str] = Form(None),
    degree: Optional[str] = Form(None),
    passing_year: Optional[int] = Form(None),
    job_position: Optional[str] = Form(None),
    company_or_self_employed: Optional[str] = Form(None),
    total_experience: Optional[float] = Form(None),
    certificates: Optional[str] = Form(None),
    achievements: Optional[str] = Form(None),
    linkedin_link: Optional[str] = Form(None)
):
    data = MentorSignUpWizardReqModel(
        profile=profile,
        photo=photo.filename if photo else None,
        city=city,
        school_name_10=school_name_10,
        school_name_12=school_name_12,
        college_name=college_name,
        degree=degree,
        passing_year=passing_year,
        job_position=job_position,
        company_or_self_employed=company_or_self_employed,
        total_experience=total_experience,
        certificates=certificates,
        achievements=achievements,
        linkedin_link=linkedin_link,
        verification_code=verification_code
    )
    return signup_controller.sign_up_wizard_mentor_controller(
        data=data, photo=photo, background_tasks=background_tasks
    )


@sign_up_router.post("/signup_wizard_institute")
def sign_up_wizard_institute_route(
    background_tasks: BackgroundTasks,
    password: str = Form(...),
    org_name: str = Form(...),
    verification_code: str = Form(...),
    tenant_url_code: str = Form(...),
    logo: Optional[UploadFile] = File(None),
    address: str = Form(...),
    coordinator_name: Optional[str] = Form(None),
    coordinator_email: Optional[str] = Form(None),
    coordinator_phone: Optional[str] = Form(None)
):
    data = InstituteSignUpWizardReqModel(
        password=password,
        org_name=org_name,
        tenant_url_code=tenant_url_code,
        logo=logo.filename if logo else None,
        address=address,
        coordinator_name=coordinator_name,
        coordinator_email=coordinator_email,
        coordinator_phone=coordinator_phone,
        verification_code=verification_code
    )
    return signup_controller.sign_up_wizard_institute_controller(
        data=data, logo=logo, background_tasks=background_tasks
    )

@sign_up_router.get("/validate_sign_up_link/{verification_code}")
def validate_sign_up_email_verification_link(verification_code: str):
    return signup_controller.validate_sign_up_email_link(verification_code)