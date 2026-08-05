import os
import base64

import requests
from dotenv import load_dotenv

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
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",
    }

    # Request
    response = requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        headers=headers,
        data=data,
    )

    response.raise_for_status() # error check

    token = response.json()["access_token"]
    return token

def search_listings(query: str) -> dict:
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

    return response.json()

