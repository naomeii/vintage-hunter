from datetime import datetime, timedelta, timezone

from app.services.listing_age import (
    get_listing_age,
    is_listing_recent,
)

def test_listing_age_just_now():
    created_at = (
        datetime.now(timezone.utc) - timedelta(seconds=30)
    ).isoformat()

    assert get_listing_age(created_at) == "Just now"


def test_listing_age_minutes():
    created_at = (
        datetime.now(timezone.utc) - timedelta(minutes=3)
    ).isoformat()

    assert get_listing_age(created_at) == "3 minutes ago"


def test_listing_age_hours():
    created_at = (
        datetime.now(timezone.utc) - timedelta(hours=2)
    ).isoformat()

    assert get_listing_age(created_at) == "2 hours ago"


def test_listing_age_days():
    created_at = (
        datetime.now(timezone.utc) - timedelta(days=2)
    ).isoformat()

    assert get_listing_age(created_at) == "2 days ago"


def test_listing_age_unknown():
    assert get_listing_age(None) == "Unknown"


def test_listing_is_recent():
    created_at = (
        datetime.now(timezone.utc) - timedelta(hours=12)
    ).isoformat()

    assert is_listing_recent(
        created_at,
        max_age_minutes=1440,
    )


def test_listing_is_too_old():
    created_at = (
        datetime.now(timezone.utc) - timedelta(days=2)
    ).isoformat()

    assert not is_listing_recent(
        created_at,
        max_age_minutes=1440,
    )


def test_listing_without_date_is_not_recent():
    assert not is_listing_recent(
        None,
        max_age_minutes=1440,
    )