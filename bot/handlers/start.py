from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from bot.config import settings
from bot.database.base import UnitOfWork
from bot.i18n import t
from bot.keyboards.common import language_keyboard, main_menu_keyboard


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uow: UnitOfWork = context.bot_data["uow"]
    user = update.effective_user
    db_user = await uow.users.get_or_create(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        language=settings.default_language,
    )
    lang = db_user.language
    tr = t(lang)
    await update.message.reply_text(
        tr.welcome,
        reply_markup=main_menu_keyboard(lang),
    )


async def cmd_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uow: UnitOfWork = context.bot_data["uow"]
    db_user = await uow.users.get(update.effective_user.id)
    lang = db_user.language if db_user else settings.default_language
    tr = t(lang)
    await update.message.reply_text(
        tr.choose_language,
        reply_markup=language_keyboard(),
    )


async def on_language_chosen(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()

    lang_code = query.data.split(":")[1]
    uow: UnitOfWork = context.bot_data["uow"]
    await uow.users.update_language(update.effective_user.id, lang_code)

    tr = t(lang_code)
    await query.edit_message_text(tr.language_set)
    await query.message.reply_text(
        tr.welcome,
        reply_markup=main_menu_keyboard(lang_code),
    )


def register_start_handlers():
    return [
        CommandHandler("start", cmd_start),
        CommandHandler("language", cmd_language),
        CallbackQueryHandler(on_language_chosen, pattern=r"^lang:"),
    ]
