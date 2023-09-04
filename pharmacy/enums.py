from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    In_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    