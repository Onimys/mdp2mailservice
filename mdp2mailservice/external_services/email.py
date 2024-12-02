from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import aiosmtplib
from fastapi import UploadFile


async def smtp_send_email(
    *,
    host: str,
    port: int = 25,
    username: str,
    password: str,
    sender: str,
    to_recipients: str,
    cc_recipients: str | None = None,
    subject: str | None = None,
    body: str = "",
    files: list[UploadFile] | list[Path] | None = None,
    use_tls: bool = False,
) -> tuple[dict[str, aiosmtplib.SMTPResponse], str]:
    message = MIMEMultipart()
    message.preamble = subject
    message["Subject"] = subject or ""
    message["From"] = sender
    message["To"] = to_recipients
    message["Bcc"] = to_recipients

    if cc_recipients:
        message["Cc"] = cc_recipients

    message.attach(MIMEText(body, "html", "utf-8"))
    for f in files or []:
        if isinstance(f, Path):
            filename = f.name
            with open(str(f), "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=filename,
                )
        else:
            filename = f.filename
            part = MIMEApplication(await f.read(), Name=filename)

        part.add_header("Content-Disposition", "attachment", filename=filename)
        message.attach(part)

    smtp = aiosmtplib.SMTP(hostname=host, port=port, use_tls=use_tls)
    async with smtp:
        await smtp.login(username, password)
        response = await smtp.send_message(message)
        return response
