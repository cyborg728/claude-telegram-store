from typing import Protocol


class TranslationSet(Protocol):
    # General
    btn_sell: str
    btn_my_listings: str
    btn_change_language: str

    # Start
    welcome: str
    choose_language: str
    language_set: str

    # Listing creation flow
    send_photos: str
    photos_received: str
    send_more_or_done: str
    btn_done_photos: str
    max_photos_reached: str
    send_description: str
    send_price: str
    invalid_price: str
    listing_preview: str
    btn_publish: str
    btn_cancel: str
    listing_published: str
    listing_cancelled: str

    # Channel post
    channel_post_caption: str
    price_label: str
    contact_seller: str

    # My listings
    no_listings: str
    listing_item: str

    # Misc
    error_occurred: str
    operation_cancelled: str


def get_text(translations: dict[str, TranslationSet], lang: str) -> TranslationSet:
    return translations.get(lang, translations["en"])
