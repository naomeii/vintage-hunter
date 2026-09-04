import pytest

from app.models.listing import Listing
from app.models.authenticity_result import (
    AuthenticityResult,
    Recommendation,
)
from app.services.discord import DiscordService
from unittest.mock import AsyncMock, patch


# creates discordservice w/ user ID
# mocks discord related activities
# verifies notif tried to fetch correct user's Discord ID
@pytest.mark.asyncio
async def test_discord_notification():
    discord_service = DiscordService()

    discord_service.client.login = AsyncMock()

    mock_user = AsyncMock()

    discord_service.client.fetch_user = AsyncMock(
        return_value=mock_user
    )

    await discord_service.login()

    try:
        listing = Listing(
            platform="ebay",
            listing_id="123",
            title="Balenciaga The City Classic Purple",
            price=1030.00,
            currency="USD",
            listing_url="https://www.ebay.com/",
            thumbnail_image_url="https://i.ebayimg.com/images/g/example/s-l1600.jpg",
            additional_image_urls=[],
            seller_username="japan_seller",
            seller_feedback_percent=99.8,
            seller_feedback_score=8432,
            condition="USED",
            created_at="2026-09-02T22:00:00Z",
        )

        result = AuthenticityResult(
            confidence=0.84,
            recommendation=Recommendation.BUY,
            explanation=(
                "The leather texture, hardware, and interior tag appear "
                "consistent with an authentic Balenciaga City. "
                "No major authenticity concerns are visible."
            ),
        )

        with patch(
            "app.services.discord.get_listing_age",
            return_value="3 minutes ago",
        ):
            await discord_service.send_listing_notification(
                "123456",
                listing,
                result,
            )

            discord_service.client.fetch_user.assert_called_with("123456")

    finally:
        await discord_service.close()