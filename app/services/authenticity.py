import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from app.models.listing import Listing
from app.models.authenticity_result import AuthenticityResult

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


from app.config import MODEL, AUTHENTICITY_PROMPT_PATH

with open(AUTHENTICITY_PROMPT_PATH) as file:
    authenticity_prompt = file.read()

# def check_openai():
#     response = client.responses.create(
#         model=MODEL,
#         input="Respond with exactly: OpenAI connection successful."
#     )

#     return response.output_text

def analyze_listing(listing: Listing) -> AuthenticityResult:
    listing_information = f"""
        Title: {listing.title}

        Price: {listing.price} {listing.currency}

        Condition: {listing.condition}

        Seller: {listing.seller_username}

        Listing URL:
        {listing.listing_url}

        Thumbnail:
        {listing.thumbnail_image_url}

        Additional Images:
        {'\n'.join(listing.additional_image_urls)}
    """

    response = client.responses.create(
        model=MODEL,
        instructions=authenticity_prompt,
        input=listing_information,
    )

    return response.output_text