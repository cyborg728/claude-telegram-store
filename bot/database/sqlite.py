import aiosqlite

from bot.database.base import (
    ListingPhotoRepository,
    ListingRepository,
    UnitOfWork,
    UserRepository,
)
from bot.database.models import Listing, ListingPhoto, ListingStatus, User

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    language TEXT NOT NULL DEFAULT 'ru',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    price REAL NOT NULL DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'RUB',
    status TEXT NOT NULL DEFAULT 'draft',
    channel_message_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(telegram_id)
);

CREATE TABLE IF NOT EXISTS listing_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id INTEGER NOT NULL,
    file_id TEXT NOT NULL,
    position INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (listing_id) REFERENCES listings(id)
);
"""


class SQLiteUserRepository(UserRepository):
    def __init__(self, db: aiosqlite.Connection) -> None:
        self._db = db

    async def get_or_create(self, telegram_id: int, **kwargs) -> User:
        cursor = await self._db.execute(
            "SELECT telegram_id, username, first_name, language, created_at "
            "FROM users WHERE telegram_id = ?",
            (telegram_id,),
        )
        row = await cursor.fetchone()
        if row:
            return User(
                telegram_id=row[0],
                username=row[1],
                first_name=row[2],
                language=row[3],
                created_at=row[4],
            )

        username = kwargs.get("username")
        first_name = kwargs.get("first_name")
        language = kwargs.get("language", "ru")
        await self._db.execute(
            "INSERT INTO users (telegram_id, username, first_name, language) "
            "VALUES (?, ?, ?, ?)",
            (telegram_id, username, first_name, language),
        )
        await self._db.commit()
        return User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            language=language,
        )

    async def update_language(self, telegram_id: int, language: str) -> None:
        await self._db.execute(
            "UPDATE users SET language = ? WHERE telegram_id = ?",
            (language, telegram_id),
        )
        await self._db.commit()

    async def get(self, telegram_id: int) -> User | None:
        cursor = await self._db.execute(
            "SELECT telegram_id, username, first_name, language, created_at "
            "FROM users WHERE telegram_id = ?",
            (telegram_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        return User(
            telegram_id=row[0],
            username=row[1],
            first_name=row[2],
            language=row[3],
            created_at=row[4],
        )


class SQLiteListingRepository(ListingRepository):
    def __init__(self, db: aiosqlite.Connection) -> None:
        self._db = db

    async def create(self, listing: Listing) -> Listing:
        cursor = await self._db.execute(
            "INSERT INTO listings (user_id, description, price, currency, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                listing.user_id,
                listing.description,
                listing.price,
                listing.currency,
                listing.status.value,
            ),
        )
        await self._db.commit()
        listing.id = cursor.lastrowid
        return listing

    async def get(self, listing_id: int) -> Listing | None:
        cursor = await self._db.execute(
            "SELECT id, user_id, description, price, currency, status, "
            "channel_message_id, created_at FROM listings WHERE id = ?",
            (listing_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        return Listing(
            id=row[0],
            user_id=row[1],
            description=row[2],
            price=row[3],
            currency=row[4],
            status=ListingStatus(row[5]),
            channel_message_id=row[6],
            created_at=row[7],
        )

    async def get_by_user(self, user_id: int) -> list[Listing]:
        cursor = await self._db.execute(
            "SELECT id, user_id, description, price, currency, status, "
            "channel_message_id, created_at FROM listings "
            "WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        rows = await cursor.fetchall()
        return [
            Listing(
                id=r[0],
                user_id=r[1],
                description=r[2],
                price=r[3],
                currency=r[4],
                status=ListingStatus(r[5]),
                channel_message_id=r[6],
                created_at=r[7],
            )
            for r in rows
        ]

    async def update_status(self, listing_id: int, status: str) -> None:
        await self._db.execute(
            "UPDATE listings SET status = ? WHERE id = ?",
            (status, listing_id),
        )
        await self._db.commit()

    async def set_channel_message_id(
        self, listing_id: int, message_id: int
    ) -> None:
        await self._db.execute(
            "UPDATE listings SET channel_message_id = ? WHERE id = ?",
            (message_id, listing_id),
        )
        await self._db.commit()


class SQLiteListingPhotoRepository(ListingPhotoRepository):
    def __init__(self, db: aiosqlite.Connection) -> None:
        self._db = db

    async def add(self, photo: ListingPhoto) -> ListingPhoto:
        cursor = await self._db.execute(
            "INSERT INTO listing_photos (listing_id, file_id, position) "
            "VALUES (?, ?, ?)",
            (photo.listing_id, photo.file_id, photo.position),
        )
        await self._db.commit()
        photo.id = cursor.lastrowid
        return photo

    async def get_by_listing(self, listing_id: int) -> list[ListingPhoto]:
        cursor = await self._db.execute(
            "SELECT id, listing_id, file_id, position "
            "FROM listing_photos WHERE listing_id = ? ORDER BY position",
            (listing_id,),
        )
        rows = await cursor.fetchall()
        return [
            ListingPhoto(id=r[0], listing_id=r[1], file_id=r[2], position=r[3])
            for r in rows
        ]


class SQLiteUnitOfWork(UnitOfWork):
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def init_db(self) -> None:
        self._db = await aiosqlite.connect(self._db_path)
        await self._db.executescript(_SCHEMA)
        await self._db.commit()
        self.users = SQLiteUserRepository(self._db)
        self.listings = SQLiteListingRepository(self._db)
        self.photos = SQLiteListingPhotoRepository(self._db)

    async def close(self) -> None:
        if self._db:
            await self._db.close()
