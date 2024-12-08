from fastapi import APIRouter

from .core.config import settings
from .health import health_check
from .mail import router as mail_router
from .template_engine import router as template_engine_router

router = APIRouter()

router.include_router(health_check.router, tags=["health"])
router.include_router(mail_router.router, prefix=settings.API_PREFIX)
router.include_router(template_engine_router.router, prefix=settings.API_PREFIX)
