"""Solved exercises 17 and 18. Run with Python; no services or credentials."""
import json
from pathlib import Path
from resilience import (Clock, Policy, Controller, Step,
                        ScriptedProvider, CircuitBreaker, CircuitOpen)


def exercise17():
    reports = {}
    for label, delay in [('fits', 400), ('too_late', 900)]:
        clock = Clock()
        policy = Policy(budget_ms=1000)
        provider = ScriptedProvider([
            Step(40, '429', delay), Step(80)])
        reports[label] = Controller(clock, policy).run(provider)
    assert reports['fits']['reason'] == 'success'
    assert reports['fits']['elapsed_ms'] == 520
    assert reports['too_late']['reason'] == 'deadline'
    assert reports['too_late']['attempts'] == 1
    return reports


def exercise18():
    clock = Clock()
    breaker = CircuitBreaker(threshold=2, cooldown_ms=500)
    stale = breaker.acquire(clock.now)
    for _ in range(2):
        permit = breaker.acquire(clock.now)
        breaker.finish(permit, 'unhealthy', clock.now)
    breaker.finish(stale, 'healthy', clock.now)
    after_stale = breaker.state
    clock.advance(500)
    probe = breaker.acquire(clock.now)
    try:
        breaker.acquire(clock.now)
    except CircuitOpen:
        second_probe = 'blocked'
    breaker.finish(probe, 'healthy', clock.now)
    assert after_stale == 'open'
    assert breaker.state == 'closed'
    return dict(after_stale=after_stale,
                second_probe=second_probe, final=breaker.state)


if __name__ == '__main__':
    data = dict(exercise17=exercise17(), exercise18=exercise18())
    out = Path('results'); out.mkdir(exist_ok=True)
    (out/'exercises.json').write_text(
        json.dumps(data, indent=2), encoding='utf-8')
    print(json.dumps(data, indent=2))

