from twilio.rest import Client

from app.config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
    USER_PHONE_NUMBER,
)

from app.models.listing import Listing
from app.models.authenticity_result import AuthenticityResult

client = Client(
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
)


def send_listing_notification(
    listing: Listing,
    result: AuthenticityResult,
):
    body = f"""
👜 {listing.title}

💰 {listing.price} {listing.currency}

⭐ {result.recommendation.value.upper()} ({result.confidence:.0%})

{result.explanation}

{listing.listing_url}
"""

    client.messages.create(
        from_=TWILIO_PHONE_NUMBER,
        to=USER_PHONE_NUMBER,
        body=body,
        media_url=[listing.thumbnail_image_url],
    )