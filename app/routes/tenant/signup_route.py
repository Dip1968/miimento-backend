from typing import Literal, Optional
from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile
from app.controller.tenant import signup_controller
from app.model.tenant.signup_model import SignUpReqModel, SignUpWizardReqModel

sign_up_router = APIRouter()


@sign_up_router.post("signup/mentor")
def sign_up_route(data: SignUpReqModel, background_tasks: BackgroundTasks):
    return signup_controller.signup_mentor_controller(data, background_tasks)

@sign_up_router.post("/sign_up_wizard/mentor")
def sign_up_wizard_route(
    background_tasks: BackgroundTasks,
    profile: Optional[str] = Form(None),
    photo: Optional[str] = Form(None),
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
    data = SignUpWizardReqModel(
        profile=profile,
        photo=photo,
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
        linkedin_link=linkedin_link
    )
    return signup_controller.sign_up_wizard_mentor_controller(
        data=data, background_tasks=background_tasks
    )