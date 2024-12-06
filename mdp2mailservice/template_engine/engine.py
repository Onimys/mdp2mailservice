from abc import ABC
from typing import Type

import jinja2
from mjml import mjml2html

from mdp2mailservice.core.config import settings

from .schemas import Template, TemplateType

templates = jinja2.Environment(loader=jinja2.FileSystemLoader(settings.TEMPLATE_FOLDER_PATH), autoescape=True)


def get_template(name_or_str: str) -> jinja2.Template:
    try:
        template = templates.get_template(name_or_str)
    except jinja2.TemplateNotFound:
        template = jinja2.Template(name_or_str)

    return template


class TemplateFormatter(ABC):
    def __init__(self, message: Template):
        self.message = message

    def format(self) -> str:
        raise NotImplementedError


class JinjaTemplateFormatter(TemplateFormatter):
    def format(self) -> str:
        if self.message.type != TemplateType.JINJA:
            raise ValueError("Message must be a Jinja template.")

        template = get_template(self.message.template)
        return template.render(self.message.context or {})


class MJMLTemplateFormatter(TemplateFormatter):
    def format(self) -> str:
        if self.message.type != TemplateType.MJML:
            raise ValueError("Message must be a MJML template.")

        template = get_template(self.message.template)
        print(mjml2html(template.render(self.message.context or {})))
        return mjml2html(template.render(self.message.context or {}))


class TemplateEngine:
    def __init__(self):
        self.formatters: dict[TemplateType, Type[TemplateFormatter]] = {
            TemplateType.JINJA: JinjaTemplateFormatter,
            TemplateType.MJML: MJMLTemplateFormatter,
        }

    def register_formatter(self, type: TemplateType, formatter: Type[TemplateFormatter]):
        self.formatters[type] = formatter

    def get_formatter(self, message: Template) -> TemplateFormatter:
        return self.formatters[message.type](message)

    def __call__(self, message: Template) -> TemplateFormatter:
        return self.get_formatter(message)
