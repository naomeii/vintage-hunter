import os
import base64

import requests
from dotenv import load_dotenv
from app.models.listing import Listing

load_dotenv()

def get_access_token() -> str:
    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError("Invalid eBay credentials.")

    # Authorization header
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # Body
    payload = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",
    }

    # Request
    response = requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        headers=headers,
        data=payload,
    )

    response.raise_for_status() # error check

    token = response.json()["access_token"]
    return token

def search_listings(query: str) -> list[Listing]:
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "q": query,
        "limit": 5
    }

    response = requests.get(
        "https://api.ebay.com/buy/browse/v1/item_summary/search",
        headers=headers,
        params=params,
    )

    response.raise_for_status()

    response_json = response.json()
    listings = []

    for item in response_json.get("itemSummaries", []):
        listings.append(normalize_listing(item))

    return listings

def normalize_listing(eBay_json_raw_listing: dict) -> Listing:
    raw_listing = eBay_json_raw_listing

    listing_id = raw_listing["itemId"]
    title = raw_listing["title"]
    price = float(raw_listing["price"]["value"])
    currency = raw_listing["price"]["currency"]
    listing_url = raw_listing["itemWebUrl"]

    thumbnail_image_url = raw_listing["image"]["imageUrl"]
    additional_image_urls = []

    for image in raw_listing.get("additionalImages", []):
        additional_image_urls.append(image["imageUrl"])

    seller_username = raw_listing["seller"]["username"]
    seller_feedback_percent = float(raw_listing["seller"]["feedbackPercentage"])
    seller_feedback_score = raw_listing["seller"]["feedbackScore"]

    condition = raw_listing["condition"]
    created_at = raw_listing["itemCreationDate"]

    return Listing(
        platform="ebay",
        listing_id=listing_id,
        title=title,
        price=price,
        currency=currency,
        listing_url=listing_url,
        thumbnail_image_url=thumbnail_image_url,
        additional_image_urls=additional_image_urls,
        seller_username=seller_username,
        seller_feedback_percent=seller_feedback_percent,
        seller_feedback_score=seller_feedback_score,
        condition=condition,
        created_at=created_at,
    )

