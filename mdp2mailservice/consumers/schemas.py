from typing import Annotated

from pydantic import BaseModel, Field

from mdp2mailservice.mail.schemas import MailSchema


class FileAttachment(BaseModel):
    filename: Annotated[str, Field(description="Attachment file name")]
    content: Annotated[str, Field(description="base64 encoded file content")]


class ConsumerMailSchema(MailSchema):
    files: Annotated[list[FileAttachment] | None, Field(description="Attachments")] = None