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
        query="balenciaga city small",
        max_price=1500,
        condition=Condition.USED,
    )

    database.save_search(search)

    different_search = Search(
        id=None,
        query="balenciaga city small",
        max_price=2000,
        condition=Condition.USED,
    )

    assert not database.search_exists(different_search)


def test_different_condition_is_not_duplicate(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    search = Search(
        id=None,
        query="balenciaga city small",
        max_price=1500,
        condition=Condition.USED,
    )

    database.save_search(search)

    different_search = Search(
        id=None,
        query="balenciaga city small",
        max_price=1500,
        condition=Condition.NEW,
    )

    assert not database.search_exists(different_search)


def test_search_without_max_price(monkeypatch, tmp_path):
    setup_test_database(monkeypatch, tmp_path)

    search = Search(
        id=None,
        query="balenciaga city small",
        max_price=None,
        condition=Condition.ANY,
    )

    database.save_search(search)

    assert database.search_exists(search)