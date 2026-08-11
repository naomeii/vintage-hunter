import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from app.models.listing import Listing
from app.models.authenticity_result import AuthenticityResult
from app.models.recommendation import Recommendation
from app.config import MODEL, AUTHENTICITY_PROMPT_PATH
import json

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

with open(AUTHENTICITY_PROMPT_PATH) as file:
    authenticity_prompt = file.read()


def analyze_listing(listing: Listing) -> AuthenticityResult:
    content = _build_listing_content(listing)

    response = client.responses.create(
        model=MODEL,
        instructions=authenticity_prompt,
        input=[
            {
                "role": "user",
                "content": content,
            }
        ],
    )

    response_json = json.loads(response.output_text)

    return AuthenticityResult(
        confidence=response_json["confidence"],
        recommendation=Recommendation(response_json["recommendation"]),
        explanation=response_json["explanation"],
    )


def _build_listing_content(listing: Listing) -> list[dict]:
    listing_information = f"""
        Title: {listing.title}

        Price: {listing.price} {listing.currency}

        Condition: {listing.condition}

        Seller: {listing.seller_username}

        Listing URL:
        {listing.listing_url}
    """

    # Add thumbnail image
    content = [
        {
            "type": "input_text",
            "text": listing_information,
        },
        {
            "type": "input_image",
            "image_url": listing.thumbnail_image_url,
        },
    ]

    # Add rest of images except thumbnail again
    for image_url in listing.additional_image_urls:
        if image_url != listing.thumbnail_image_url:
            content.append(
                {
                    "type": "input_image",
                    "image_url": image_url,
                }
            )

    return content
