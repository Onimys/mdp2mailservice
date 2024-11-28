from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mdp2mailservice.routes import router as api_rputer

from .config import settings
from .exceptions import register_exceptions
from .middlewares import RateLimitingMiddleware
from .openapi import custom_openapi


def get_application() -> FastAPI:
    """Configure, start and return the application"""

    app = FastAPI(
        title=settings.APP_NAME,
        root_path=settings.ROOT_PATH,
        version=settings.APP_VERSION,
        description="Service to send mails",
        docs_url="/swagger",
        redoc_url="/",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.include_router(api_rputer)

    if settings.MAIL_QUEUE_CONSUMER_ENABLED:
        register_consumers(app)

    if settings.ADMIN_ENABLED:
        register_admin(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_origin_regex=settings.ALLOWED_HOSTS_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.RATE_LIMIT_ENABLED:
        app.add_middleware(RateLimitingMiddleware)  # type: ignore

    register_exceptions(app)

    app.openapi = custom_openapi(app)

    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def register_consumers(app: FastAPI):
    from mdp2mailservice.consumers import mail

    app.include_router(mail.router)


def register_admin(app: FastAPI):
    from mdp2mailservice.admin.admin_panel import create_admin_panel

    from .db import engine

    create_admin_panel(app, engine)
