from unittest.mock import Mock

from app.models.search import Search, Condition
from app.search_cli import show_searches, add_search, remove_search


def test_show_searches_empty(monkeypatch, capsys):
    monkeypatch.setattr(
        "app.search_cli.get_saved_searches",
        lambda: [],
    )

    show_searches()

    output = capsys.readouterr().out

    assert "No saved searches yet" in output


def test_show_searches(monkeypatch, capsys):
    searches = [
        Search(
            id=1,
            query="balenciaga city small",
            max_price=1500,
            condition=Condition.USED,
            color="Black",
        ),
    ]

    monkeypatch.setattr(
        "app.search_cli.get_saved_searches",
        lambda: searches,
    )

    show_searches()

    output = capsys.readouterr().out

    assert "balenciaga city small" in output
    assert "$1,500.00" in output
    assert "USED" in output
    assert "Black" in output


def test_add_search(monkeypatch):
    saved_search = Mock()

    # Pretend this search does not already exist
    monkeypatch.setattr(
        "app.search_cli.search_exists",
        lambda search: False,
    )

    # Prevent the test from writing to the real database
    monkeypatch.setattr(
        "app.search_cli.save_search",
        saved_search,
    )

    # Fake the user's CLI input
    inputs = iter([
        "balenciaga city small",
        "1500",
        "3",
        "1",  # Any color
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(inputs),
    )

    # Run the CLI function
    add_search()

    # Verify the search was saved once
    saved_search.assert_called_once()

    search = saved_search.call_args.args[0]

    # Verify the Search object was built correctly
    assert search.query == "balenciaga city small"
    assert search.max_price == 1500
    assert search.condition == Condition.USED
    assert search.color is None


def test_add_search_rejects_invalid_price(monkeypatch):
    saved_search = Mock()

    monkeypatch.setattr(
        "app.search_cli.save_search",
        saved_search,
    )

    inputs = iter([
        "balenciaga city small",
        "not-a-price",
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(inputs),
    )

    add_search()

    saved_search.assert_not_called()


def test_add_search_rejects_invalid_condition(monkeypatch):
    saved_search = Mock()

    monkeypatch.setattr(
        "app.search_cli.save_search",
        saved_search,
    )

    inputs = iter([
        "balenciaga city small",
        "1500",
        "99",
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(inputs),
    )

    add_search()

    saved_search.assert_not_called()


def test_remove_search(monkeypatch):
    searches = [
        Search(
            id=1,
            query="balenciaga city small",
            max_price=1500,
            condition=Condition.USED,
        ),
    ]

    delete = Mock()

    monkeypatch.setattr(
        "app.search_cli.get_saved_searches",
        lambda: searches,
    )

    monkeypatch.setattr(
        "app.search_cli.delete_search",
        delete,
    )

    # remove_search() calls show_searches(), which reads
    # get_saved_searches(), then asks for the ID.
    monkeypatch.setattr(
        "builtins.input",
        lambda _: "1",
    )

    remove_search()

    delete.assert_called_once_with(1)


def test_remove_search_rejects_missing_id(monkeypatch):
    searches = [
        Search(
            id=1,
            query="balenciaga city small",
            max_price=1500,
            condition=Condition.USED,
        ),
    ]

    delete = Mock()

    monkeypatch.setattr(
        "app.search_cli.get_saved_searches",
        lambda: searches,
    )

    monkeypatch.setattr(
        "app.search_cli.delete_search",
        delete,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "999",
    )

    remove_search()

    delete.assert_not_called()

def test_add_search_rejects_duplicate(monkeypatch):
    saved_search = Mock()

    monkeypatch.setattr(
        "app.search_cli.search_exists",
        lambda search: True,
    )

    monkeypatch.setattr(
        "app.search_cli.save_search",
        saved_search,
    )

    inputs = iter([
        "balenciaga city small",
        "1500",
        "3",
        "1",  # Any color
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(inputs),
    )

    add_search()

    saved_search.assert_not_called()

def test_add_search_with_black_color(monkeypatch):
    saved_search = Mock()

    # Pretend this search does not already exist
    monkeypatch.setattr(
        "app.search_cli.search_exists",
        lambda search: False,
    )

    # Prevent writing to the real database
    monkeypatch.setattr(
        "app.search_cli.save_search",
        saved_search,
    )

    # Choose Black as the color
    inputs = iter([
        "balenciaga city small",
        "1500",
        "3",
        "2",
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(inputs),
    )

    add_search()

    saved_search.assert_called_once()

    search = saved_search.call_args.args[0]

    assert search.color == "Black"


def test_add_search_with_custom_color(monkeypatch):
    saved_search = Mock()

    # Pretend this search does not already exist
    monkeypatch.setattr(
        "app.search_cli.search_exists",
        lambda search: False,
    )

    # Prevent writing to the real database
    monkeypatch.setattr(
        "app.search_cli.save_search",
        saved_search,
    )

    # Choose "Other" and enter a custom color
    inputs = iter([
        "balenciaga city small",
        "1500",
        "3",
        "11",
        "Dark green",
    ])

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(inputs),
    )

    add_search()

    saved_search.assert_called_once()

    search = saved_search.call_args.args[0]

    assert search.color == "Dark green"