from app.models.search import Search, Condition
from app.services.database import (
    initialize_database,
    save_search,
)
from app.hunter import run_hunter


def test_run_hunter():
    initialize_database()

    save_search(
        Search(
            id=None,
            query="balenciaga city small",
            max_price=None,
            condition=Condition.ANY,
        )
    )

    run_hunter()