import pytest
from unittest.mock import AsyncMock

from app.hunter import run_hunter
from app.models.listing import Listing
from app.models.search import Search, Condition
from app.models.authenticity_result import (
    AuthenticityResult,
    Recommendation,
)

from unittest.mock import AsyncMock, Mock


def make_listing(listing_id: str, title: str) -> Listing:
    return Listing(
        platform="ebay",
        listing_id=listing_id,
        title=title,
        price=1200.00,
        currency="USD",
        listing_url="https://www.ebay.com/",
        thumbnail_image_url="https://example.com/image.jpg",
        additional_image_urls=[],
        seller_username="test_seller",
        seller_feedback_percent=99.8,
        seller_feedback_score=8432,
        condition="USED",
        created_at="today",
    )

# Baseline/everything works
@pytest.mark.asyncio
async def test_run_hunter_success(monkeypatch):
    search = Search(
        id=1,
        query="balenciaga city small",
        max_price=None,
        condition=Condition.ANY,
    )

    listing = make_listing(
        "123",
        "Balenciaga City Small Black",
    )

    result = AuthenticityResult(
        confidence=0.84,
        recommendation=Recommendation.BUY,
        explanation="Looks authentic.",
    )

    monkeypatch.setattr(
        "app.hunter.get_saved_searches",
        lambda: [search],
    )

    monkeypatch.setattr(
        "app.hunter.ebay.search",
        lambda search: [listing],
    )

    monkeypatch.setattr(
        "app.hunter.has_seen_listing",
        lambda listing: False,
    )

    monkeypatch.setattr(
        "app.hunter.analyze_listing",
        lambda listing: result,
    )

    mark_seen = monkeypatch.setattr(
        "app.hunter.mark_listing_seen",
        lambda listing: None,
    )

    discord = AsyncMock()

    await run_hunter(discord)

    discord.send_listing_notification.assert_awaited_once_with(
        listing,
        result,
    )

# Hunter continues after error when eBay search fails with no discord notif
@pytest.mark.asyncio
async def test_run_hunter_search_failure(monkeypatch):
    search = Search(
        id=1,
        query="balenciaga city small",
        max_price=None,
        condition=Condition.ANY,
    )

    monkeypatch.setattr(
        "app.hunter.get_saved_searches",
        lambda: [search],
    )

    def failed_search(search):
        raise RuntimeError("eBay is unavailable")

    monkeypatch.setattr(
        "app.hunter.ebay.search",
        failed_search,
    )

    discord = AsyncMock()

    await run_hunter(discord)

    discord.send_listing_notification.assert_not_awaited()

# If badly formatted AI response, hunter doesn't stop
@pytest.mark.asyncio
async def test_run_hunter_continues_after_listing_failure(monkeypatch):
    search = Search(
        id=1,
        query="balenciaga city small",
        max_price=None,
        condition=Condition.ANY,
    )

    listing_1 = make_listing(
        "123",
        "Balenciaga City Black",
    )

    listing_2 = make_listing(
        "456",
        "Balenciaga City Pink",
    )

    result = AuthenticityResult(
        confidence=0.84,
        recommendation=Recommendation.BUY,
        explanation="Looks authentic.",
    )

    monkeypatch.setattr(
        "app.hunter.get_saved_searches",
        lambda: [search],
    )

    monkeypatch.setattr(
        "app.hunter.ebay.search",
        lambda search: [listing_1, listing_2],
    )

    monkeypatch.setattr(
        "app.hunter.has_seen_listing",
        lambda listing: False,
    )

    def analyze(listing):
        if listing.listing_id == "123":
            raise RuntimeError("OpenAI failed")

        return result

    monkeypatch.setattr(
        "app.hunter.analyze_listing",
        analyze,
    )

    mark_seen = monkeypatch.setattr(
        "app.hunter.mark_listing_seen",
        lambda listing: None,
    )

    discord = AsyncMock()

    await run_hunter(discord)

    discord.send_listing_notification.assert_awaited_once_with(
        listing_2,
        result,
    )

@pytest.mark.asyncio
async def test_run_hunter_does_not_mark_seen_if_discord_fails(
    monkeypatch,
):
    search = Search(
        id=1,
        query="balenciaga city small",
        max_price=None,
        condition=Condition.ANY,
    )

    listing = make_listing(
        "123",
        "Balenciaga City Black",
    )

    result = AuthenticityResult(
        confidence=0.84,
        recommendation=Recommendation.BUY,
        explanation="Looks authentic.",
    )

    monkeypatch.setattr(
        "app.hunter.get_saved_searches",
        lambda: [search],
    )

    monkeypatch.setattr(
        "app.hunter.ebay.search",
        lambda search: [listing],
    )

    monkeypatch.setattr(
        "app.hunter.has_seen_listing",
        lambda listing: False,
    )

    monkeypatch.setattr(
        "app.hunter.analyze_listing",
        lambda listing: result,
    )

    # Track whether mark_listing_seen() gets called
    mark_seen = Mock()

    monkeypatch.setattr(
        "app.hunter.mark_listing_seen",
        mark_seen,
    )

    # Make Discord fail
    discord = AsyncMock()

    discord.send_listing_notification.side_effect = (
        RuntimeError("Discord unavailable")
    )

    await run_hunter(discord)

    # Discord was attempted
    discord.send_listing_notification.assert_awaited_once_with(
        listing,
        result,
    )

    # Because Discord failed, listing must NOT be marked as seen
    mark_seen.assert_not_called()