from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mdp2mailservice.core.db import get_session
from mdp2mailservice.mail.service import MailService


def get_service(session: AsyncSession = Depends(get_session)) -> MailService:
    return MailService(session)
