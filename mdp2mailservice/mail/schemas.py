from typing import Any

import email_validator
from pydantic import UUID4, BaseModel, Field, field_validator, model_validator

from .constants import EMPTY_RECIPIENTS_ERROR, DeliveryStatus


class MailSchema(BaseModel):
    to_recipients: list[str] = Field(
        ...,
        description="Recipients of the mail.",
        examples=[
            ["example@mail.ru"],
        ],
    )
    cc_recipients: list[str] | None = Field(default=None, description="Carbon copy recipients.")
    subject: str = Field(default="", description="Subject of the mail.")
    message: str = Field(..., min_length=1, description="Message to send.", examples=["Hello, World!"])

    @model_validator(mode="before")
    @classmethod
    def validate_recipients(cls, values: Any) -> Any:
        fields_for_validation = ("to_recipients", "cc_recipients")
        for field in fields_for_validation:
            recipients = values.get(field)
            if recipients:
                values[field] = [recipient.strip() for recipient in recipients if cls.is_valid_email_address(recipient)]

        return values

    @field_validator("to_recipients")
    def validate_to_recipients(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError(EMPTY_RECIPIENTS_ERROR)

        return value

    @staticmethod
    def is_valid_email_address(email_address: str) -> bool:
        """Check if the provided email address is valid."""
        try:
            email_validator.validate_email(email_address)
        except email_validator.EmailNotValidError:
            return False

        return True


class MailInDB(MailSchema):
    id: UUID4


class SendMailResponse(BaseModel):
    status: DeliveryStatus
    mail_id: UUID4