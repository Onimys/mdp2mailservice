from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from mdp2mailservice.core.config import settings

TemplateData = dict[str, Any]


class TemplateType(str, Enum):
    JINJA = "jinja"
    MJML = "mjml"


class Template(BaseModel):
    template: str
    context: TemplateData | None = None
    type: TemplateType = Field(
        default=TemplateType(settings.TEMPLATE_DEFAULT_TYPE),
        description="Type of template ('jinja' or 'mjml').",
    )


class TemplateFile(BaseModel):
    name: str
    path: str
    size: int
