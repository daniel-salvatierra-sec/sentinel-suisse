import enum


def enum_values(enum_cls: type[enum.Enum]) -> list[str]:
    return [member.value for member in enum_cls]  # type: ignore[misc]


class ListingType(enum.StrEnum):
    HOUSING = "housing"
    JOB = "job"


class ChannelType(enum.StrEnum):
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    TELEGRAM = "telegram"


class AlertStatus(enum.StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
