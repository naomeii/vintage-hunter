from app.services import ebay
from app.services.database import (
    get_saved_searches,
    has_seen_listing,
    mark_listing_seen,
)


# def run_hunter():
#     searches = get_saved_searches()

#     for search in searches:
#         listings = ebay.search(search)

#         for listing in listings:
#             if has_seen_listing(listing):
#                 continue

#             mark_listing_seen(listing)

#             # AI authenticity
#             # Send SMS

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

            mark_listing_seen(listing)