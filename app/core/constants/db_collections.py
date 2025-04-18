import dataclasses


# Constants for Super Admin collections
@dataclasses.dataclass
class SuperAdminCollections:
    MENTORS = "mentors"
    TENANTS_CONFIG = "mentors_config"
    ROLES_TEMPLATE = "roles_template"
    USERS_TEMPLATE = "users_template"
    TENANT_USERS = "tenant_users"



@dataclasses.dataclass
# Constants for Tenant collections
class TenantCollections:
    USERS = "users"
    TEST = "test"
    ROLES = "roles"




