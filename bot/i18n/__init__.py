from bot.i18n.en import English
from bot.i18n.ru import Russian

TRANSLATIONS: dict[str, English | Russian] = {
    "en": English(),
    "ru": Russian(),
}

LANGUAGE_LABELS: dict[str, str] = {
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
}


def t(lang: str) -> English | Russian:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"])
