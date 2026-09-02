from datetime import datetime, timezone


def get_listing_age(created_at: str | None) -> str:
    if created_at is None:
        return "Unknown"

    created_time = datetime.fromisoformat(
        created_at.replace("Z", "+00:00")
    )

    now = datetime.now(timezone.utc)

    age_seconds = int(
        (now - created_time).total_seconds()
    )

    if age_seconds < 60:
        return "Just now"

    minutes = age_seconds // 60

    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"

    hours = minutes // 60

    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"

    days = hours // 24

    return f"{days} day{'s' if days != 1 else ''} ago"