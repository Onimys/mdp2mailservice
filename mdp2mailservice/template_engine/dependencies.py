import pathlib
from typing import Annotated

from fastapi import Path

from mdp2mailservice.core.config import settings

from .exceptions import TemplateNotFound
from .schemas import TemplateFile


def map_file_to_template_file(file: pathlib.Path) -> TemplateFile:
    return TemplateFile(name=file.name, path=str(file), size=file.stat().st_size)


async def valid_template_filename(
    filename: Annotated[str, Path(title="Tempalate filename with extension")],
) -> TemplateFile:
    file = pathlib.Path(f"{settings.TEMPLATE_FOLDER_PATH}/{filename}")
    if not file.is_file():
        raise TemplateNotFound()

    return map_file_to_template_file(file)
