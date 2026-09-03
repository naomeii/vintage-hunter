from dataclasses import dataclass
from enum import Enum

class Condition(Enum):
    ANY = "any"
    NEW = "new"
    USED = "used"

@dataclass
class Search:
    id: int | None
    user_id: int
    query: str
    condition: Condition
    min_price: float | None = None
    max_price: float | None = None
    color: str | None = None