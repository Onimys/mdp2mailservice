from enum import Enum
from typing import Final


class DeliveryStatus(str, Enum):
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"
    REJECTED = "rejected"


EMPTY_RECIPIENTS_ERROR: Final[str] = "Must provide at least one or more correct recipient."
