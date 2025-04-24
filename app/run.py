from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from fastapi.middleware.gzip import GZipMiddleware
import sentry_sdk
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.adapter.mongodb_adapter import close_super_client
from app.config import get_config
from app.core.error_handler import register_exception_handler
from .routes import router


config = get_config()

if config.IS_SENTRY_ENABLED:
    sentry_sdk.init(
        dsn=config.SENTRY_DSN,
        environment=config.ENV,
        enable_tracing=config.SENTRY_ENABLE_TRACING,  # The parameter enable_tracing needs to be set when initializing the Sentry SDK for performance measurements to be recorded.
        traces_sample_rate=config.SENTRY_TRACES_SAMPLE_RATE,  # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring.
        profiles_sample_rate=config.SENTRY_PROFILES_SAMPLE_RATE,  # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions. We recommend adjusting this value in production.
        integrations=[
            StarletteIntegration(
                transaction_style="endpoint"
            ),  # This option lets you influence how the transactions are named in Sentry
            FastApiIntegration(transaction_style="endpoint"),
        ],
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup event handler
    print("Server starting...")
    yield
    # Shutdown event handler
    print("Server Shutting down...")
    close_super_client()


app = FastAPI(debug=config.DEBUG, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["result_time"],  # Expose the 'result_time' header
)
# Temporary Disabled due to chat stream api issue
# app.add_middleware(
#     GZipMiddleware, minimum_size=500 * 1000
# )  # Compress responses larger than 500kb


app.include_router(router)

register_exception_handler(app)
