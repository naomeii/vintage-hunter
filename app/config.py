from pathlib import Path
import os

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data"

DATABASE_PATH = DATA_DIR / "vintage_hunter.db"
AUTHENTICITY_PROMPT_PATH = DATA_DIR / "AUTHENTICITY_PROMPT.md"

MODEL = "gpt-5.5"

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_USER_ID_RAW = os.getenv("DISCORD_USER_ID")

if not DISCORD_USER_ID_RAW:
    raise ValueError("DISCORD_USER_ID is not configured.")

DISCORD_USER_ID = int(DISCORD_USER_ID_RAW)

HUNTER_INTERVAL_SECONDS = int(
    os.getenv("HUNTER_INTERVAL_SECONDS", "300")
)