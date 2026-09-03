import sqlite3

from app.models.search import Search, Condition
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