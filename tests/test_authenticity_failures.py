import json

import pytest

from app.models.listing import Listing
from app.models.authenticity_result import Recommendation
from app.services.authenticity import (
    analyze_listing,
    AuthenticityAnalysisError,
)

def make_listing() -> Listing:
    return Listing(
        platform="ebay",
        listing_id="123",
        title="Balenciaga City Black",
        price=1200.00,
        currency="USD",
        listing_url="https://www.ebay.com/",
        thumbnail_image_url="https://example.com/image.jpg",
        additional_image_urls=[],
        seller_username="test_seller",
        seller_feedback_percent=99.8,
        seller_feedback_score=8432,
        condition="USED",
        created_at="today",
    )


def test_analyze_listing_valid_response(monkeypatch):
    response = type(
        "Response",
        (),
        {
            "output_text": json.dumps(
                {
                    "confidence": 0.84,
                    "recommendation": "buy",
                    "explanation": "Looks authentic.",
                }
            )
        },
    )()

    monkeypatch.setattr(
        "app.services.authenticity.client.responses.create",
        lambda **kwargs: response,
    )

    result = analyze_listing(make_listing())

    assert result.confidence == 0.84
    assert result.recommendation == Recommendation.BUY
    assert result.explanation == "Looks authentic."

def test_analyze_listing_invalid_json(monkeypatch):
    response = type(
        "Response",
        (),
        {
            "output_text": "this is not json"
        },
    )()

    monkeypatch.setattr(
        "app.services.authenticity.client.responses.create",
        lambda **kwargs: response,
    )

    with pytest.raises(AuthenticityAnalysisError):
        analyze_listing(make_listing())

def test_analyze_listing_invalid_recommendation(monkeypatch):
    response = type(
        "Response",
        (),
        {
            "output_text": json.dumps(
                {
                    "confidence": 0.84,
                    "recommendation": "maybe",
                    "explanation": "Looks interesting.",
                }
            )
        },
    )()

    monkeypatch.setattr(
        "app.services.authenticity.client.responses.create",
        lambda **kwargs: response,
    )

    with pytest.raises(AuthenticityAnalysisError):
        analyze_listing(make_listing())

def test_analyze_listing_missing_confidence(monkeypatch):
    response = type(
        "Response",
        (),
        {
            "output_text": json.dumps(
                {
                    "recommendation": "buy",
                    "explanation": "Looks authentic.",
                }
            )
        },
    )()

    monkeypatch.setattr(
        "app.services.authenticity.client.responses.create",
        lambda **kwargs: response,
    )

    with pytest.raises(AuthenticityAnalysisError):
        analyze_listing(make_listing())