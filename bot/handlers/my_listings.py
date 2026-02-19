from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from bot.config import settings
from bot.database.base import UnitOfWork
from bot.i18n import TRANSLATIONS, t


async def show_my_listings(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    uow: UnitOfWork = context.bot_data["uow"]
    db_user = await uow.users.get(update.effective_user.id)
    lang = db_user.language if db_user else settings.default_language
    tr = t(lang)

    listings = await uow.listings.get_by_user(update.effective_user.id)
    if not listings:
        await update.message.reply_text(tr.no_listings)
        return

    lines = []
    for lst in listings:
        desc = lst.description[:50]
        lines.append(
            f"#{lst.id} — {desc} — {lst.price:,.2f} — {lst.status.value}"
        )

    await update.message.reply_text("\n".join(lines))


def register_my_listings_handlers():
    button_texts = list({tr.btn_my_listings for tr in TRANSLATIONS.values()})
    return [
        MessageHandler(filters.Text(button_texts), show_my_listings),
    ]
