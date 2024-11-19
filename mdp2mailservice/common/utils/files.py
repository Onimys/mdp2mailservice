import os
import shutil
from functools import wraps
from pathlib import Path
from typing import Any, Callable

import aiofiles
from fastapi import HTTPException, UploadFile


def check_file_size(max_size: int) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            files: list[UploadFile] | None = kwargs.get("files")
            if files:
                total_file_size = sum([f.size or 0 for f in files])
                if total_file_size > max_size:
                    raise HTTPException(400, "File size exceeds {max} bytes")
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
