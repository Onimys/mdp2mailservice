from typing import Any

from pydantic import BaseModel, Field

from mdp2mailservice.core.config import settings

from .constants import TemplateType

TemplateData = dict[str, Any]


class Template(BaseModel):
    template: str
    context: TemplateData | None = None
    type: TemplateType = Field(
        default=TemplateType(settings.TEMPLATE_DEFAULT_TYPE),
        description="Type of template ('jinja' or 'mjml').",
    )
