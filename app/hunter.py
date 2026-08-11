from app.services import ebay
from app.services.database import (
    get_saved_searches,
    has_seen_listing,
    mark_listing_seen,
)
from app.services.authenticity import analyze_listing
from app.services.email import send_listing_notification

def run_hunter():
    searches = get_saved_searches()

    for search in searches:
        print(f"Searching: {search.query}")

        listings = ebay.search(search)

        print(f"Found {len(listings)} listings.")

        for listing in listings:
            if has_seen_listing(listing):
                print(f"Skipping duplicate: {listing.title}")
                continue

            print(f"NEW: {listing.title}")

            result = analyze_listing(listing)

            print(result)

            send_listing_notification(listing, result)

            mark_listing_seen(listing)