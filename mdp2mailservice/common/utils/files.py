import os
import shutil
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Sequence

import aiofiles
from fastapi import UploadFile

from mdp2mailservice.core.exceptions import IncorrectFileExtensionException, MaxFileSizeExceededException


def check_files(max_size: int = 0, ext: Sequence[str] | None = None) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            files: list[UploadFile] | None = kwargs.get("files") or kwargs.get("file")
            if not isinstance(files, list):
                files = [files]  # type: ignore

            if files and max_size > 0:
                total_file_size = sum([f.size or 0 for f in files])
                if total_file_size > max_size:
                    raise MaxFileSizeExceededException()

            if files and ext:
                for f in files:
                    if f.filename and f.filename.split(".")[-1] not in ext:
                        raise IncorrectFileExtensionException()

            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def upload_files(files: list[UploadFile], *, path: str) -> list[Path]:
    file_paths = []
    for f in files or []:
        assert f.filename, "Filename must not be empty."

        filepath = f"{path}/{f.filename}"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        async with aiofiles.open(filepath, "wb") as out_file:
            content = await f.read()
            await out_file.write(content)

            file_paths.append(Path(filepath).resolve())

    return file_paths


async def clean_upload_folder(*, path: str) -> None:
    shutil.rmtree(Path(path), ignore_errors=True)
