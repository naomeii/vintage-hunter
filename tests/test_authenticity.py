# from app.services.authenticity import check_openai

# def test_openai_connection():
#     response = check_openai()
    
#     assert response == "OpenAI connection successful."

from app.models.search import Search, Condition
from app.services import ebay
from app.services.authenticity import analyze_listing

def test_analyze_listing():
    search = Search(
        id=None,
        query="balenciaga city small",
        max_price=None,
        condition=Condition.ANY,
    )

    listings = ebay.search(search)

    result = analyze_listing(listings[0])

    print(result)