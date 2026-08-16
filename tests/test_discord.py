import pytest

from app.models.listing import Listing
from app.models.authenticity_result import (
    AuthenticityResult,
    Recommendation,
)
from app.services.discord import DiscordService


@pytest.mark.asyncio
async def test_discord_notification():
    discord_service = DiscordService()

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
            created_at="today",
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

        await discord_service.send_listing_notification(
            listing,
            result,
        )

    finally:
        await discord_service.close()