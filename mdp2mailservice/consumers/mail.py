import base64
from io import BytesIO

from fastapi import Depends, UploadFile
from faststream.rabbit import RabbitQueue
from faststream.rabbit.fastapi import Logger, RabbitRouter

from mdp2mailservice.core.config import settings
from mdp2mailservice.mail.dependencies import get_service
from mdp2mailservice.mail.schemas import SendMailRequest
from mdp2mailservice.mail.service import MailService

from .schemas import ConsumerMailRequest

assert settings.MAIL_QUEUE_CONSUMER_ENABLED, "RabbitMQ consumer must be enabled."
assert settings.MAIL_QUEUE_CONSUMER_URL, "RabbitMQ URL must be provided."

router = RabbitRouter(
    settings.MAIL_QUEUE_CONSUMER_URL.get_secret_value(),
    max_consumers=settings.MAIL_QUEUE_CONSUMER_MAX_WORKERS,
    schema_url="/asyncapi",
    asyncapi_url=str(settings.MAIL_QUEUE_CONSUMER_URL),
    tags=["Consumer"],
)
queue = RabbitQueue(settings.MAIL_QUEUE_CONSUMER_QUEUE, auto_delete=settings.MAIL_QUEUE_CONSUMER_AUTO_DELETE)


@router.subscriber(
    queue,
    title="send-mail",
    description="Common mail send with RabbitMQ.",
)
async def stream_send_mail(
    msg: ConsumerMailRequest, logger: Logger, service: MailService = Depends(get_service)
) -> None:
    logger.info(msg)

    mail = SendMailRequest(**msg.model_dump(exclude={"files"}))

    files: list[UploadFile] = []
    for file in msg.files or []:
        data = base64.b64decode(file.content)
        file_like_object = BytesIO(data)
        files.append(UploadFile(file_like_object, filename=file.filename))

    await service.send_mail(mail, files=files)
