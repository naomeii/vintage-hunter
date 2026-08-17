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
    assert captured["params"]["limit"] == 5

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