from mdp2mailservice.core.exceptions import BaseInternalException


class MailNotFound(BaseInternalException):
    _status_code = 404
    _message = "Mail not found."


class NoRecipientsFound(BaseInternalException):
    _status_code = 400
    _message = "Must provide at least one or more correct recipient."
