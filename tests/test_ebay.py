# from app.services.ebay import get_access_token

# token = get_access_token()

# print(token[:30])

from app.services.ebay import search_listings
import json

results = search_listings("balenciaga city small")

print(json.dumps(results["itemSummaries"][0], indent=2))