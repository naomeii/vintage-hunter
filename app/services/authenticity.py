import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from app.models.listing import Listing
from app.models.authenticity_result import AuthenticityResult
from app.models.recommendation import Recommendation
from app.config import MODEL, AUTHENTICITY_PROMPT_PATH
import json

class AuthenticityAnalysisError(Exception):
    pass

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

with open(AUTHENTICITY_PROMPT_PATH) as file:
    authenticity_prompt = file.read()


def analyze_listing(listing: Listing) -> AuthenticityResult:
    content = _build_listing_content(listing)

    try:
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
    except Exception as error:
        raise AuthenticityAnalysisError(
            f"AI request failed: {error}"
        ) from error

    try:
        response_json = json.loads(response.output_text)
    except json.JSONDecodeError as error:
        raise AuthenticityAnalysisError(
            "AI returned invalid JSON"
        ) from error

    try:
        confidence = response_json["confidence"]
        recommendation = Recommendation(
            response_json["recommendation"]
        )
        explanation = response_json["explanation"]

    except KeyError as error:
        raise AuthenticityAnalysisError(
            f"AI response is missing required field: {error.args[0]}"
        ) from error

    except ValueError as error:
        raise AuthenticityAnalysisError(
            f"AI returned an invalid recommendation: "
            f"{response_json.get('recommendation')}"
        ) from error

    return AuthenticityResult(
        confidence=confidence,
        recommendation=recommendation,
        explanation=explanation,
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
