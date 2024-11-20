from enum import Enum


class TemplateType(str, Enum):
    JINJA = "jinja"
    MJML = "mjml"
