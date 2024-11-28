from fastapi import Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from mdp2mailservice.core.db import get_session

from .exceptions import MailNotFound
from .models import Mail
from .service import MailService


def get_service(session: AsyncSession = Depends(get_session)) -> MailService:
    return MailService(session)


async def valid_mail_id(
    mail_id: UUID4,
    service: MailService = Depends(get_service),
) -> Mail:
    mail = await service.get_mail(mail_id)
    if not mail:
        raise MailNotFound()

    return mail
