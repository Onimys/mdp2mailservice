from typing import Any

from pydantic import BaseModel

from .constants import TemplateType

TemplateData = dict[str, Any]


class Template(BaseModel):
    template: str
    context: TemplateData | None = None
    type: TemplateType = TemplateType.JINJA
