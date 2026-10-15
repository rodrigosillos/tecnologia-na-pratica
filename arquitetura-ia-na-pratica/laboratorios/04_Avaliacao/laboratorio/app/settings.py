from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Settings:
    snapshot: str = "2026-10-14"
    timeout_ms: int = 2500
    budget_microusd: int = 1000
    max_body_bytes: int = 2048

    def __post_init__(self):
        if date.fromisoformat(self.snapshot).isoformat() != self.snapshot:
            raise ValueError("snapshot must be YYYY-MM-DD")
        for value in (self.timeout_ms, self.max_body_bytes):
            if type(value) is not int or value <= 0:
                raise ValueError("positive integer required")
        if type(self.budget_microusd) is not int or self.budget_microusd < 0:
            raise ValueError("non-negative integer budget required")
