from dataclasses import dataclass


@dataclass(frozen=True)
class Russian:
    # General
    btn_sell: str = "📦 Продать"
    btn_my_listings: str = "📋 Мои объявления"
    btn_change_language: str = "🌐 Язык"

    # Start
    welcome: str = (
        "Добро пожаловать на маркетплейс техники!\n\n"
        "Здесь вы можете продать свою б/у электронику и гаджеты.\n"
        "Используйте меню ниже, чтобы начать."
    )
    choose_language: str = "Выберите язык:"
    language_set: str = "Язык установлен: Русский."

    # Listing creation flow
    send_photos: str = (
        "Отправьте фотографии вашего товара (от 1 до 10).\n"
        "Когда закончите, нажмите кнопку ниже."
    )
    photos_received: str = "Фото получено! ({count}/{max})"
    send_more_or_done: str = "Отправьте ещё фото или нажмите Готово."
    btn_done_photos: str = "✅ Готово"
    max_photos_reached: str = "Максимальное количество фото достигнуто. Продолжаем."
    send_description: str = "Введите описание для вашего объявления:"
    send_price: str = "Введите цену (только число):"
    invalid_price: str = "Пожалуйста, введите корректное число."
    listing_preview: str = (
        "📋 <b>Предпросмотр объявления:</b>\n\n"
        "{description}\n\n"
        "💰 <b>Цена:</b> {price}\n\n"
        "Опубликовать это объявление?"
    )
    btn_publish: str = "✅ Опубликовать"
    btn_cancel: str = "❌ Отменить"
    listing_published: str = "Ваше объявление опубликовано в канале!"
    listing_cancelled: str = "Объявление отменено."

    # Channel post
    channel_post_caption: str = (
        "📦 <b>Продаётся</b>\n\n"
        "{description}\n\n"
        "💰 <b>Цена:</b> {price}\n\n"
        "👤 <b>Продавец:</b> {seller}"
    )
    price_label: str = "Цена"
    contact_seller: str = "Написать продавцу"

    # My listings
    no_listings: str = "У вас пока нет объявлений."
    listing_item: str = "#{id} — {description:.50} — {price} — {status}"

    # Misc
    error_occurred: str = "Произошла ошибка. Попробуйте снова."
    operation_cancelled: str = "Операция отменена."
