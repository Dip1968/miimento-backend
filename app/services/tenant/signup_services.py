from datetime import datetime, timezone
import uuid
from pymongo import ReturnDocument
from app.core.constants.db_collections import SuperAdminCollections, TenantCollections
from app.adapter.mongodb_adapter import super_db, super_client
from app.core.constants.email_templates import SIGN_UP_EMAIL_VERIFICATION_TEMPLATE, SIGN_UP_SUCCESS_EMAIL_TEMPLATE
from app.core.error_handler import handle_internal_error
from app.model.tenant.signup_model import InsertMentorModel, InsertSignUpWizardModel, SignUpWizardReqModel
from app.utils.auth_utils import hash_password
from app.utils.email_utils import email_util
from app.utils.file_utils import upload_file_util
from app.utils.string_utils import generate_random_string
from app.config import get_config
from pymongo.database import Database
import httpx

config= get_config()

def verify_email(email):
    collection = super_db[SuperAdminCollections.MENTORS]
    items = collection.find_one({"email": email})
    return items

def insert_mentor_data(data) -> bool:
    collection = super_db[SuperAdminCollections.MENTORS]
    data_object = InsertMentorModel(**data.model_dump())
    items = collection.insert_one(data_object.model_dump())
    return items

def generate_verification_link(insertedData, data) -> tuple:
    random_string = generate_random_string(20)
    collection = super_db[SuperAdminCollections.MENTORS]
    tenant_data = collection.find_one_and_update(
        {"_id": insertedData.inserted_id},
        {
            "$set": {
                "verification_link": random_string,
                "verification_link_sent_at": datetime.now(timezone.utc),
            }
        },
        projection={"email": True, "_id": False},
        return_document=ReturnDocument.AFTER,
    )
    make_url = f"{config.UI_HOST_URL}/auth/signup_wizard/{random_string}"
    if data.planId:
        make_url += f"?plan_id={data.planId}"

    return make_url, tenant_data

def send_signup_verification_email(insertedData, data):
    verification_url, tenant_data = generate_verification_link(insertedData, data)
    email_util.send_email(
        to_address=tenant_data.get("email"),
        subject=SIGN_UP_EMAIL_VERIFICATION_TEMPLATE.subject,
        body=SIGN_UP_EMAIL_VERIFICATION_TEMPLATE.get_body_with_variables(
            verify_link=verification_url
        ),
        is_html=SIGN_UP_EMAIL_VERIFICATION_TEMPLATE.is_html,
    )

    return True

def validate_tenant_sign_up_link(data):
    collection = super_db[SuperAdminCollections.MENTORS]
    tenant_data = collection.find_one_and_update(
        data,
        {"$set": {"is_email_verified": True}},
        projection={"_id": False},
        return_document=ReturnDocument.AFTER,
    )
    return tenant_data

def check_duplicate_tenant_data(tenant_url_code):
    collection = super_db[SuperAdminCollections.MENTORS]
    tenant_data = collection.find_one({"tenant_url_code": tenant_url_code}, {"_id": 1})
    return tenant_data

def store_company_logo(file, data):
    resp = upload_file_util(file, tenant=data)
    return resp

def insert_signup_wizard_data(data: SignUpWizardReqModel):
    collection = super_db[SuperAdminCollections.MENTORS]
    data_object = InsertSignUpWizardModel(**data.model_dump())
    tenant_info = collection.find_one_and_update(
        {"verification_link": data.verification_code},
        {
            "$set": data_object.model_dump(),
            "$unset": {"verification_link": 1, "verification_link_sent_at": 1},
        },
        projection={
            "_id": False,
            "id": {"$toString": "$_id"},
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
    return tenant_info

def signup_wizard_background_tasks(
    tenant_url_code: str, person_name: str, tenant_info: dict, password: str
):
    generate_tenant_database(
        tenant_url_code=tenant_url_code,
        person_name=person_name,
        tenant_info=tenant_info,
        password=password,
    )
    
def generate_tenant_database(
    tenant_url_code: str,
    person_name: str,
    tenant_info: dict,
    password: str,
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
            admin_db = client[
                "admin"
            ]  # Connect to the 'admin' database for user management
            # Authenticate to the admin database (if authentication is enabled)
            # If your MongoDB instance requires authentication to manage users,
            # you'll need to authenticate here using a user with the appropriate privileges (e.g., userAdminAnyDatabase role).
            # admin_db.authenticate('admin_user', 'admin_password')

            # Check if the user already exists
            user_exists = admin_db.system.users.find_one(
                {"user": db_cred["db_username"], "db": db_cred["db_name"]}
            )
            if user_exists:
                print(
                    f"User '{db_cred["db_username"]}' already exists in database '{db_cred["db_name"]}'."
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
                f"User '{db_cred["db_username"]}' created successfully in database '{db_cred["db_name"]}'."
            )
        store_tenant_config(
            db_cred,
            tenant_info,
            tenant_creation_response,
        )
        seed_tenant_data(db, tenant_info, password)
        send_signup_success_email(tenant_info)

        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
    
def create_atlas_user(username, password, db_name):
    url = f"https://cloud.mongodb.com/api/atlas/v1.0/groups/{
        config.NEW_TENANT_ATLAS_PROJECT_ID}/databaseUsers"

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


def seed_tenant_data(tenant_db: Database, tenant_info: dict, password):

    # seed chat completions
    source_chat_completions_collection = super_db[
        SuperAdminCollections.CHAT_COMPLETIONS_TEMPLATE
    ]
    dest_chat_completions_collection = tenant_db[TenantCollections.CHAT_COMPLETIONS]

    chat_completions = list(source_chat_completions_collection.find())

    dest_chat_completions_collection.insert_many(chat_completions)

    # seed roles
    source_roles_collection = super_db[SuperAdminCollections.ROLES_TEMPLATE]
    dest_roles_collection = tenant_db[TenantCollections.ROLES]
    # Fetch all roles from the source collection (both Admin and Guest)
    roles = list(source_roles_collection.find())  # Fetch all roles

    # Insert all roles into the tenant's roles collection
    dest_roles_collection.insert_many(roles)

    # admin_role = next(role for role in roles if role["role_name"] == "Admin")
    # Find the first role that is not a guest role
    admin_role = next(
        (role for role in roles if not role.get("is_guest_role", False)), None
    )

    # seed tenant user
    source_user_collection = super_db[SuperAdminCollections.USERS_TEMPLATE]
    dest_user_collection = tenant_db[TenantCollections.USERS]
    user_template = source_user_collection.find_one({}, {"_id": 0})
    new_user = {
        "first_name": tenant_info.get("first_name"),
        "last_name": tenant_info.get("last_name"),
        "email": tenant_info.get("email"),
        "password": hash_password(password),
        "role_id": str(admin_role["_id"]),
        "role_name": admin_role["role_name"],
        "is_email_verified": True,
        "is_admin": True,
    }
    user = {**user_template, **new_user}
    dest_user_collection.insert_one(user)

    # register user in super admin collection
    source_tenant_user_collection = super_db[SuperAdminCollections.TENANT_USERS]
    tenant_user = {
        "email": tenant_info.get("email"),
        "is_active": True,
        "tenant_id": tenant_info.get("id"),
        "tenant_url_code": tenant_info.get("tenant_url_code"),
    }
    source_tenant_user_collection.insert_one(tenant_user)

    # Update DB generated status
    clients_collection = super_db[SuperAdminCollections.CLIENTS]
    clients_collection.update_one(
        {"tenant_url_code": tenant_info.get("tenant_url_code")},
        {
            "$set": {"is_tenant_db_generated": True},
            "$unset": {"is_reg_pending": 1, "is_email_verified": 1},
        },
    )


def store_tenant_config(
    db_cred, tenant_info, secret_key, openai_project_id, tenant_creation_response
):
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

    if tenant_info.get("ai_service") == AiService.OpenAI:
        config_data = {
            "tenant_id": tenant_info.get("id"),
            "ai_service": tenant_info.get("ai_service"),
            "tenant_url_code": tenant_info.get("tenant_url_code"),
            "api_key": str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc),
            "db_cred": db_cred,
            "ai_service_config": {
                "openai_key": secret_key,
                "openai_project_id": openai_project_id,
            },
            "is_tenant_owned_config": False,
            "plan": plan,
        }
        tenant_config_collection.insert_one(config_data)

    else:
        pass
    
def send_signup_success_email(tenant_data):
    email_util.send_email(
        to_address=tenant_data.get("email"),
        subject=SIGN_UP_SUCCESS_EMAIL_TEMPLATE.subject,
        body=SIGN_UP_SUCCESS_EMAIL_TEMPLATE.get_body_with_variables(
            person_name=tenant_data.get("first_name"),
        ),
        is_html=SIGN_UP_SUCCESS_EMAIL_TEMPLATE.is_html,
    )
    return True