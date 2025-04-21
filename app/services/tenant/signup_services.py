# services.py
from datetime import datetime, timezone
import uuid
from pymongo import ReturnDocument
from app.core.constants.db_collections import SuperAdminCollections, TenantCollections
from app.adapter.mongodb_adapter import super_db, super_client
from app.core.constants.email_templates import SIGN_UP_EMAIL_VERIFICATION_TEMPLATE, SIGN_UP_SUCCESS_EMAIL_TEMPLATE
from app.core.error_handler import handle_internal_error
from app.model.tenant.signup_model import (
    InsertUserModel, 
    InsertMentorWizardModel,
    InsertInstituteWizardModel,
    InstituteSignUpWizardReqModel,
    MentorSignUpWizardReqModel
)
from app.utils.auth_utils import hash_password
from app.utils.email_utils import email_util
from app.utils.file_utils import upload_file_util
from app.utils.string_utils import generate_random_string
from app.config import get_config
from fastapi import UploadFile
from pymongo.database import Database
import httpx

config = get_config()


def verify_email(email):
    collection = super_db[SuperAdminCollections.USERS]
    items = collection.find_one({"email": email})
    return items


def insert_user_data(data) -> bool:
    collection = super_db[SuperAdminCollections.USERS]
    data_object = InsertUserModel(**data.model_dump())
    items = collection.insert_one(data_object.model_dump())
    return items


def generate_verification_link(insertedData, data) -> tuple:
    random_string = generate_random_string(20)
    collection = super_db[SuperAdminCollections.USERS]
    user_data = collection.find_one_and_update(
        {"_id": insertedData.inserted_id},
        {
            "$set": {
                "verification_link": random_string,
                "verification_link_sent_at": datetime.now(timezone.utc),
            }
        },
        projection={"email": True, "user_type": True, "_id": False},
        return_document=ReturnDocument.AFTER,
    )
    
    # Determine the wizard page based on user type
    wizard_page = f"signup_wizard_{user_data.get('user_type')}"
    make_url = f"{config.UI_HOST_URL}/auth/{wizard_page}/{random_string}"
    
    if hasattr(data, 'planId') and data.planId:
        make_url += f"?plan_id={data.planId}"

    return make_url, user_data


def send_signup_verification_email(insertedData, data):
    verification_url, user_data = generate_verification_link(insertedData, data)
    email_util.send_email(
        to_address=user_data.get("email"),
        subject=SIGN_UP_EMAIL_VERIFICATION_TEMPLATE.subject,
        body=SIGN_UP_EMAIL_VERIFICATION_TEMPLATE.get_body_with_variables(
            verify_link=verification_url
        ),
        is_html=SIGN_UP_EMAIL_VERIFICATION_TEMPLATE.is_html,
    )

    return True


def validate_sign_up_link(data):
    collection = super_db[SuperAdminCollections.USERS]
    user_data = collection.find_one_and_update(
        data,
        {"$set": {"is_email_verified": True}},
        projection={"_id": False, "user_type": True},
        return_document=ReturnDocument.AFTER,
    )
    return user_data


def check_duplicate_tenant_data(tenant_url_code):
    collection = super_db[SuperAdminCollections.USERS]
    tenant_data = collection.find_one({"tenant_url_code": tenant_url_code}, {"_id": 1})
    return tenant_data


def store_photo(file: UploadFile, data):
    resp = upload_file_util(file, tenant=data, file_type="photo")
    return resp


def store_institute_logo(file: UploadFile, data):
    resp = upload_file_util(file, tenant=data, file_type="logo")
    return resp


def insert_mentor_wizard_data(data: MentorSignUpWizardReqModel):
    collection = super_db[SuperAdminCollections.USERS]
    data_object = InsertMentorWizardModel(**data.model_dump())
    user_info = collection.find_one_and_update(
        {"verification_link": data.verification_code, "user_type": "mentor"},
        {
            "$set": data_object.model_dump(),
            "$unset": {"verification_link": 1, "verification_link_sent_at": 1},
        },
        projection={
            "_id": False,
            "id": {"$toString": "$_id"},
            "name": 1,
            "email": 1,
            "phone_number": 1,
            "user_type": 1,
            "profile": 1,
            "photo": 1,
            "city": 1,
            "school_name_10": 1,
            "school_name_12": 1,
            "college_name": 1,
            "degree": 1,
            "passing_year": 1,
            "job_position": 1,
            "company_or_self_employed": 1,
            "total_experience": 1,
            "certificates": 1,
            "achievements": 1,
            "linkedin_link": 1,
            "is_email_verified": 1,
            "is_reg_pending": 1,
            "is_tenant_db_generated": 1,
            "is_active": 1,
            "plan_id": 1,
        },
        return_document=ReturnDocument.AFTER,
    )
    return user_info


def insert_institute_wizard_data(data: InstituteSignUpWizardReqModel):
    collection = super_db[SuperAdminCollections.USERS]
    data_object = InsertInstituteWizardModel(**data.model_dump())
    user_info = collection.find_one_and_update(
        {"verification_link": data.verification_code, "user_type": "institute"},
        {
            "$set": data_object.model_dump(),
            "$unset": {"verification_link": 1, "verification_link_sent_at": 1},
        },
        projection={
            "_id": False,
            "id": {"$toString": "$_id"},
            "name": 1,
            "email": 1,
            "phone_number": 1,
            "user_type": 1,
            "org_name": 1,
            "logo": 1,
            "address": 1,
            "coordinator_name": 1,
            "coordinator_email": 1,
            "coordinator_phone": 1,
            "is_email_verified": 1,
            "is_reg_pending": 1,
            "is_tenant_db_generated": 1,
            "is_active": 1,
            "plan_id": 1,
        },
        return_document=ReturnDocument.AFTER,
    )
    return user_info


def signup_wizard_background_tasks(
    tenant_url_code: str, person_name: str, user_info: dict, user_type: str
):
    tenant_creation_response = {}  # This would be populated based on subscription logic
    generate_tenant_database(
        tenant_url_code=tenant_url_code,
        person_name=person_name,
        user_info=user_info,
        user_type=user_type,
        tenant_creation_response=tenant_creation_response,
    )
    

def generate_tenant_database(
    tenant_url_code: str,
    person_name: str,
    user_info: dict,
    user_type: str,
    tenant_creation_response,
):
    try:
        db_cred = {
            "db_host": config.NEW_TENANT_DB_HOST,
            "db_name": tenant_url_code,
            "db_username": f"{person_name}-{generate_random_string(5)}",
            "db_password": generate_random_string(12),
            "extra_params": config.NEW_TENANT_DB_EXTRA_PARAMS,
        }
        db = super_client[db_cred["db_name"]]
        db.create_collection(TenantCollections.TEST)
        db[TenantCollections.TEST].insert_one(
            {"test": f"hey {tenant_url_code}, we are good!"}
        )

        if config.NEW_TENANT_DB_SERVER == "atlas":
            create_atlas_user(
                db_cred["db_username"], db_cred["db_password"], db_cred["db_name"]
            )
        elif config.NEW_TENANT_DB_SERVER == "native":
            client = super_db.client
            admin_db = client["admin"]  # Connect to the 'admin' database for user management
            
            # Check if the user already exists
            user_exists = admin_db.system.users.find_one(
                {"user": db_cred["db_username"], "db": db_cred["db_name"]}
            )
            if user_exists:
                print(
                    f"User '{db_cred['db_username']}' already exists in database '{db_cred['db_name']}'."
                )
                return

            # Create the user
            admin_db.command(
                "createUser",
                db_cred["db_username"],
                pwd=db_cred["db_password"],
                roles=[{"role": "readWrite", "db": db_cred["db_name"]}],
            )
            print(
                f"User '{db_cred['db_username']}' created successfully in database '{db_cred['db_name']}'."
            )
        
        # Store tenant configuration with tenant type information
        store_tenant_config(
            db_cred,
            user_info,
            tenant_creation_response,
            user_type,
        )
        
        # Seed database with appropriate data based on user type
        seed_tenant_data(db, user_info, user_type)
        
        # Send success email
        send_signup_success_email(user_info)

        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
    
def create_atlas_user(username, password, db_name):
    url = f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{config.NEW_TENANT_ATLAS_PROJECT_ID}/databaseUsers"

    payload = {
        "databaseName": "admin",
        "roles": [{"roleName": "readWrite", "databaseName": db_name}],
        "username": username,
        "password": password,
    }

    auth = httpx.DigestAuth(
        config.NEW_TENANT_ATLAS_PUBLIC_KEY, config.NEW_TENANT_ATLAS_PRIVATE_KEY
    )
    response = httpx.post(
        url,
        json=payload,
        auth=auth,
    )

    if response.status_code != 201:
        return handle_internal_error(
            f"Failed to create Atlas user. Status code: {response.status_code}, Response: {response.text}"
        )

    return True


def seed_tenant_data(tenant_db: Database, user_info: dict, user_type: str):
    # Seed roles based on user type
    source_roles_collection = super_db[SuperAdminCollections.ROLES_TEMPLATE]
    dest_roles_collection = tenant_db[TenantCollections.ROLES]
    
    # Fetch appropriate roles based on user type
    roles_filter = {}
    if user_type == "mentor":
        roles_filter = {"is_mentor_role": True}
    elif user_type == "institute":
        roles_filter = {"is_institute_role": True}
    
    roles = list(source_roles_collection.find(roles_filter))
    
    # Insert roles into tenant's roles collection
    if roles:
        dest_roles_collection.insert_many(roles)
    
    # Find appropriate admin role
    admin_role = next(
        (role for role in roles if not role.get("is_guest_role", False)), None
    )
    
    # Seed tenant user
    source_user_collection = super_db[SuperAdminCollections.USERS_TEMPLATE]
    dest_user_collection = tenant_db[TenantCollections.USERS]
    user_template = source_user_collection.find_one({}, {"_id": 0})
    
    # Create new user based on user type
    if user_type == "mentor":
        new_user = {
            "name": user_info.get("name"),
            "email": user_info.get("email"),
            "phone_number": user_info.get("phone_number"),
            "profile": user_info.get("profile"),
            "photo": user_info.get("photo"),
            "city": user_info.get("city"),
            "school_name_10": user_info.get("school_name_10"),
            "school_name_12": user_info.get("school_name_12"),
            "college_name": user_info.get("college_name"),
            "degree": user_info.get("degree"),
            "passing_year": user_info.get("passing_year"),
            "job_position": user_info.get("job_position"),
            "company_or_self_employed": user_info.get("company_or_self_employed"),
            "total_experience": user_info.get("total_experience"),
            "certificates": user_info.get("certificates"),
            "achievements": user_info.get("achievements"),
            "linkedin_link": user_info.get("linkedin_link"),
            "password": hash_password(generate_random_string(12)),  # Generate a random password that will be reset
            "role_id": str(admin_role["_id"]) if admin_role else None,
            "role_name": admin_role["role_name"] if admin_role else "Mentor",
            "user_type": "mentor",
            "is_email_verified": True,
            "is_admin": True,
        }
    else:  # institute
        new_user = {
            "name": user_info.get("name"),
            "email": user_info.get("email"),
            "phone_number": user_info.get("phone_number"),
            "org_name": user_info.get("org_name"),
            "logo": user_info.get("logo"),
            "address": user_info.get("address"),
            "coordinator_name": user_info.get("coordinator_name"),
            "coordinator_email": user_info.get("coordinator_email"),
            "coordinator_phone": user_info.get("coordinator_phone"),
            "password": hash_password(generate_random_string(12)),  # Generate a random password that will be reset
            "role_id": str(admin_role["_id"]) if admin_role else None,
            "role_name": admin_role["role_name"] if admin_role else "Institute Admin",
            "user_type": "institute",
            "is_email_verified": True,
            "is_admin": True,
        }
    
    user = {**user_template, **new_user}
    dest_user_collection.insert_one(user)

    # Register user in super admin collection
    source_tenant_user_collection = super_db[SuperAdminCollections.TENANT_USERS]
    tenant_user = {
        "email": user_info.get("email"),
        "is_active": True,
        "tenant_id": user_info.get("id"),
        "tenant_url_code": user_info.get("tenant_url_code"),
        "user_type": user_type,
    }
    source_tenant_user_collection.insert_one(tenant_user)

    # Update DB generated status
    users_collection = super_db[SuperAdminCollections.USERS]
    users_collection.update_one(
        {"_id": user_info.get("id")},
        {
            "$set": {"is_tenant_db_generated": True},
            "$unset": {"is_reg_pending": 1, "is_email_verified": 1},
        },
    )


def store_tenant_config(db_cred, user_info, tenant_creation_response, user_type):
    tenant_config_collection = super_db[SuperAdminCollections.TENANTS_CONFIG]
    
    # Extract plan attributes from tenant creation response
    subscribed_plan = (
        tenant_creation_response.get("data", {})
        .get("plan", {})
        .get("subscribedPlan", {})
    )
    
    # Create plan object structure
    plan = {
        "plan_name": subscribed_plan.get("plan_name", ""),
        "plan_start_date": subscribed_plan.get("start_date", ""),
        "plan_end_date": subscribed_plan.get("end_date", ""),
        "plan_attributes": subscribed_plan.get("plan_attributes", []),
    }

    # Base configuration
    config_data = {
        "tenant_id": user_info.get("id"),
        "tenant_url_code": user_info.get("tenant_url_code"),
        "user_type": user_type,
        "api_key": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc),
        "db_cred": db_cred,
        "is_tenant_owned_config": False,
        "plan": plan,
    }
    
    tenant_config_collection.insert_one(config_data)


def send_signup_success_email(user_data):
    email_util.send_email(
        to_address=user_data.get("email"),
        subject=SIGN_UP_SUCCESS_EMAIL_TEMPLATE.subject,
        body=SIGN_UP_SUCCESS_EMAIL_TEMPLATE.get_body_with_variables(
            person_name=user_data.get("name"),
            user_type=user_data.get("user_type"),
        ),
        is_html=SIGN_UP_SUCCESS_EMAIL_TEMPLATE.is_html,
    )
    return True