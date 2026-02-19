import logging

from telegram import InputMediaPhoto, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.config import settings
from bot.database.base import UnitOfWork
from bot.i18n import TRANSLATIONS
from bot.database.models import Listing, ListingPhoto, ListingStatus
from bot.i18n import t
from bot.keyboards.common import (
    contact_seller_keyboard,
    done_photos_keyboard,
    main_menu_keyboard,
    publish_keyboard,
)

logger = logging.getLogger(__name__)

PHOTOS, DESCRIPTION, PRICE, CONFIRM = range(4)


def _done_button_texts() -> list[str]:
    return list({tr.btn_done_photos for tr in TRANSLATIONS.values()})


async def _get_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    uow: UnitOfWork = context.bot_data["uow"]
    db_user = await uow.users.get(update.effective_user.id)
    return db_user.language if db_user else settings.default_language


async def start_sell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = await _get_lang(update, context)
    tr = t(lang)
    context.user_data["listing_photos"] = []
    await update.message.reply_text(
        tr.send_photos,
        reply_markup=done_photos_keyboard(lang),
    )
    return PHOTOS


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = await _get_lang(update, context)
    tr = t(lang)
    photos = context.user_data.setdefault("listing_photos", [])

    photo = update.message.photo[-1]
    photos.append(photo.file_id)

    count = len(photos)
    if count >= settings.max_photos:
        await update.message.reply_text(tr.max_photos_reached)
        await update.message.reply_text(tr.send_description)
        return DESCRIPTION

    await update.message.reply_text(
        tr.photos_received.format(count=count, max=settings.max_photos)
        + "\n"
        + tr.send_more_or_done,
        reply_markup=done_photos_keyboard(lang),
    )
    return PHOTOS


async def done_photos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = await _get_lang(update, context)
    tr = t(lang)

    photos = context.user_data.get("listing_photos", [])
    if len(photos) < settings.min_photos:
        await update.message.reply_text(tr.send_photos)
        return PHOTOS

    await update.message.reply_text(tr.send_description)
    return DESCRIPTION


async def receive_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    lang = await _get_lang(update, context)
    tr = t(lang)
    context.user_data["listing_description"] = update.message.text
    await update.message.reply_text(tr.send_price)
    return PRICE


async def receive_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = await _get_lang(update, context)
    tr = t(lang)

    try:
        price = float(update.message.text.replace(",", ".").strip())
        if price <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(tr.invalid_price)
        return PRICE

    context.user_data["listing_price"] = price

    description = context.user_data["listing_description"]
    preview_text = tr.listing_preview.format(
        description=description,
        price=f"{price:,.2f}",
    )

    photos = context.user_data["listing_photos"]
    if len(photos) == 1:
        await update.message.reply_photo(
            photo=photos[0],
            caption=preview_text,
            parse_mode="HTML",
            reply_markup=publish_keyboard(lang),
        )
    else:
        media = [InputMediaPhoto(media=fid) for fid in photos]
        media[0] = InputMediaPhoto(media=photos[0], caption=preview_text, parse_mode="HTML")
        await update.message.reply_media_group(media=media)
        await update.message.reply_text(
            tr.btn_publish + "?",
            reply_markup=publish_keyboard(lang),
        )

    return CONFIRM


async def publish_listing(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    lang = await _get_lang(update, context)
    tr = t(lang)
    uow: UnitOfWork = context.bot_data["uow"]
    user = update.effective_user

    listing = Listing(
        user_id=user.id,
        description=context.user_data["listing_description"],
        price=context.user_data["listing_price"],
        status=ListingStatus.ACTIVE,
    )
    listing = await uow.listings.create(listing)

    photos = context.user_data["listing_photos"]
    for i, file_id in enumerate(photos):
        await uow.photos.add(
            ListingPhoto(listing_id=listing.id, file_id=file_id, position=i)
        )

    seller_name = f"@{user.username}" if user.username else user.first_name
    caption = tr.channel_post_caption.format(
        description=listing.description,
        price=f"{listing.price:,.2f}",
        seller=seller_name,
    )

    keyboard = None
    if user.username:
        keyboard = contact_seller_keyboard(lang, user.username)

    try:
        if len(photos) == 1:
            msg = await context.bot.send_photo(
                chat_id=settings.channel_id,
                photo=photos[0],
                caption=caption,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        else:
            media = [InputMediaPhoto(media=fid) for fid in photos]
            media[0] = InputMediaPhoto(
                media=photos[0], caption=caption, parse_mode="HTML"
            )
            messages = await context.bot.send_media_group(
                chat_id=settings.channel_id,
                media=media,
            )
            msg = messages[0]
            if keyboard and user.username:
                await context.bot.send_message(
                    chat_id=settings.channel_id,
                    text=f"👤 {seller_name}",
                    reply_markup=keyboard,
                )

        await uow.listings.set_channel_message_id(listing.id, msg.message_id)
    except Exception:
        logger.exception("Failed to publish listing #%s to channel", listing.id)

    await query.edit_message_text(tr.listing_published)
    await query.message.reply_text(
        tr.welcome,
        reply_markup=main_menu_keyboard(lang),
    )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_listing(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    lang = await _get_lang(update, context)
    tr = t(lang)

    await query.edit_message_text(tr.listing_cancelled)
    await query.message.reply_text(
        tr.welcome,
        reply_markup=main_menu_keyboard(lang),
    )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    lang = await _get_lang(update, context)
    tr = t(lang)

    await update.message.reply_text(
        tr.operation_cancelled,
        reply_markup=main_menu_keyboard(lang),
    )
    context.user_data.clear()
    return ConversationHandler.END


def build_listing_conversation(sell_button_texts: list[str]) -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Text(sell_button_texts),
                start_sell,
            ),
            CommandHandler("sell", start_sell),
        ],
        states={
            PHOTOS: [
                MessageHandler(filters.PHOTO, receive_photo),
                MessageHandler(
                    filters.Text(_done_button_texts()),
                    done_photos,
                ),
            ],
            DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description),
            ],
            PRICE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_price),
            ],
            CONFIRM: [
                CallbackQueryHandler(publish_listing, pattern=r"^listing:publish$"),
                CallbackQueryHandler(cancel_listing, pattern=r"^listing:cancel$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel_command),
        ],
    )
