from app.models.authenticity_result import (
    AuthenticityResult,
    Recommendation,
)
from app.models.listing import Listing


def build_notification(listing: Listing, result: AuthenticityResult) -> str:
    match result.recommendation:
        case Recommendation.BUY:
            greeting = "₍^. .^₎Ⳋ I found something!"
            verdict = "♡ BUY ♡"

        case Recommendation.INVESTIGATE:
            greeting = "( •̀ᴗ•́ )و Worth a closer look!"
            verdict = "❀ INVESTIGATE ❀"

        case Recommendation.AVOID:
            greeting = "૮ • ﻌ • ა I'd pass on this one."
            verdict = "✕ AVOID ✕"

    return f"""{greeting}

{listing.title}

୨୧ Verdict • {verdict} • {result.confidence:.0%}

୨୧ Price
${listing.price:,.2f} {listing.currency}

୨୧ Seller
{listing.seller_username} • {listing.seller_feedback_percent:.1f}% ({listing.seller_feedback_score:,})

{result.explanation}

{listing.listing_url}
"""