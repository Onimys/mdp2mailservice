import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Query, UploadFile, status

from mdp2mailservice.common.utils.files import check_file_size, upload_files
from mdp2mailservice.common.utils.shared import validate_multupart_json
from mdp2mailservice.core.config import settings
from mdp2mailservice.mail.models import Mail

from .constants import DEFAULT_MAILS_LIMIT, DEFAULT_MAILS_OFFSET, DeliveryStatus
from .dependencies import get_service, valid_mail_id
from .schemas import MailInDB, SendMailRequest, SendMailResponse
from .service import MailService

router = APIRouter(tags=["mail"], prefix="/mails")


@router.post(
    "/send",
    name="Send mail",
    description="Common mail send.",
    response_model=SendMailResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
@check_file_size(settings.ATTACHMENTS_TOTAL_SIZE)
async def send_mail(
    body: SendMailRequest = Depends(validate_multupart_json(SendMailRequest)),
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
    body: SendMailRequest = Depends(validate_multupart_json(SendMailRequest)),
    files: list[UploadFile] | None = File(None, examples=[[]]),
    service: MailService = Depends(get_service),
) -> SendMailResponse:
    mail_id = uuid.uuid4()

    upload_paths = None
    if files:
        upload_paths = await upload_files(files, path=f"{settings.ATTACHMENTS_FOLDER}{mail_id}/")

    background_tasks.add_task(service.send_mail, body, upload_paths, mail_id=mail_id, remove_files=True)

    return SendMailResponse(status=DeliveryStatus.QUEUED, mail_id=mail_id)


@router.get("/", name="Get All Mails", response_model=list[MailInDB])
async def get_all_mails(
    service: MailService = Depends(get_service),
    limit: int = Query(DEFAULT_MAILS_LIMIT, ge=1),
    offset: int = Query(DEFAULT_MAILS_OFFSET, ge=0),
):
    return await service.get_mails(limit, offset)


@router.get("/{mail_id}", name="Get Mail", response_model=MailInDB)
async def get_mail_by_id(mail: Mail = Depends(valid_mail_id)):
    return mail


@router.get("/{mail_id}/status", response_model=DeliveryStatus)
async def get_mail_status(mail: Mail = Depends(valid_mail_id)):
    return mail.status


@router.delete("/{mail_id}", name="Delete Mail", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mail_by_id(mail: Mail = Depends(valid_mail_id), service: MailService = Depends(get_service)):
    return await service.delete_mail(mail.id)
