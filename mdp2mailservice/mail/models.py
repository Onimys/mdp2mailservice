from sqlalchemy import ARRAY, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from mdp2mailservice.common.bases.models import Base, DateTimeMixin, uuid_
from mdp2mailservice.mail.constants import DeliveryStatus


class Mail(DateTimeMixin, Base):
    __tablename__ = "mails"  # type: ignore

    id: Mapped[uuid_]
    to_recipients: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    cc_recipients: Mapped[list[str] | None] = mapped_column(ARRAY(String))

    subject: Mapped[str | None] = mapped_column(String(255), index=True)
    message: Mapped[str] = mapped_column(Text)

    status: Mapped[DeliveryStatus] = mapped_column(
        default=DeliveryStatus.DRAFT, server_default=text("'DRAFT'"), index=True, nullable=False
    )