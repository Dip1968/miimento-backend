import os
from functools import lru_cache
from typing import Literal
from pydantic import BaseModel, ValidationError
from dotenv import dotenv_values


class Settings(BaseModel):
    ENV: str
    DEBUG: bool
    SUPER_ADMIN_DB_URI: str
    SUPER_ADMIN_DB_NAME: str
    IS_SENTRY_ENABLED: bool
    SENTRY_DSN: str
    SENTRY_ENABLE_TRACING: bool
    SENTRY_TRACES_SAMPLE_RATE: float
    SENTRY_PROFILES_SAMPLE_RATE: float
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    DEFAULT_SENDER_EMAIL: str
    SMTP_PASSWORD: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    UI_HOST_URL: str
    NEW_TENANT_DB_SERVER: Literal["atlas", "native"]
    NEW_TENANT_DB_HOST: str
    NEW_TENANT_DB_EXTRA_PARAMS: str
    NEW_TENANT_ATLAS_PUBLIC_KEY: str
    NEW_TENANT_ATLAS_PRIVATE_KEY: str
    NEW_TENANT_ATLAS_PROJECT_ID: str
    FILE_STORAGE_TYPE: Literal["local", "uploadCare", "S3"]
    OPENAI_API_KEY: str
    SYNO_ADMIN_HOST: str
    BACKEND_URL: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION_NAME: str
    AWS_ATTACHMENT_BUCKET_NAME: str
    PLAN_CACHE_EXPIRY_SECONDS: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    TURNSTILE_SECRET_KEY: str
    AMQP_URL: str
    TASK_QUEUE: str
    TASK_CONSUMER_QUEUE: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_VHOST: str
    TASK_TYPE: str
    CRON_JOB_API_KEY: str


def load_env_file(env: str) -> dict:
    env_file = f".env.{env}"
    print(f"Loading environment file📁 : {env_file}")

    env_values = dotenv_values(env_file)
    try:
        return Settings(**env_values)
    except ValidationError as e:
        raise ValueError(f"Environment configuration is invalid: {e}") from e


def load_configs() -> dict:
    env = os.getenv("ENVIRONMENT", "dev")
    if env not in ["prod", "dev", "qa", "uat"]:
        raise ValueError("Provide a valid environment variable.")

    return load_env_file(env)


@lru_cache()
def get_config() -> Settings:
    return load_configs()
