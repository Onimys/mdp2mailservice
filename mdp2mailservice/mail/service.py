import uuid
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from mdp2mailservice.common.utils.files import clean_upload_folder
from mdp2mailservice.core.config import settings
from mdp2mailservice.external_services.email import smtp_send_email

from .constants import DeliveryStatus
from .models import Mail
from .repository import MailRepository
from .schemas import MailSchema


class MailService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self.repository = MailRepository(session)

    async def send_mail(
        self,
        mail_data: MailSchema,
        files: list[UploadFile] | list[Path] | None = None,
        *,
        mail_id: UUID | None = None,
        remove_files: bool = False,
    ) -> Mail:
        mail_id = mail_id or uuid.uuid4()
        try:
            db_mail: Mail = await self.repository.create_mail(mail_id, mail_data)

            await self.__send_mail(db_mail, files)
            await self.repository.update_status(db_mail.id, DeliveryStatus.SENT)
        finally:
            if remove_files:
                await clean_upload_folder(path=f"{settings.ATTACHMENTS_FOLDER}{mail_id}")

        return db_mail

    async def __send_mail(self, mail: Mail, files: list[UploadFile] | list[Path] | None = None) -> None:
        assert mail.message, "Message must not be empty."
        assert mail.to_recipients, "Must provide at least one recipient."

        try:
            await smtp_send_email(
                host=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD.get_secret_value(),
                sender=settings.SMTP_FROM or settings.SMTP_USERNAME,
                to_recipients=", ".join(mail.to_recipients),
                cc_recipients=", ".join(mail.cc_recipients) if mail.cc_recipients else None,
                subject=mail.subject,
                body=mail.message,
                files=files,
                use_tls=settings.SMTP_USE_TLS,
            )
        except Exception:
            await self.repository.update_status(mail.id, DeliveryStatus.FAILED)
            raise
