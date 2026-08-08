from dataclasses import dataclass

@dataclass
class AuthenticityResult:
    confidence: float
    recommendation: str
    explanation: str