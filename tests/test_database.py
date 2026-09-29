import sqlite3

from app.models.search import Search, Condition
from app.models.listing import Listing
from app.services import database


def setup_test_database(monkeypatch, tmp_path):
    test_database_path = tmp_path / "test.db"

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        test_database_path,
    )

    database.initialize_database()


def test_search_exists(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    search = Search(
        id=None,
        user_id=1,
        query="balenciaga city small",
        max_price=1500,
        condition=Condition.USED,
    )

    database.save_search(search)

    assert database.search_exists(search)


def test_different_search_does_not_exist(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    search = Search(
        id=None,
        user_id=1,
        query="balenciaga city small",
        max_price=1500,
        condition=Condition.USED,
    )

    database.save_search(search)

    different_search = Search(
        id=None,
        user_id=1,
        query="balenciaga city small",
        max_price=2000,
        condition=Condition.USED,
    )

    assert not database.search_exists(different_search)


def test_different_condition_is_not_duplicate(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    search = Search(
        id=None,
        user_id=1,
        query="balenciaga city small",
        max_price=1500,
        condition=Condition.USED,
    )

    database.save_search(search)

    different_search = Search(
        id=None,
        user_id=1,
        query="balenciaga city small",
        max_price=1500,
        condition=Condition.NEW,
    )

    assert not database.search_exists(different_search)


def test_search_without_max_price(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    search = Search(
        id=None,
        user_id=1,
        query="balenciaga city small",
        max_price=None,
        condition=Condition.ANY,
    )

    database.save_search(search)

    assert database.search_exists(search)

def test_different_min_price_is_not_duplicate(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    search = Search(
        id=None,
        user_id=1,
        query="balenciaga city small",
        min_price=500,
        max_price=1500,
        condition=Condition.ANY,
    )

    database.save_search(search)

    different_search = Search(
        id=None,
        user_id=1,
        query="balenciaga city small",
        min_price=600,
        max_price=1500,
        condition=Condition.ANY,
    )

    assert not database.search_exists(different_search)


def test_create_user(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    user_id = database.create_user("123456789")

    assert user_id is not None

def test_get_user(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    user_id = database.create_user("123456789")

    user = database.get_user("123456789")

    assert user["id"] == user_id
    assert user["discord_user_id"] == "123456789"

def test_same_search_can_exist_for_different_users(
    monkeypatch,
    tmp_path,
):
    setup_test_database(monkeypatch, tmp_path)

    search = Search(
        id=None,
        user_id=1,
        query="balenciaga city small",
        min_price=500,
        max_price=1500,
        condition=Condition.ANY,
    )

    database.save_search(search)

    different_user_search = Search(
        id=None,
        user_id=2,
        query="balenciaga city small",
        min_price=500,
        max_price=1500,
        condition=Condition.ANY,
    )

    assert not database.search_exists(different_user_search)


def test_get_saved_searches_only_returns_user_searches(
    monkeypatch,
    tmp_path,
):
    setup_test_database(monkeypatch, tmp_path)

    user_1_search = Search(
        id=None,
        user_id=1,
        query="balenciaga city small",
        max_price=1500,
        condition=Condition.ANY,
    )

    user_2_search = Search(
        id=None,
        user_id=2,
        query="ysl kate small",
        max_price=1500,
        condition=Condition.ANY,
    )

    database.save_search(user_1_search)
    database.save_search(user_2_search)

    searches = database.get_saved_searches(1)

    assert len(searches) == 1
    assert searches[0].user_id == 1
    assert searches[0].query == "balenciaga city small"

def test_user_cannot_delete_another_users_search(
    monkeypatch,
    tmp_path,
):
    setup_test_database(monkeypatch, tmp_path)

    search = Search(
        id=None,
        user_id=1,
        query="balenciaga city small",
        max_price=1500,
        condition=Condition.ANY,
    )

    database.save_search(search)

    saved_search = database.get_saved_searches(1)[0]

    database.delete_search(
        saved_search.id,
        user_id=2,
    )

    searches = database.get_saved_searches(1)

    assert len(searches) == 1

def test_user_can_delete_their_own_search(
    monkeypatch,
    tmp_path,
):
    setup_test_database(monkeypatch, tmp_path)

    search = Search(
        id=None,
        user_id=1,
        query="balenciaga city small",
        max_price=1500,
        condition=Condition.ANY,
    )

    database.save_search(search)

    saved_search = database.get_saved_searches(1)[0]

    database.delete_search(
        saved_search.id,
        user_id=1,
    )

    searches = database.get_saved_searches(1)

    assert len(searches) == 0


def test_seen_listing_is_user_specific(
    monkeypatch,
    tmp_path,
):
    setup_test_database(monkeypatch, tmp_path)

    listing = Listing(
        platform="ebay",
        listing_id="123",
        title="Balenciaga City",
        price=1000,
        currency="USD",
        listing_url="https://ebay.com/123",
        thumbnail_image_url=None,
        additional_image_urls=[],
        seller_username="seller",
        seller_feedback_percent=100,
        seller_feedback_score=100,
        condition="USED",
    )

    database.mark_listing_seen(1, listing)

    assert database.has_seen_listing(1, listing)
    assert not database.has_seen_listing(2, listing)

def test_same_user_cannot_mark_listing_twice(
    monkeypatch,
    tmp_path,
):
    setup_test_database(monkeypatch, tmp_path)

    listing = Listing(
        platform="ebay",
        listing_id="123",
        title="Balenciaga City",
        price=1000,
        currency="USD",
        listing_url="https://ebay.com/123",
        thumbnail_image_url=None,
        additional_image_urls=[],
        seller_username="seller",
        seller_feedback_percent=100,
        seller_feedback_score=100,
        condition="USED",
    )

    database.mark_listing_seen(1, listing)

    assert database.has_seen_listing(1, listing)


def test_user_can_have_multiple_searches(
    monkeypatch,
    tmp_path,
):
    setup_test_database(monkeypatch, tmp_path)

    search_1 = Search(
        id=None,
        user_id=1,
        query="balenciaga city small",
        max_price=1500,
        condition=Condition.ANY,
    )

    search_2 = Search(
        id=None,
        user_id=1,
        query="ysl kate small",
        max_price=1500,
        condition=Condition.ANY,
    )

    database.save_search(search_1)
    database.save_search(search_2)

    searches = database.get_saved_searches(1)

    assert len(searches) == 2
    assert searches[0].user_id == 1
    assert searches[1].user_id == 1

def test_get_all_users(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    user_1_id = database.create_user("123456")
    user_2_id = database.create_user("987654")

    users = database.get_all_users()

    assert len(users) == 2
    assert users[0]["id"] == user_1_id
    assert users[0]["discord_user_id"] == "123456"
    assert users[1]["id"] == user_2_id
    assert users[1]["discord_user_id"] == "987654"

def test_get_user_by_id(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    user_id = database.create_user("123456")

    user = database.get_user_by_id(user_id)

    assert user["id"] == user_id
    assert user["discord_user_id"] == "123456"

# migration regression test
def test_initialize_database_migrates_old_database(
    monkeypatch,
    tmp_path,
):
    test_database_path = tmp_path / "old.db"

    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        test_database_path,
    )

    with sqlite3.connect(test_database_path) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_user_id TEXT NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            INSERT INTO users (discord_user_id)
            VALUES ('123456')
        """)

        cursor.execute("""
            CREATE TABLE searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                max_price REAL,
                condition TEXT NOT NULL,
                color TEXT,
                min_price REAL
            )
        """)

        cursor.execute("""
            INSERT INTO searches (
                query,
                max_price,
                condition,
                color,
                min_price
            )
            VALUES (
                'balenciaga city small',
                1500,
                'any',
                'Black',
                500
            )
        """)

        cursor.execute("""
            CREATE TABLE seen_listings (
                platform TEXT NOT NULL,
                listing_id TEXT NOT NULL,
                PRIMARY KEY (platform, listing_id)
            )
        """)

        cursor.execute("""
            INSERT INTO seen_listings (
                platform,
                listing_id
            )
            VALUES (
                'ebay',
                '123'
            )
        """)

    database.initialize_database()

    searches = database.get_saved_searches(1)

    assert len(searches) == 1
    assert searches[0].user_id == 1
    assert searches[0].query == "balenciaga city small"
    assert searches[0].min_price == 500
    assert searches[0].max_price == 1500
    assert searches[0].color == "Black"

    listing = Listing(
        platform="ebay",
        listing_id="123",
        title="Balenciaga City",
        price=1000,
        currency="USD",
        listing_url="https://ebay.com/123",
        thumbnail_image_url=None,
        additional_image_urls=[],
        seller_username="seller",
        seller_feedback_percent=100,
        seller_feedback_score=100,
        condition="USED",
    )

    assert database.has_seen_listing(1, listing)