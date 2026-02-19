from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ListingStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    SOLD = "sold"
    CANCELLED = "cancelled"


@dataclass
class User:
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    language: str = "ru"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Listing:
    id: int | None = None
    user_id: int = 0
    description: str = ""
    price: float = 0.0
    currency: str = "RUB"
    status: ListingStatus = ListingStatus.DRAFT
    channel_message_id: int | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ListingPhoto:
    id: int | None = None
    listing_id: int = 0
    file_id: str = ""
    position: int = 0
