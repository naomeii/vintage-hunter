from dataclasses import dataclass

@dataclass
class Listing:
    platform: str
    listing_id: str
    title: str
    price: float
    currency: str
    listing_url: str
    thumbnail_image_url: str | None
    additional_image_urls: list[str]
    seller_username: str
    seller_feedback_percent: float
    seller_feedback_score: int
    condition: str
    created_at: str