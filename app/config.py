from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"

DATABASE_PATH = DATA_DIR / "vintage_hunter.db"
AUTHENTICITY_PROMPT_PATH = DATA_DIR / "AUTHENTICITY_PROMPT.md"

MODEL="gpt-5.5"
