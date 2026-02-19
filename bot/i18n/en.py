from dataclasses import dataclass


@dataclass(frozen=True)
class English:
    # General
    btn_sell: str = "📦 Sell item"
    btn_my_listings: str = "📋 My listings"
    btn_change_language: str = "🌐 Language"

    # Start
    welcome: str = (
        "Welcome to the Tech Marketplace!\n\n"
        "Here you can sell your used electronics and gadgets.\n"
        "Use the menu below to get started."
    )
    choose_language: str = "Choose your language:"
    language_set: str = "Language set to English."

    # Listing creation flow
    send_photos: str = (
        "Send photos of your item (1 to 10 photos).\n"
        "When you're done, press the button below."
    )
    photos_received: str = "Photo received! ({count}/{max})"
    send_more_or_done: str = "Send more photos or press Done."
    btn_done_photos: str = "✅ Done"
    max_photos_reached: str = "Maximum number of photos reached. Moving on."
    send_description: str = "Now enter a description for your listing:"
    send_price: str = "Enter the price (number only):"
    invalid_price: str = "Please enter a valid number for the price."
    listing_preview: str = (
        "📋 <b>Your listing preview:</b>\n\n"
        "{description}\n\n"
        "💰 <b>Price:</b> {price}\n\n"
        "Publish this listing?"
    )
    btn_publish: str = "✅ Publish"
    btn_cancel: str = "❌ Cancel"
    listing_published: str = "Your listing has been published to the channel!"
    listing_cancelled: str = "Listing cancelled."

    # Channel post
    channel_post_caption: str = (
        "📦 <b>For Sale</b>\n\n"
        "{description}\n\n"
        "💰 <b>Price:</b> {price}\n\n"
        "👤 <b>Seller:</b> {seller}"
    )
    price_label: str = "Price"
    contact_seller: str = "Contact seller"

    # My listings
    no_listings: str = "You don't have any listings yet."
    listing_item: str = "#{id} — {description:.50} — {price} — {status}"

    # Misc
    error_occurred: str = "An error occurred. Please try again."
    operation_cancelled: str = "Operation cancelled."
