from uuid import UUID

from sqlalchemy import update

from mdp2mailservice.common.bases.repository import RepositoryBase
from mdp2mailservice.mail.schemas import MailSchema

from .constants import DeliveryStatus
from .models import Mail


class MailRepositoryBase(RepositoryBase[Mail]):
    model = Mail


class MailRepository(MailRepositoryBase):
    """Repository for performing database queries."""

    async def create_mail(self, mail_id: UUID, mail: MailSchema) -> Mail:
        return await super().create({"id": mail_id} | mail.model_dump())

    async def update_status(self, mail_id: UUID, status: DeliveryStatus) -> None:
        await self.session.execute(update(Mail).where(Mail.id == mail_id).values(status=status))
        await self.session.commit()
