"""Ports used by the application; no HTTP, SDK, or storage imports."""
from typing import Protocol
from contracts import Completion, Document, Limits, Principal, Query


class Repository(Protocol):
    def search(self, principal: Principal, topic: str,
               snapshot: str) -> tuple[Document, ...]: ...


class Generator(Protocol):
    def complete(self, query: Query, documents: tuple[Document, ...],
                 limits: Limits) -> Completion: ...


class Clock(Protocol):
    def now_ms(self) -> int: ...
