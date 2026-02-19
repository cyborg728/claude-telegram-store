import logging

from telegram.ext import Application

from bot.config import BotMode, settings
from bot.database.sqlite import SQLiteUnitOfWork
from bot.handlers import get_all_handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    uow = SQLiteUnitOfWork(settings.db_path)
    await uow.init_db()
    application.bot_data["uow"] = uow
    logger.info("Database initialized at %s", settings.db_path)


async def post_shutdown(application: Application) -> None:
    uow: SQLiteUnitOfWork | None = application.bot_data.get("uow")
    if uow:
        await uow.close()
    logger.info("Database connection closed")


def create_application() -> Application:
    app = (
        Application.builder()
        .token(settings.bot_token.get_secret_value())
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    for handler in get_all_handlers():
        app.add_handler(handler)

    return app


def run_polling() -> None:
    logger.info("Starting bot in polling mode")
    app = create_application()
    app.run_polling(drop_pending_updates=True)


def run_webhook() -> None:
    if not settings.webhook_url:
        raise ValueError("WEBHOOK_URL must be set for webhook mode")

    logger.info("Starting bot in webhook mode at %s", settings.webhook_url)
    app = create_application()
    app.run_webhook(
        listen=settings.webhook_host,
        port=settings.webhook_port,
        url_path=settings.webhook_path,
        webhook_url=f"{settings.webhook_url}{settings.webhook_path}",
        drop_pending_updates=True,
    )


def main() -> None:
    if settings.mode == BotMode.WEBHOOK:
        run_webhook()
    else:
        run_polling()
