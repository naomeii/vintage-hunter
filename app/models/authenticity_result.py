from dataclasses import dataclass

@dataclass
class AuthenticityResult:
    is_authentic: bool
    confidence: float
    explanation: str