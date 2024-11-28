from enum import Enum
from typing import Final

DEFAULT_MAILS_LIMIT = 20
DEFAULT_MAILS_OFFSET = 0


class DeliveryStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    REJECTED = "rejected"


EMPTY_RECIPIENTS_ERROR: Final[str] = "Must provide at least one or more correct recipient."
