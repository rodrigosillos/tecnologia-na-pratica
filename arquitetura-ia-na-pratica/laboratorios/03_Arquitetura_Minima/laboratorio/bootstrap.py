"""Composition root: concrete construction stays outside the use case."""
from adapters import JsonRepository, MonotonicClock, ROOT, StubGenerator
from service import AnswerService
from settings import Settings


def wire(settings=None, mode="good"):
    repository = JsonRepository(ROOT / "documents.json")
    generator = StubGenerator(mode)
    clock = MonotonicClock()
    return AnswerService(repository, generator, clock,
                         settings if settings is not None else Settings())
