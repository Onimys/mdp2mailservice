from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from mdp2mailservice.mail.schemas import MailSchema

from .config import settings


def custom_openapi(app: FastAPI):
    def wrapper():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(title="mdp2mailservice", version=settings.APP_VERSION, routes=app.routes)

        multipart_schema_names = [
            "Body_Send_mail_api_v1_mails_send_post",
            "Body_Async_send_mail_api_v1_mails_async_send_post",
        ]
        for schema_name in multipart_schema_names:
            openapi_schema["components"]["schemas"][schema_name]["properties"]["body"] = {
                "title": "Body",
                "type": "object",
                "$ref": "#/components/schemas/MailSchema",
            }
        openapi_schema["components"]["schemas"]["MailSchema"] = MailSchema.model_json_schema()

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return wrapper
