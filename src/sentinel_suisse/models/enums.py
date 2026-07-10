import enum


class ListingType(str, enum.Enum):
    HOUSING = "housing"
    JOB = "job"


class ChannelType(str, enum.Enum):
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    TELEGRAM = "telegram"


class AlertStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
