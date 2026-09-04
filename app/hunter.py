from app.services import ebay
from app.services.database import (
    get_saved_searches,
    has_seen_listing,
    mark_listing_seen,
    get_user_by_id,
)
from app.services.authenticity import analyze_listing
from app.services.discord import DiscordService

from app.config import HUNTER_MAX_LISTING_AGE_MINUTES
from app.services.listing_age import is_listing_recent


async def run_hunter(user_id: int, discord_service: DiscordService):    
    user = get_user_by_id(user_id)

    if user is None:
        print(f"✕ User {user_id} not found.")
        return

    discord_user_id = user["discord_user_id"]

    searches = get_saved_searches(user_id)

    for search in searches:
        print(f"Searching: {search.query}")

        try:
            listings = ebay.search(search)

            print(f"Found {len(listings)} listings.")

        except Exception as error:
            print(
                f"✕ Search failed for "
                f"'{search.query}': {error}"
            )
            continue

        for listing in listings:

            if not is_listing_recent(
                listing.created_at,
                HUNTER_MAX_LISTING_AGE_MINUTES,
            ):
                print(f"Skipping old listing: {listing.title}")
                continue

            if has_seen_listing(user_id, listing):
                print(f"Skipping duplicate: {listing.title}")
                continue

            print(f"NEW: {listing.title}")

            try:
                result = analyze_listing(listing)

                print(result)

                # waiting to send new notifications
                await discord_service.send_listing_notification(
                    discord_user_id,
                    listing,
                    result,
                )

                mark_listing_seen(user_id, listing)

                print(f"✓ Notified: {listing.title}")

            except Exception as error:
                print(
                    f"✕ Failed to process "
                    f"'{listing.title}': {error}"
                )

                continue