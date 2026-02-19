from abc import ABC, abstractmethod

from bot.database.models import Listing, ListingPhoto, User


class UserRepository(ABC):
    @abstractmethod
    async def get_or_create(self, telegram_id: int, **kwargs) -> User:
        ...

    @abstractmethod
    async def update_language(self, telegram_id: int, language: str) -> None:
        ...

    @abstractmethod
    async def get(self, telegram_id: int) -> User | None:
        ...


class ListingRepository(ABC):
    @abstractmethod
    async def create(self, listing: Listing) -> Listing:
        ...

    @abstractmethod
    async def get(self, listing_id: int) -> Listing | None:
        ...

    @abstractmethod
    async def get_by_user(self, user_id: int) -> list[Listing]:
        ...

    @abstractmethod
    async def update_status(self, listing_id: int, status: str) -> None:
        ...

    @abstractmethod
    async def set_channel_message_id(
        self, listing_id: int, message_id: int
    ) -> None:
        ...


class ListingPhotoRepository(ABC):
    @abstractmethod
    async def add(self, photo: ListingPhoto) -> ListingPhoto:
        ...

    @abstractmethod
    async def get_by_listing(self, listing_id: int) -> list[ListingPhoto]:
        ...


class UnitOfWork(ABC):
    users: UserRepository
    listings: ListingRepository
    photos: ListingPhotoRepository

    @abstractmethod
    async def init_db(self) -> None:
        ...
