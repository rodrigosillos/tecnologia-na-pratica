"""Application use case. No HTTP, file IO, environment or SDK dependency."""
from contracts import DependencyFailure, Limits, Outcome
from policy import choose_evidence, validated_document
from ports import Clock, Generator, Repository
from settings import Settings


class AnswerService:
    def __init__(self, repository: Repository, generator: Generator,
                 clock: Clock, settings: Settings):
        self.repository, self.generator = repository, generator
        self.clock, self.settings = clock, settings

    def answer(self, principal, query):
        start = self.clock.now_ms()
        attempted = False
        def result(status, reason=None, cost=0, doc=None):
            text = None if doc is None else (
                doc.text_pt if query.language == "pt-BR" else doc.text_en)
            return Outcome(status, text, doc.id if doc else None,
                           reason, cost, self.clock.now_ms() - start)
        try:
            candidates = self.repository.search(
                principal, query.topic, self.settings.snapshot)
            docs, reason = choose_evidence(candidates, principal,
                query.topic, self.settings.snapshot)
            remaining = self.settings.timeout_ms - (
                self.clock.now_ms() - start)
            if remaining <= 0:
                return result("error", "deadline_exceeded")
            if reason:
                return result("abstain", reason)
            if self.settings.budget_microusd == 0:
                return result("error", "budget_exceeded")
            attempted = True
            limits = Limits(remaining, self.settings.budget_microusd)
            completion = self.generator.complete(query, docs, limits)
        except DependencyFailure as exc:
            return result("error", exc.code, None if attempted else 0)
        cost = completion.usage.cost if completion.usage else None
        doc = validated_document(completion, docs)
        if self.clock.now_ms() - start > self.settings.timeout_ms:
            return result("error", "deadline_exceeded", cost)
        states = {"incomplete":"generation_incomplete",
                  "refused":"generation_refused",
                  "unavailable":"dependency_unavailable"}
        if completion.state in states:
            return result("error", states[completion.state], cost)
        if doc is None:
            return result("error", "invalid_output", cost)
        if cost is None:
            return result("error", "usage_unknown", None)
        if cost > self.settings.budget_microusd:
            return result("error", "budget_exceeded", cost)
        return result("answer", cost=cost, doc=doc)
