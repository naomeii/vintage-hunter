from app.services.ebay import search
from app.models.search import Search, Condition
from app.models.listing import Listing


def test_search_returns_listings():
    listings = search(
        Search(
            id=None,
            query="balenciaga city small",
            max_price=None,
            condition=Condition.ANY,
        )
    )

    # Verify we got a list
    assert isinstance(listings, list)

    # Verify there is at least one result
    assert len(listings) > 0

    # Verify the first item is our Listing model
    assert isinstance(listings[0], Listing)