from sqlalchemy import ARRAY, JSON, String, Text, text
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column

from mdp2mailservice.common.bases.models import Base, DateTimeMixin, uuid_
from mdp2mailservice.mail.schemas import DeliveryStatus


class Mail(DateTimeMixin, Base):
    __tablename__ = "mails"  # type: ignore

    id: Mapped[uuid_]
    smtp_mail_id: Mapped[str | None] = mapped_column(index=True)
    to_recipients: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    cc_recipients: Mapped[list[str] | None] = mapped_column(ARRAY(String))

    subject: Mapped[str | None] = mapped_column(String(255), index=True)
    message: Mapped[str] = mapped_column(Text)
    template: Mapped[str | None] = mapped_column(String(255))
    template_data: Mapped[JSON | None] = mapped_column(type_=JSON)

    attachments: Mapped[list[str] | None] = mapped_column(ARRAY(String))

    status: Mapped[DeliveryStatus] = mapped_column(
        PgEnum(DeliveryStatus, name="deliverystatus", create_type=False, schema=Base.metadata.schema),
        default=DeliveryStatus.DRAFT,
        server_default=text("'DRAFT'"),
        index=True,
        nullable=False,
    )
