import requests

from app.config import DISCORD_WEBHOOK_URL
from app.models.listing import Listing
from app.models.authenticity_result import (
    AuthenticityResult,
    Recommendation,
)
from app.services.notification import build_notification


def send_listing_notification(
    listing: Listing,
    result: AuthenticityResult,
):
    if result.recommendation == Recommendation.BUY:
        color = 0x57F287  # Green

    elif result.recommendation == Recommendation.INVESTIGATE:
        color = 0xFEE75C  # Yellow

    else:
        color = 0xED4245  # Red

    payload = {
        "embeds": [
            {
                "title": listing.title,
                "description": build_notification(listing, result),
                "url": listing.listing_url,
                "color": color,
                "thumbnail": {
                    "url": listing.thumbnail_image_url,
                },
            }
        ]
    }

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)

    response.raise_for_status()