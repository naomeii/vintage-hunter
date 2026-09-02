import os
import base64

import requests
from dotenv import load_dotenv
from app.models.listing import Listing
from app.models.search import Search, Condition
from app.config import (
    EBAY_RESULTS_PER_PAGE,
    MAX_EBAY_RESULTS_PER_HUNT,
)

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

# Public facing API / interface
def search(search: Search) -> list[Listing]:
    return _search_ebay(search)

# Finds relevant eBay category & return existing colors for the search
def _get_color_filter(search: Search, token: str,) -> tuple[str, str] | None:

    if search.color is None:
        return None

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "q": search.query,
        "fieldgroups": "ASPECT_REFINEMENTS",
    }

    response = requests.get(
        "https://api.ebay.com/buy/browse/v1/item_summary/search",
        headers=headers,
        params=params,
    )

    response.raise_for_status()

    response_json = response.json()

    refinement = response_json.get("refinement", {})

    category_id = (
        refinement.get("dominantCategoryId")
        or response_json.get("dominantCategoryId")
    )

    aspect_distributions = (
        refinement.get("aspectDistributions")
        or response_json.get("aspectDistributions", [])
    )

    if not category_id:
        return None

    for aspect in aspect_distributions:
        if (
            aspect.get("localizedAspectName", "").lower()
            == "color"
        ):
            for value in aspect.get(
                "aspectValueDistributions",
                []
            ):
                if (
                    value.get("localizedAspectValue", "").lower()
                    == search.color.lower()
                ):
                    return (
                        category_id,
                        value["localizedAspectValue"],
                    )

    return None

def _search_ebay(search: Search) -> list[Listing]:
    token = get_access_token()

    color_filter = _get_color_filter(search, token)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    listings = []
    offset = 0

    while len(listings) < MAX_EBAY_RESULTS_PER_HUNT:
        remaining = MAX_EBAY_RESULTS_PER_HUNT - len(listings)

        limit = min(
            EBAY_RESULTS_PER_PAGE,
            remaining,
        )

        params = {
            "q": search.query,
            "limit": limit,
            "offset": offset,
            "sort": "newlyListed",
        }

        if color_filter is not None:
            category_id, color = color_filter

            params["category_ids"] = category_id
            params["aspect_filter"] = (
                f"categoryId:{category_id},"
                f"Color:{{{color}}}"
            )

        filters = []

        if search.max_price is not None:
            filters.append(
                f"price:[..{search.max_price}]"
            )

        if search.condition == Condition.NEW:
            filters.append("conditions:{NEW}")

        elif search.condition == Condition.USED:
            filters.append("conditions:{USED}")

        if filters:
            params["filter"] = ",".join(filters)

        response = requests.get(
            "https://api.ebay.com/buy/browse/v1/item_summary/search",
            headers=headers,
            params=params,
        )

        response.raise_for_status()

        response_json = response.json()

        items = response_json.get(
            "itemSummaries",
            [],
        )

        for item in items:
            listings.append(
                _normalize_ebay_listing(item)
            )

        # No more results
        if len(items) < limit:
            break

        # eBay has another page
        if "next" not in response_json:
            break

        offset += limit

    return listings

def _normalize_ebay_listing(ebay_json_raw_listing: dict) -> Listing:
    raw_listing = ebay_json_raw_listing

    listing_id = raw_listing["itemId"]
    title = raw_listing["title"]
    price = float(raw_listing["price"]["value"])
    currency = raw_listing["price"]["currency"]
    listing_url = raw_listing["itemWebUrl"]

    # Get the thumbnail if eBay provided one
    image = raw_listing.get("image")

    if image:
        thumbnail_image_url = image.get("imageUrl")
    else:
        thumbnail_image_url = None

    # Get any additional images eBay provided
    additional_image_urls = []

    for image in raw_listing.get("additionalImages", []):
        image_url = image.get("imageUrl")

        if image_url:
            additional_image_urls.append(image_url)

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

