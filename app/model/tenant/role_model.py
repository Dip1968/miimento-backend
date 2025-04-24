from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils import db_utils


class Permissions(BaseModel):
    create: bool = False
    view: bool = False
    update: bool = False
    delete: bool = False


DEFAULT_PERMISSIONS = Permissions()


class RolePermissionsConst(BaseModel):
    roles: Permissions = DEFAULT_PERMISSIONS
    permissions: Permissions = DEFAULT_PERMISSIONS
    users: Permissions = DEFAULT_PERMISSIONS
    assistants: Permissions = DEFAULT_PERMISSIONS
    files: Permissions = DEFAULT_PERMISSIONS
    chatcompletions: Permissions = DEFAULT_PERMISSIONS
    plan: Permissions = DEFAULT_PERMISSIONS
    setting: Permissions = DEFAULT_PERMISSIONS


class RolePermissions(BaseModel):
    roles: Permissions
    permissions: Permissions
    users: Permissions
    assistants: Permissions
    files: Permissions
    chatcompletions: Permissions
    plan: Permissions = None
    setting: Permissions = None


class TokenData(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[str] = None


class Role(BaseModel):
    id: Optional[db_utils.PyObjectId] = Field(None, alias="_id")
    role_name: str
    permission: Optional[RolePermissions] = RolePermissionsConst()
    is_active: bool = True
    created_by_id: Optional[str] = None
    created_by_name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by_id: Optional[str] = None
    updated_by_name: Optional[str] = None
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "role_name": "role 1",
                "permission": {
                    "roles": {
                        "create": False,
                        "view": False,
                        "update": False,
                        "delete": False,
                    },
                    "permissions": {
                        "create": False,
                        "view": False,
                        "update": False,
                        "delete": False,
                    },
                    "users": {
                        "create": False,
                        "view": False,
                        "update": False,
                        "delete": False,
                    },
                    "assistants": {
                        "create": False,
                        "view": False,
                        "update": False,
                        "delete": False,
                    },
                    "files": {
                        "create": False,
                        "view": False,
                        "update": False,
                        "delete": False,
                    },
                    "chatcompletions": {
                        "create": True,
                        "view": True,
                        "update": True,
                        "delete": True,
                    },
                    "plan": {
                        "create": False,
                        "view": False,
                        "update": False,
                        "delete": False,
                    },
                    "setting": {
                        "create": False,
                        "view": False,
                        "update": False,
                        "delete": False,
                    },
                },
                "is_active": True,
                "created_by_id": "user_id",
                "created_by_name": "varchar",
                "created_at": "2023-06-25T00:00:00Z",
                "updated_by_id": "user_id",
                "updated_by_name": "varchar",
                "updated_at": "2023-06-25T00:00:00Z",
            }
        }


class UpdateRole(BaseModel):
    id: Optional[db_utils.PyObjectId] = Field(None, alias="_id")
    role_name: str
    is_active: bool = True
    updated_by_id: Optional[str] = None
    updated_by_name: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UpdatePermissionsRequest(BaseModel):
    permission: RolePermissions
    updated_by_id: Optional[str] = None
    updated_by_name: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UpdateRoleRequest(BaseModel):
    role_name: str


class RoleList(BaseModel):
    id: Optional[db_utils.PyObjectId] = Field(None, alias="_id")
    role_name: str
    is_active: bool = True
    is_guest_role: bool = False
    created_by_id: Optional[str] = None
    created_by_name: Optional[str] = None
    created_at: datetime
    updated_by_id: Optional[str] = None
    updated_by_name: Optional[str] = None
    updated_at: Optional[datetime] = None
