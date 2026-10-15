"""Solved exercises 5 and 6; synthetic time, no sleeping or provider."""
from dataclasses import asdict
import json
from adapters import (JsonRepository, ManualClock, MemoryRepository,
                      ROOT, StubGenerator)
from contracts import Principal, Query
from service import AnswerService
from settings import Settings


class SlowRepository:
    def __init__(self, inner, clock, delay):
        self.inner, self.clock, self.delay = inner, clock, delay

    def search(self, principal, topic, snapshot):
        self.clock.advance(self.delay)
        return self.inner.search(principal, topic, snapshot)


class TimedGenerator:
    def __init__(self, clock, delay):
        self.clock, self.delay = clock, delay
        self.calls = 0
        self.received_limits = None

    def complete(self, query, documents, limits):
        self.calls += 1
        self.received_limits = limits
        self.clock.advance(self.delay)
        return StubGenerator().complete(query, documents, limits)


def exercise5():
    file_repo = JsonRepository(ROOT / "documents.json")
    memory_repo = MemoryRepository(file_repo.documents)
    observed = []
    for repo in (file_repo, memory_repo):
        service = AnswerService(repo, StubGenerator(),
                                ManualClock(), Settings())
        acme = service.answer(Principal("acme", "operator"),
                              Query("refund", "en-US"))
        zen = service.answer(Principal("zen", "operator"),
                             Query("refund", "en-US"))
        assert acme.citation == "acme-refund-v1"
        assert zen.citation == "zen-refund-v1"
        assert acme.answer != zen.answer
        observed.append([asdict(acme), asdict(zen)])
    assert observed[0] == observed[1]
    return {"adapters_equivalent":True, "outcomes":observed[0]}


def timing_case(repository_ms, generation_ms):
    clock = ManualClock()
    inner = JsonRepository(ROOT / "documents.json")
    repo = SlowRepository(inner, clock, repository_ms)
    generator = TimedGenerator(clock, generation_ms)
    service = AnswerService(repo, generator, clock, Settings())
    result = service.answer(Principal("acme", "operator"), Query("returns"))
    return {"outcome":asdict(result), "calls":generator.calls,
            "received_remaining_ms":(generator.received_limits.remaining_ms
                if generator.received_limits else None)}


def exercise6():
    late = timing_case(1600, 901)
    exact = timing_case(1600, 900)
    exhausted = timing_case(2500, 0)
    assert late['received_remaining_ms'] == 900
    assert late['outcome']['reason'] == 'deadline_exceeded'
    assert late['outcome']['elapsed_ms'] == 2501
    assert late['outcome']['cost_microusd'] == 660
    assert exact['outcome']['status'] == 'answer'
    assert exact['outcome']['elapsed_ms'] == 2500
    assert exhausted['calls'] == 0
    assert exhausted['outcome']['cost_microusd'] == 0
    return {"late":late, "exact":exact, "exhausted":exhausted}


if __name__ == "__main__":
    print(json.dumps({"exercise5":exercise5(), "exercise6":exercise6()},
                     indent=2, ensure_ascii=False))
