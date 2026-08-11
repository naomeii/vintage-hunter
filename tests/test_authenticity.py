# from app.services.authenticity import check_openai

# def test_openai_connection():
#     response = check_openai()
    
#     assert response == "OpenAI connection successful."
import json

from app.models.search import Search, Condition
from app.services import ebay
from app.services.authenticity import analyze_listing
from app.models.authenticity_result import AuthenticityResult
from app.models.recommendation import Recommendation



def test_analyze_listing():
    search = Search(
        id=None,
        query="balenciaga city small",
        max_price=None,
        condition=Condition.ANY,
    )

    listings = ebay.search(search)

    result = analyze_listing(listings[0])

    print(
        f"{result.recommendation.value.upper()} "
        f"({result.confidence:.0%})"
    )

    assert isinstance(result, AuthenticityResult)
    assert 0 <= result.confidence <= 1
    assert result.recommendation in {
        Recommendation.BUY,
        Recommendation.INVESTIGATE,
        Recommendation.AVOID,
    }
    assert isinstance(result.explanation, str)