from dataclasses import dataclass
from app.models.recommendation import Recommendation


@dataclass
class AuthenticityResult:
    confidence: float
    recommendation: Recommendation
    explanation: str