from sqladmin import ModelView

from mdp2mailservice.admin import formatters

from .models import Mail


class MailAdmin(ModelView, model=Mail):
    column_default_sort = [("created_at", True)]
    column_list = [Mail.id, Mail.to_recipients, Mail.subject, Mail.message, Mail.status, Mail.created_at]
    column_searchable_list = ("subject", "message", "to_recipients", "status")
    column_sortable_list = ("created_at", "status")
    column_formatters = {Mail.message: formatters.truncate_value("message", 40)}
