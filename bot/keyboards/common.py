from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from bot.i18n import LANGUAGE_LABELS, t


def main_menu_keyboard(lang: str) -> ReplyKeyboardMarkup:
    tr = t(lang)
    return ReplyKeyboardMarkup(
        [
            [tr.btn_sell],
            [tr.btn_my_listings],
            [tr.btn_change_language],
        ],
        resize_keyboard=True,
    )


def language_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=label, callback_data=f"lang:{code}")]
        for code, label in LANGUAGE_LABELS.items()
    ]
    return InlineKeyboardMarkup(buttons)


def done_photos_keyboard(lang: str) -> ReplyKeyboardMarkup:
    tr = t(lang)
    return ReplyKeyboardMarkup(
        [[tr.btn_done_photos]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def publish_keyboard(lang: str) -> InlineKeyboardMarkup:
    tr = t(lang)
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(tr.btn_publish, callback_data="listing:publish"),
                InlineKeyboardButton(tr.btn_cancel, callback_data="listing:cancel"),
            ]
        ]
    )


def contact_seller_keyboard(lang: str, seller_username: str) -> InlineKeyboardMarkup:
    tr = t(lang)
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    tr.contact_seller,
                    url=f"https://t.me/{seller_username}",
                )
            ]
        ]
    )
