from uuid import UUID

from sqlalchemy import select, update

from mdp2mailservice.common.bases.repository import RepositoryBase

from .models import Mail
from .schemas import DeliveryStatus, SendMailRequest


class MailRepositoryBase(RepositoryBase[Mail]):
    model = Mail


class MailRepository(MailRepositoryBase):
    """Repository for performing database queries."""

    async def create_mail(self, mail_id: UUID, mail: SendMailRequest) -> Mail:
        return await super().create({"id": mail_id} | mail.model_dump())

    async def update_status(self, mail_id: UUID, status: DeliveryStatus) -> None:
        await self.session.execute(update(Mail).where(Mail.id == mail_id).values(status=status))
        await self.session.commit()

    async def list_by_filters(self, limit: int, offset: int) -> list[Mail]:
        # TODO: add filters
        query = select(self.model).order_by(Mail.created_at.desc())
        query = query.limit(limit).offset(offset)

        return list(await self.session.scalars(query))
