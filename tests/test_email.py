from app.models.listing import Listing
from app.models.authenticity_result import AuthenticityResult
from app.models.recommendation import Recommendation
from app.services.email import send_listing_notification

def test_send_email():
    listing = Listing(
        platform="ebay",
        listing_id="123",
        title="Balenciaga City Small Black",
        price=1200.00,
        currency="USD",
        listing_url="https://www.ebay.com/",
        thumbnail_image_url="https://i.ebayimg.com/images/g/example/s-l1600.jpg",
        additional_image_urls=[],
        seller_username="japan_seller",
        seller_feedback_percent=99.8,
        seller_feedback_score=2500,
        condition="USED",
        created_at="2026-08-10T12:00:00Z",
    )

    result = AuthenticityResult(
        confidence=0.84,
        recommendation=Recommendation.BUY,
        explanation="The bag appears authentic with only minor uncertainty due to image quality.",
    )

    send_listing_notification(listing, result)