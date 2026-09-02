from dataclasses import dataclass
from enum import Enum

class Condition(Enum):
    ANY = "any"
    NEW = "new"
    USED = "used"

@dataclass
class Search:
    id: int | None

    query: str
    max_price: float | None
    condition: Condition
    color: str | None = None
