import re
import uuid
from pathlib import Path
from typing import Final, TypeAlias
from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from mdp2mailservice.common.utils.files import clean_upload_folder
from mdp2mailservice.core.config import settings
from mdp2mailservice.external_services.email import smtp_send_email
from mdp2mailservice.template_engine.engine import TemplateEngine
from mdp2mailservice.template_engine.schemas import Template

from .models import Mail
from .repository import MailRepository
from .schemas import DeliveryStatus, SendMailRequest

SMTPMailId: TypeAlias = str
SMTP_REGEX_IDENTIFIER: Final[str] = r"id=([^\s]+)"


class MailService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._template_engine = TemplateEngine()
        self.repository = MailRepository(session)

    async def send_mail(
        self,
        mail_data: SendMailRequest,
        files: list[UploadFile] | list[Path] | None = None,
        *,
        mail_id: UUID | None = None,
        remove_files: bool = False,
    ) -> Mail:
        mail_id = mail_id or uuid.uuid4()

        template = None
        template_data = None
        if isinstance(mail_data.message, Template):
            template = mail_data.message.template
            template_data = mail_data.message.context
            mail_data.message = self._template_engine(mail_data.message).format()

        try:
            db_mail: Mail = await self.repository.create_mail(
                mail_id, mail_data, template, template_data, attachments=[str(f) for f in files or []]
            )

            smtp_mail_id = await self.__send_mail(db_mail, files)
            if smtp_mail_id:
                await self.repository.set_smpt_id(db_mail.id, smtp_mail_id)

            await self.repository.update_status(db_mail.id, DeliveryStatus.SENT)
        finally:
            if remove_files:
                await clean_upload_folder(path=f"{settings.ATTACHMENTS_FOLDER}{mail_id}")

        return db_mail

    async def __send_mail(self, mail: Mail, files: list[UploadFile] | list[Path] | None = None) -> SMTPMailId | None:
        assert mail.message, "Message must not be empty."
        assert mail.to_recipients, "Must provide at least one recipient."

        try:
            _, response = await smtp_send_email(
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
            if smtP_mail_id := re.findall(SMTP_REGEX_IDENTIFIER, response):
                return smtP_mail_id[0]
        except Exception:
            await self.repository.update_status(mail.id, DeliveryStatus.FAILED)
            raise

    async def get_mail(self, mail_id: UUID) -> Mail | None:
        return await self.repository.get(mail_id)

    async def get_mails(self, limit: int, offset: int) -> list[Mail] | None:
        return await self.repository.list_by_filters(limit=limit, offset=offset)

    async def delete_mail(self, mail_id: UUID) -> None:
        return await self.repository.delete(Mail.id == mail_id)
