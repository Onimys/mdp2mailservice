import asyncio
import base64
import json
from functools import wraps
from pathlib import Path
from typing import Annotated, Any, Callable, Coroutine, Optional, ParamSpec, TypedDict, TypeVar

import aiormq
import typer
from dotenv import dotenv_values, load_dotenv

app = typer.Typer(name="mdp2mailservice client")

load_dotenv()
config = dotenv_values(".env")

P = ParamSpec("P")
R = TypeVar("R")


def typer_async(f: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, R]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return asyncio.run(f(*args, **kwargs))

    return wrapper


class FileAttachment(TypedDict):
    filename: str
    content: str


@app.command()
@typer_async
async def send():
    raise NotImplementedError("TODO")


@app.command()
@typer_async
async def send_async(
    to: Annotated[Optional[list[str]], typer.Option("--to", "-to", help="Recipients of the mail")],
    message: Annotated[Optional[str], typer.Option("--message", "-m", help="Message to send")],
    subject: Annotated[Optional[str], typer.Option("--subject", "-s", help="Subject of the mail")] = None,
    cc: Annotated[Optional[list[str]], typer.Option("--cc", "-cc", help="Carbon copy recipients")] = None,
    files: Annotated[Optional[list[Path]], typer.Option("--files", "-f", help="Path to files")] = None,
):
    if not config.get("MDP2MAIL_QUEUE_URL"):
        print("Enviroment varriable MDP2MAIL_QUEUE_URL is not provided.")
        raise typer.Abort()

    connection = await aiormq.connect(str(config.get("MDP2MAIL_QUEUE_URL")))
    channel = await connection.channel()

    message_data = {
        "to_recipients": to,
        "cc_recipients": cc,
        "subject": subject or "",
        "message": message,
    }

    if files:
        attachments: list[FileAttachment] = []
        for path in files or []:
            if path.is_file():
                with open(str(path), "rb") as f:
                    content = base64.b64encode(f.read()).decode()
                    attachments.append({"filename": f.name, "content": content})
            else:
                raise FileNotFoundError(f"File {path} does not exist.")
        message_data |= {"files": attachments}

    message_encode_data = json.dumps(message_data).encode("utf-8")

    assert config.get("MDP2MAIL_QUEUE_NAME"), "Queue name must be provided."
    await channel.basic_publish(body=message_encode_data, routing_key=str(config.get("MDP2MAIL_QUEUE_NAME")))
    await connection.close()


if __name__ == "__main__":
    app()
