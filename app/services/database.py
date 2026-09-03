import sqlite3
from app.models.search import Search, Condition
from app.models.listing import Listing
from app.config import DATABASE_PATH

def initialize_database():
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                min_price REAL,
                max_price REAL,
                condition TEXT NOT NULL,
                color TEXT
            )
        """)

        # Add color to older databases that don't have it yet
        cursor.execute("PRAGMA table_info(searches)")
        columns = [row[1] for row in cursor.fetchall()]

        if "color" not in columns:
            cursor.execute(
                "ALTER TABLE searches ADD COLUMN color TEXT"
            )

        if "min_price" not in columns:
            cursor.execute(
                "ALTER TABLE searches ADD COLUMN min_price REAL"
            )

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS seen_listings (
                platform TEXT NOT NULL,
                listing_id TEXT NOT NULL,
                PRIMARY KEY (platform, listing_id)
            )
        """)

def save_search(search: Search):
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO searches (query, min_price, max_price, condition, color)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                search.query,
                search.min_price,
                search.max_price,
                search.condition.value,
                search.color,
            ),
        )


def get_saved_searches() -> list[Search]:
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, query, min_price, max_price, condition, color
            FROM searches
        """)

        rows = cursor.fetchall()

        searches = []

        for row in rows:
            searches.append(
                Search(
                    id=row[0],
                    query=row[1],
                    min_price=row[2],
                    max_price=row[3],
                    condition=Condition(row[4]),
                    color=row[5],
                )
            )

        return searches

# prevent saving duplicate searches
def search_exists(search: Search) -> bool:
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM searches
            WHERE query = ?
              AND min_price IS ?
              AND max_price IS ?
              AND condition = ?
              AND color IS ?
            """,
            (
                search.query,
                search.min_price,
                search.max_price,
                search.condition.value,
                search.color,
            ),
        )

        return cursor.fetchone() is not None

def delete_search(search_id: int):
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM searches
            WHERE id = ?
            """,
            (search_id,),
        )


def has_seen_listing(listing: Listing) -> bool:
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT 1
            FROM seen_listings
            WHERE platform = ? AND listing_id = ?
            """,
            (listing.platform, listing.listing_id),
        )

        row = cursor.fetchone()

        return row is not None

def mark_listing_seen(listing: Listing):
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO seen_listings (platform, listing_id)
            VALUES (?, ?)
            """,
            (listing.platform, listing.listing_id),
        )