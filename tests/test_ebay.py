from app.services.ebay import search_listings
from app.models.listing import Listing


def test_search_listings_returns_listings():
    listings = search_listings("balenciaga city small")

    # Verify we got a list
    assert isinstance(listings, list)

    # Verify there is at least one result
    assert len(listings) > 0

    # Verify the first item is our Listing model
    assert isinstance(listings[0], Listing)