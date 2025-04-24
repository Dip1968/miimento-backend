import dataclasses


# Constants for Super Admin collections
@dataclasses.dataclass
class SuperAdminCollections:
    USERS = "users"                   # Collection for all users (mentors and institutes)
    ROLES_TEMPLATE = "roles_template" # Template for user roles
    USERS_TEMPLATE = "users_template" # Template for user structure
    TENANT_USERS = "tenant_users"     # Users associated with tenants
    TENANTS_CONFIG = "tenants_config" # Configuration for tenants
    TEST = "test" 



@dataclasses.dataclass
# Constants for Tenant collections
class TenantCollections:
    ROLES = "roles"                   # Roles specific to the tenant
    USERS = "users"                   # Users specific to the tenant
    TEST = "test"                     # Test collection for tenant databases




