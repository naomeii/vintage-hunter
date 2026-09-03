from unittest.mock import Mock

from app.models.search import Search, Condition
from app.services import ebay


def test_search_applies_max_price_and_condition(monkeypatch):
    search = Search(
        id=None,
        query="balenciaga city small",
        max_price=1500,
        condition=Condition.USED,
    )

    fake_response = Mock()

    fake_response.json.return_value = {
        "itemSummaries": []
    }

    fake_response.raise_for_status.return_value = None

    captured = {}

    def fake_get(url, **kwargs):
        captured["url"] = url
        captured["headers"] = kwargs["headers"]
        captured["params"] = kwargs["params"]

        return fake_response

    monkeypatch.setattr(
        "app.services.ebay.get_access_token",
        lambda: "fake-token",
    )

    monkeypatch.setattr(
        "app.services.ebay.requests.get",
        fake_get,
    )

    ebay.search(search)

    assert captured["params"]["q"] == "balenciaga city small"
    assert captured["params"]["limit"] == 50
    assert captured["params"]["sort"] == "newlyListed"

    assert (
        "price:[..1500]" in captured["params"]["filter"]
    )

    assert (
        "conditions:{USED}" in captured["params"]["filter"]
    )

def test_search_applies_new_condition(monkeypatch):
    search = Search(
        id=None,
        query="balenciaga city small",
        max_price=None,
        condition=Condition.NEW,
    )

    fake_response = Mock()

    fake_response.json.return_value = {
        "itemSummaries": []
    }

    fake_response.raise_for_status.return_value = None

    captured = {}

    def fake_get(url, **kwargs):
        captured["params"] = kwargs["params"]
        return fake_response

    monkeypatch.setattr(
        "app.services.ebay.get_access_token",
        lambda: "fake-token",
    )

    monkeypatch.setattr(
        "app.services.ebay.requests.get",
        fake_get,
    )

    ebay.search(search)

    assert (
        captured["params"]["filter"]
        == "conditions:{NEW}"
    )

def test_search_any_condition_has_no_condition_filter(monkeypatch):
    search = Search(
        id=None,
        query="balenciaga city small",
        max_price=None,
        condition=Condition.ANY,
    )

    fake_response = Mock()

    fake_response.json.return_value = {
        "itemSummaries": []
    }

    fake_response.raise_for_status.return_value = None

    captured = {}

    def fake_get(url, **kwargs):
        captured["params"] = kwargs["params"]
        return fake_response

    monkeypatch.setattr(
        "app.services.ebay.get_access_token",
        lambda: "fake-token",
    )

    monkeypatch.setattr(
        "app.services.ebay.requests.get",
        fake_get,
    )

    ebay.search(search)

    assert "filter" not in captured["params"]

def test_search_paginates(monkeypatch):
    # Create the search we're testing
    search = Search(
        id=None,
        query="balenciaga city small",
        max_price=None,
        condition=Condition.ANY,
    )

    # Helper to create fake eBay listing data
    def make_item(item_id):
        return {
            "itemId": item_id,
            "title": f"Balenciaga City {item_id}",
            "price": {
                "value": "1000",
                "currency": "USD",
            },
            "itemWebUrl": "https://www.ebay.com/",
            "image": {
                "imageUrl": "https://example.com/image.jpg",
            },
            "additionalImages": [],
            "seller": {
                "username": "seller",
                "feedbackPercentage": "99.0",
                "feedbackScore": 1000,
            },
            "condition": "USED",
            "itemCreationDate": "2026-08-18T12:00:00.000Z",
        }

    # Simulate two pages of 50 eBay listings
    first_page = [
        make_item(str(i))
        for i in range(50)
    ]

    second_page = [
        make_item(str(i))
        for i in range(50, 100)
    ]

    # Fake eBay responses for page 1 and page 2
    responses = [
        Mock(
            json=Mock(
                return_value={
                    "itemSummaries": first_page,
                    "next": "https://api.ebay.com/next-page",
                }
            )
        ),
        Mock(
            json=Mock(
                return_value={
                    "itemSummaries": second_page,
                }
            )
        ),
    ]

    # Make both fake responses behave like successful HTTP responses
    for response in responses:
        response.raise_for_status.return_value = None

    # Track the parameters used for each eBay request
    calls = []

    def fake_get(url, **kwargs):
        calls.append(kwargs["params"])
        return responses[len(calls) - 1]

    # Replace the real eBay API calls with our fake ones
    monkeypatch.setattr(
        "app.services.ebay.get_access_token",
        lambda: "fake-token",
    )

    monkeypatch.setattr(
        "app.services.ebay.requests.get",
        fake_get,
    )

    # Run the actual search function
    listings = ebay.search(search)

    # Verify both pages were combined
    assert len(listings) == 100

    # Verify eBay was called twice
    assert len(calls) == 2

    # Verify pagination moved from page 1 to page 2
    assert calls[0]["offset"] == 0
    assert calls[1]["offset"] == 50

    # Verify each request asked for 50 listings
    assert calls[0]["limit"] == 50
    assert calls[1]["limit"] == 50

    # Verify both requests asked for newest listings first
    assert calls[0]["sort"] == "newlyListed"
    assert calls[1]["sort"] == "newlyListed"

def test_get_color_filter(monkeypatch):
    search = Search(
        id=None,
        query="Balenciaga City",
        max_price=1600,
        condition=Condition.ANY,
        color="Black",
    )

    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = {
        "refinement": {
            "dominantCategoryId": "3000",
            "aspectDistributions": [
                {
                    "localizedAspectName": "Color",
                    "aspectValueDistributions": [
                        {
                            "localizedAspectValue": "Black",
                        },
                        {
                            "localizedAspectValue": "Brown",
                        },
                    ],
                }
            ],
        }
    }

    monkeypatch.setattr(
        ebay.requests,
        "get",
        Mock(return_value=response),
    )

    result = ebay._get_color_filter(
        search,
        "fake-token",
    )

    assert result == ("3000", "Black")

def test_get_color_filter_any_color(monkeypatch):
    search = Search(
        id=None,
        query="Balenciaga City",
        max_price=1600,
        condition=Condition.ANY,
        color=None,
    )

    mock_get = Mock()

    monkeypatch.setattr(
        ebay.requests,
        "get",
        mock_get,
    )

    result = ebay._get_color_filter(
        search,
        "fake-token",
    )

    assert result is None
    mock_get.assert_not_called()

# _search_ebat() takes result of _get_color_filter() -> ("3000", "Black") and puts correct category_ids + aspect_filter into eBay API request
def test_search_ebay_applies_color_filter(monkeypatch):
    search = Search(
        id=None,
        query="Balenciaga City",
        max_price=1600,
        condition=Condition.ANY,
        color="Black",
    )

    monkeypatch.setattr(
        ebay,
        "get_access_token",
        Mock(return_value="fake-token"),
    )

    monkeypatch.setattr(
        ebay,
        "_get_color_filter",
        Mock(return_value=("3000", "Black")),
    )

    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = {
        "itemSummaries": [],
    }

    mock_get = Mock(return_value=response)

    monkeypatch.setattr(
        ebay.requests,
        "get",
        mock_get,
    )

    result = ebay._search_ebay(search)

    assert result == []

    params = mock_get.call_args.kwargs["params"]

    assert params["category_ids"] == "3000"
    assert params["aspect_filter"] == (
        "categoryId:3000,Color:{Black}"
    )

def test_search_filters_out_listings_over_max_price(monkeypatch):
    search = Search(
        id=None,
        query="balenciaga city small",
        max_price=1500,
        condition=Condition.ANY,
        color=None,
    )

    fake_response = {
        "itemSummaries": [
            {
                "itemId": "123",
                "title": "Cheap Bag",
                "price": {
                    "value": "1200",
                    "currency": "USD",
                },
                "itemWebUrl": "https://example.com/123",
                "seller": {
                    "username": "seller",
                    "feedbackPercentage": "99.9",
                    "feedbackScore": 1000,
                },
                "condition": "USED",
            },
            {
                "itemId": "456",
                "title": "Expensive Bag",
                "price": {
                    "value": "2000",
                    "currency": "USD",
                },
                "itemWebUrl": "https://example.com/456",
                "seller": {
                    "username": "seller",
                    "feedbackPercentage": "99.9",
                    "feedbackScore": 1000,
                },
                "condition": "USED",
            },
        ]
    }

    class FakeResponse:
        def json(self):
            return fake_response

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        ebay,
        "get_access_token",
        lambda: "fake-token",
    )

    monkeypatch.setattr(
        ebay.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(),
    )

    listings = ebay.search(search)

    assert len(listings) == 1
    assert listings[0].listing_id == "123"
    assert listings[0].price == 1200

def test_search_pagination_keeps_limit_at_50_on_final_page(monkeypatch):
    search = Search(
        id=None,
        query="balenciaga city small",
        max_price=None,
        condition=Condition.ANY,
    )

    def make_item(item_id):
        return {
            "itemId": item_id,
            "title": f"Balenciaga City {item_id}",
            "price": {
                "value": "1000",
                "currency": "USD",
            },
            "itemWebUrl": "https://www.ebay.com/",
            "image": {
                "imageUrl": "https://example.com/image.jpg",
            },
            "additionalImages": [],
            "seller": {
                "username": "seller",
                "feedbackPercentage": "99.0",
                "feedbackScore": 1000,
            },
            "condition": "USED",
            "itemCreationDate": "2026-08-18T12:00:00.000Z",
        }

    # First page has 50 results.
    first_page = [
        make_item(str(i))
        for i in range(50)
    ]

    # Second page has only 35 results.
    second_page = [
        make_item(str(i))
        for i in range(50, 85)
    ]

    responses = [
        Mock(
            json=Mock(
                return_value={
                    "itemSummaries": first_page,
                    "next": "https://api.ebay.com/next-page",
                }
            )
        ),
        Mock(
            json=Mock(
                return_value={
                    "itemSummaries": second_page,
                }
            )
        ),
    ]

    for response in responses:
        response.raise_for_status.return_value = None

    calls = []

    def fake_get(url, **kwargs):
        calls.append(kwargs["params"])
        return responses[len(calls) - 1]

    monkeypatch.setattr(
        ebay,
        "get_access_token",
        lambda: "fake-token",
    )

    monkeypatch.setattr(
        ebay.requests,
        "get",
        fake_get,
    )

    listings = ebay.search(search)

    assert len(listings) == 85

    assert len(calls) == 2

    assert calls[0]["limit"] == 50
    assert calls[0]["offset"] == 0

    assert calls[1]["limit"] == 50
    assert calls[1]["offset"] == 50