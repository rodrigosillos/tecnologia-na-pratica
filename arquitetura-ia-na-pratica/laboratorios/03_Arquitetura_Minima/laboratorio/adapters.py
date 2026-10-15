"""Concrete, local adapters. Fixture keys are public, not credentials."""
import json
from pathlib import Path
import time
from contracts import Completion, DependencyFailure, Document, Principal, Usage
from policy import allowed

ROOT = Path(__file__).resolve().parent
DEMO_IDENTITIES = {"acme-demo": Principal("acme", "operator"),
                   "zen-demo": Principal("zen", "operator")}


class MonotonicClock:
    def now_ms(self):
        return time.monotonic_ns() // 1_000_000


class ManualClock:
    def __init__(self): self.value = 0
    def now_ms(self): return self.value
    def advance(self, milliseconds): self.value += milliseconds


class MemoryRepository:
    def __init__(self, documents):
        self.documents = tuple(documents)

    def search(self, principal, topic, snapshot):
        return tuple(d for d in self.documents
                     if allowed(d, principal, topic, snapshot))


class JsonRepository(MemoryRepository):
    def __init__(self, path):
        rows = json.loads(Path(path).read_text(encoding="utf-8"))
        ids = [row["id"] for row in rows]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate document id")
        documents = []
        for row in rows:
            documents.append(Document(row["id"], row["tenant"],
                row["topic"], row["fact_id"], tuple(row["roles"]),
                row["valid_from"], row["valid_until"],
                row["text"]["pt-BR"], row["text"]["en-US"]))
        super().__init__(documents)


class StubGenerator:
    MODES = ("good", "malformed", "unsupported", "timeout",
             "unavailable", "unexpected", "unknown_usage", "expensive",
             "incomplete", "refused")

    def __init__(self, mode="good"):
        if mode not in self.MODES: raise ValueError("unknown stub mode")
        self.mode = mode

    def complete(self, query, documents, limits):
        if self.mode == "timeout":
            raise DependencyFailure("dependency_timeout")
        if self.mode == "unavailable":
            raise DependencyFailure("dependency_unavailable")
        if self.mode == "unexpected":
            raise RuntimeError("synthetic private diagnostic")
        doc = documents[0]
        payload = {"status":"answer", "fact_id":doc.fact_id,
                   "citation":doc.id, "reason":None}
        if self.mode == "unsupported": payload["fact_id"] = "invented"
        text = "{" if self.mode == "malformed" else json.dumps(payload)
        usage = Usage(180, 200 if self.mode == "expensive" else 50)
        if self.mode == "unknown_usage": usage = None
        state = self.mode if self.mode in ("incomplete", "refused") else "completed"
        return Completion(state, text, usage)
