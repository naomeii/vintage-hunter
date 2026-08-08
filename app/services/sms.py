import os

from dotenv import load_dotenv
from twilio.rest import Client
from app.models.listing import Listing

load_dotenv()

def send_new_listing_notification(listing: Listing):
    pass

def send_test_message():
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
    user_phone_number = os.getenv("USER_PHONE_NUMBER")

    if (
        not account_sid
        or not auth_token
        or not twilio_phone_number
        or not user_phone_number
    ):
        raise ValueError("Missing Twilio credentials.")

    client = Client(account_sid, auth_token)

    client.messages.create(
        body="Vintage Hunter is connected to SMS!!! AYEE",
        from_=twilio_phone_number,
        to=user_phone_number,
    )