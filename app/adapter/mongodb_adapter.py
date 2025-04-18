from urllib.parse import quote_plus
from functools import lru_cache
from pydantic import BaseModel
from pymongo import MongoClient

from app.config import get_config

config = get_config()

# Create a single MongoClient instance and reuse it
super_client = MongoClient(config.SUPER_ADMIN_DB_URI, connectTimeoutMS=60000)
super_db = super_client[config.SUPER_ADMIN_DB_NAME]


def get_super_db_conn():
    return super_db


# Cleanup function to close the MongoClient instance on application shutdown
def close_super_client():
    return super_client.close()


class TenantCredentials(BaseModel):
    db_host: str
    db_name: str
    db_username: str
    db_password: str
    extra_params: str

    def __hash__(self):
        return hash(
            (
                self.db_host,
                self.db_name,
                self.db_username,
                self.db_password,
                self.extra_params,
            )
        )


@lru_cache()
def generate_mongodb_uri(cred: TenantCredentials) -> str:
    username = quote_plus(cred.db_username)
    password = quote_plus(cred.db_password)
    host = cred.db_host
    db_name = cred.db_name
    extra_params = cred.extra_params

    # Remove directConnection if it exists in extra_params
    if "directConnection=true" in extra_params:
        return f"mongodb://{username}:{password}@{host}?{extra_params}"

    return f"mongodb+srv://{username}:{password}@{host}/{db_name}?{extra_params}"


# @lru_cache()
def get_tenant_db_conn(db_cred: dict):
    cred = TenantCredentials(**db_cred)
    tenant_uri = generate_mongodb_uri(cred)
    return make_tenant_db_conn(tenant_uri, cred.db_name)


@lru_cache()
def make_tenant_db_conn(tenant_uri, db_name):
    return MongoClient(tenant_uri)[db_name]


# handle from service file where error occurs
# Clear cache if the tenant connection has been expired
# make_tenant_db_conn.cache_clear()
