from bot.i18n import TRANSLATIONS
from bot.handlers.listing import build_listing_conversation
from bot.handlers.my_listings import register_my_listings_handlers
from bot.handlers.start import register_start_handlers

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from bot.config import settings
from bot.database.base import UnitOfWork
from bot.i18n import t
from bot.keyboards.common import language_keyboard


async def _on_language_button(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    uow: UnitOfWork = context.bot_data["uow"]
    db_user = await uow.users.get(update.effective_user.id)
    lang = db_user.language if db_user else settings.default_language
    tr = t(lang)
    await update.message.reply_text(
        tr.choose_language,
        reply_markup=language_keyboard(),
    )


def get_all_handlers():
    sell_texts = list({tr.btn_sell for tr in TRANSLATIONS.values()})
    lang_texts = list({tr.btn_change_language for tr in TRANSLATIONS.values()})

    handlers = []
    handlers.append(build_listing_conversation(sell_texts))
    handlers.extend(register_start_handlers())
    handlers.extend(register_my_listings_handlers())
    handlers.append(
        MessageHandler(filters.Text(lang_texts), _on_language_button)
    )
    return handlers
