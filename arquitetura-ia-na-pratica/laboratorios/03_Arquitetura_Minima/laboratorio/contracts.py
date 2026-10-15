"""Technology-independent values and normalized dependency failures."""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Principal:
    tenant: str
    role: str


@dataclass(frozen=True)
class Query:
    topic: str
    language: str = "pt-BR"

    def __post_init__(self):
        if not isinstance(self.topic, str) or not re.fullmatch(
                r"[a-z][a-z0-9_]{0,39}", self.topic):
            raise ValueError("invalid topic")
        if self.language not in ("pt-BR", "en-US"):
            raise ValueError("invalid language")


@dataclass(frozen=True)
class Document:
    id: str
    tenant: str
    topic: str
    fact_id: str
    roles: tuple[str, ...]
    valid_from: str
    valid_until: str | None
    text_pt: str
    text_en: str


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int

    def __post_init__(self):
        if any(type(n) is not int or n < 0 for n in
               (self.input_tokens, self.output_tokens)):
            raise ValueError("usage requires non-negative integers")

    @property
    def cost(self):
        # Fictional rates inherited from chapter 2, micro-USD/token.
        return 2 * self.input_tokens + 6 * self.output_tokens


@dataclass(frozen=True)
class Completion:
    state: str
    text: str
    usage: Usage | None


@dataclass(frozen=True)
class Limits:
    remaining_ms: int
    budget_microusd: int


@dataclass(frozen=True)
class Outcome:
    status: str
    answer: str | None
    citation: str | None
    reason: str | None
    cost_microusd: int | None
    elapsed_ms: int


class DependencyFailure(Exception):
    def __init__(self, code):
        if code not in ("dependency_timeout", "dependency_unavailable"):
            raise ValueError("unknown normalized dependency failure")
        super().__init__(code)
        self.code = code
