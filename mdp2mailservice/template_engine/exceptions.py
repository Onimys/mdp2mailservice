from mdp2mailservice.core.exceptions import BaseInternalException


class TemplateNotFound(BaseInternalException):
    _status_code = 404
    _message = "Template not found."
