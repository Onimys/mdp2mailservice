from mdp2mailservice.core.exceptions import BaseInternalException


class MailNotFound(BaseInternalException):
    _status_code = 404
    _message = "Mail not found."
