import random
import smtplib
from email.message import EmailMessage

from app.config import (
    EMAIL_ADDRESS,
    EMAIL_APP_PASSWORD,
    EMAIL_RECIPIENT,
)
from app.models.authenticity_result import (
    AuthenticityResult,
    Recommendation,
)
from app.models.listing import Listing


GREETINGS = [
    "₍^. .^₎Ⳋ I found something!",
    "♡ New treasure spotted!",
    "✿ Look what I found!",
    "ᕙ( •̀ ᗜ •́ )ᕗ Another hunt was successful!",
    "✌︎㋡ I sniffed out another listing!",
    "୨୧ A fresh listing just appeared!",
    "❀ Treasure detected!",
    "✧ Your next favorite piece might be here...",
]

SIGN_OFFS = [
    "Happy hunting ♡",
    "See you next find!",
    "May your dream piece find you soon ♡",
    "Until the next treasure ✿",
    "Good luck hunting! ୨୧",
]

LITTLE_NOTES = [
    "I hope it's the one! ♡",
    "I'll keep searching for you! ✿",
    "Another treasure might appear soon! ❀",
    "I love finding pretty pieces! ₍^. .^₎Ⳋ",
    "I'll let you know if I find another one! ♡",
    "Hopefully this one's hiding in plain sight! ♡",
    "I have a good feeling about this one! ✿",
]


def recommendation_text(recommendation: Recommendation) -> str:
    match recommendation:
        case Recommendation.BUY:
            return "♡ BUY ♡"

        case Recommendation.INVESTIGATE:
            return "❀ Needs a closer look ❀"

        case Recommendation.AVOID:
            return "૮ • ﻌ • ა I'd skip this one"


def subject_prefix(recommendation: Recommendation) -> str:
    match recommendation:
        case Recommendation.BUY:
            return "♡ Dream piece spotted!"

        case Recommendation.INVESTIGATE:
            return "❀ Worth investigating!"

        case Recommendation.AVOID:
            return "૮ • ﻌ • ა I found one..."


def send_listing_notification(
    listing: Listing,
    result: AuthenticityResult,
):
    greeting = random.choice(GREETINGS)
    sign_off = random.choice(SIGN_OFFS)
    note = random.choice(LITTLE_NOTES)

    recommendation = recommendation_text(result.recommendation)

    message = EmailMessage()

    message["Subject"] = (
        f"{subject_prefix(result.recommendation)} {listing.title}"
    )

    # Cute sender name ❤️
    message["From"] = (
        f"₍^. .^₎Ⳋ Your little Vintage Hunter <{EMAIL_ADDRESS}>"
    )

    message["To"] = EMAIL_RECIPIENT

    plain = f"""
♡────────────────────────♡

{greeting}

✿ {listing.title}

₊˚ Price
{listing.price} {listing.currency}

₊˚ Recommendation
{recommendation}

₊˚ Confidence
{result.confidence:.0%}

₊˚ Notes
{result.explanation}

₊˚ View Listing
{listing.listing_url}

♡────────────────────────♡

{note}

{sign_off}

₍^. .^₎Ⳋ Your little Vintage Hunter
"""

    message.set_content(plain)

    html = f"""
<html>
<body style="font-family:Arial,sans-serif;max-width:650px;margin:auto;line-height:1.6">

<h2>♡────────────────────────♡</h2>

<h2>{greeting}</h2>

<h3>✿ {listing.title}</h3>

<p>
<b>₊˚ Price</b><br>
{listing.price} {listing.currency}
</p>

<p>
<b>₊˚ Recommendation</b><br>
{recommendation}
</p>

<p>
<b>₊˚ Confidence</b><br>
{result.confidence:.0%}
</p>

<p>
<a href="{listing.listing_url}">
<img
    src="{listing.thumbnail_image_url}"
    width="340"
    style="border-radius:12px;"
>
</a>
</p>

<p>{result.explanation}</p>

<p>
<a href="{listing.listing_url}">
♡ View Listing ♡
</a>
</p>

<hr>

<p>{note}</p>

<p>{sign_off}</p>

<p><b>₍^. .^₎Ⳋ Your little Vintage Hunter</b></p>

</body>
</html>
"""

    message.add_alternative(html, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        smtp.send_message(message)