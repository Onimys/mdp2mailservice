import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status

from mdp2mailservice.common.utils.files import check_file_size, upload_files
from mdp2mailservice.common.utils.shared import validate_multupart_json
from mdp2mailservice.core.config import settings

from .constants import DeliveryStatus
from .dependencies import get_service
from .schemas import MailSchema, SendMailResponse
from .service import MailService

router = APIRouter(tags=["Mail"], prefix="/mails")


@router.post(
    "/send",
    name="Send mail",
    description="Common mail send.",
    response_model=SendMailResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
@check_file_size(settings.ATTACHMENTS_TOTAL_SIZE)
async def send_mail(
    body: MailSchema = Depends(validate_multupart_json(MailSchema)),
    files: list[UploadFile] | None = File(None, examples=[[]]),
    service: MailService = Depends(get_service),
) -> SendMailResponse:
    mail = await service.send_mail(body, files)
    return SendMailResponse(status=mail.status, mail_id=mail.id)


@router.post(
    "/background-send",
    name="Background send mail",
    description="Background mail send.",
    response_model=SendMailResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
@check_file_size(settings.ATTACHMENTS_TOTAL_SIZE)
async def send_mail_async(
    background_tasks: BackgroundTasks,
    body: MailSchema = Depends(validate_multupart_json(MailSchema)),
    files: list[UploadFile] | None = File(None, examples=[[]]),
    service: MailService = Depends(get_service),
) -> SendMailResponse:
    mail_id = uuid.uuid4()

    upload_paths = None
    if files:
        upload_paths = await upload_files(files, path=f"{settings.ATTACHMENTS_FOLDER}{mail_id}/")

    background_tasks.add_task(service.send_mail, body, upload_paths, mail_id=mail_id, remove_files=True)

    return SendMailResponse(status=DeliveryStatus.QUEUED, mail_id=mail_id)
