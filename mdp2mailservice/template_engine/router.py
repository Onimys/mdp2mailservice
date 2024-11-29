import pathlib
from typing import Annotated

from fastapi import APIRouter, Depends, Path, UploadFile, status
from fastapi.responses import FileResponse

from mdp2mailservice.common.utils.files import check_files, upload_files
from mdp2mailservice.core.config import settings

from .dependencies import map_file_to_template_file, valid_template_filename
from .schemas import TemplateFile

router = APIRouter(tags=["templates"], prefix="/templates")


@router.get("/", name="Get All Templates", response_model=list[TemplateFile])
async def get_all_templates() -> list[TemplateFile]:
    templates = []
    for p in pathlib.Path(settings.TEMPLATE_FOLDER_PATH).iterdir():
        if p.is_file():
            templates.append(map_file_to_template_file(p))
    return templates


@router.get("/{filename}", name="Get Template")
async def get_template(template: TemplateFile = Depends(valid_template_filename)) -> TemplateFile:
    return template


@router.get("/{filename}/download", name="Download Template")
async def download_template(template: TemplateFile = Depends(valid_template_filename)):
    return FileResponse(path=template.path, filename=template.name, media_type="application/octet-stream")


@router.patch(
    "/{filename}/rename/{new_filename}",
    name="Rename Existing Template",
    status_code=status.HTTP_202_ACCEPTED,
)
async def rename_template(
    new_filename: Annotated[str, Path(title="Tempalate filename with extension", min_length=3)],
    template: TemplateFile = Depends(valid_template_filename),
) -> TemplateFile:
    file = pathlib.Path(template.path).rename(f"{settings.TEMPLATE_FOLDER_PATH}/{new_filename}")
    return map_file_to_template_file(file)


@router.post("/upload", name="Upload Template", status_code=status.HTTP_201_CREATED)
@check_files(settings.TEMPLATE_UPLOAD_MAX_SIZE, ext=settings.TEMPLATE_ALLOWED_EXTENSIONS)
async def upload_template(file: UploadFile) -> TemplateFile:
    files = await upload_files([file], path=f"{settings.TEMPLATE_FOLDER_PATH}/")
    return map_file_to_template_file(files[0])


@router.delete("/{filename}", name="Delete Template", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template: TemplateFile = Depends(valid_template_filename),
):
    pathlib.Path(template.path).unlink()
