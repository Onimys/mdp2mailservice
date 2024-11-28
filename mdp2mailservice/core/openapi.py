from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from mdp2mailservice.mail.schemas import SendMailRequest
from mdp2mailservice.template_engine.constants import TemplateType
from mdp2mailservice.template_engine.schemas import Template

from .config import settings


def custom_openapi(app: FastAPI):
    def wrapper():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(title="mdp2mailservice", version=settings.APP_VERSION, routes=app.routes)

        multipart_openapi_paths = [
            "Body_Send_mail_api_v1_mails_send_post",
            "Body_Background_send_mail_api_v1_mails_background_send_post",
        ]
        for schema_name in multipart_openapi_paths:
            openapi_schema["components"]["schemas"][schema_name]["properties"]["body"] = {
                "title": "Body",
                "type": "object",
                "$ref": "#/components/schemas/SendMailRequest",
            }

        openapi_schema["components"]["schemas"]["SendMailRequest"] = SendMailRequest.model_json_schema()
        openapi_schema["components"]["schemas"]["Template"] = Template.model_json_schema()
        openapi_schema["components"]["schemas"]["TemplateType"] = [t.value for t in TemplateType]

        openapi_schema["components"]["schemas"]["SendMailRequest"]["properties"]["message"]["anyOf"][0] = {
            "type": "object",
            "$ref": "#/components/schemas/Template",
        }
        del openapi_schema["components"]["schemas"]["SendMailRequest"]["$defs"]

        openapi_schema["components"]["schemas"]["Template"]["properties"]["type"]["$ref"] = (
            "#/components/schemas/TemplateType"
        )

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return wrapper
