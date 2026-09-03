import sqlite3
from app.models.search import Search, Condition
from app.models.listing import Listing
from app.config import DATABASE_PATH

def initialize_database():
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_user_id TEXT NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
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
                user_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                listing_id TEXT NOT NULL,
                PRIMARY KEY (user_id, platform, listing_id)
            )
        """)

def create_user(discord_user_id: str) -> int:
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO users (discord_user_id)
            VALUES (?)
            """,
            (discord_user_id,),
        )

        return cursor.lastrowid


def get_user(discord_user_id: str):
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, discord_user_id
            FROM users
            WHERE discord_user_id = ?
            """,
            (discord_user_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "discord_user_id": row[1],
        }

def save_search(search: Search):
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO searches (user_id, query, min_price, max_price, condition, color)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                search.user_id,
                search.query,
                search.min_price,
                search.max_price,
                search.condition.value,
                search.color,
            ),
        )


def get_saved_searches(user_id: int) -> list[Search]:
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, user_id, query, min_price, max_price, condition, color
            FROM searches
            WHERE user_id = ?
            """,
            (user_id,),
        )

        rows = cursor.fetchall()

        searches = []

        for row in rows:
            searches.append(
                Search(
                    id=row[0],
                    user_id=row[1],
                    query=row[2],
                    min_price=row[3],
                    max_price=row[4],
                    condition=Condition(row[5]),
                    color=row[6],
                )
            )

        return searches

# prevent saving duplicate searches for a single user
def search_exists(search: Search) -> bool:
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM searches
            WHERE user_id = ?
              AND query = ?
              AND min_price IS ?
              AND max_price IS ?
              AND condition = ?
              AND color IS ?
            """,
            (
                search.user_id,
                search.query,
                search.min_price,
                search.max_price,
                search.condition.value,
                search.color,
            ),
        )

        return cursor.fetchone() is not None

def delete_search(search_id: int, user_id: int):
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM searches
            WHERE id = ?
            AND user_id = ?
            """,
            (search_id, user_id),
        )


def has_seen_listing(user_id: int, listing: Listing,) -> bool:
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT 1
            FROM seen_listings
            WHERE user_id = ?
            AND platform = ?
            AND listing_id = ?
            """,
            (
                user_id,
                listing.platform,
                listing.listing_id,
            ),
        )

        row = cursor.fetchone()

        return row is not None

def mark_listing_seen(user_id: int, listing: Listing,):
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO seen_listings (
                user_id,
                platform,
                listing_id
            )
            VALUES (?, ?, ?)
            """,
            (
                user_id,
                listing.platform,
                listing.listing_id,
            ),
        )

def get_all_users() -> list[dict]:
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, discord_user_id
            FROM users
            """
        )

        rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "discord_user_id": row[1],
            }
            for row in rows
        ]