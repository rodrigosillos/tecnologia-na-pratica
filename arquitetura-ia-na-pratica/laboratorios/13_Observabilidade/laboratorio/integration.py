"""Use one shared request deadline with the unchanged Chapter 8 contract."""
from threading import Event
from client import consume, fragments
from fixtures import seeded
from retrieval import answer
from scenarios import request, wire
from resilience import (Clock, Policy, Controller, ControlledFailure,
                        ScriptedProvider, Step)


def integrated_case(language='pt-BR', failure=False, cancel_at=None,
                    shared_deadline=False):
    token = Event()
    clock = Clock(after_advance=lambda now:
                  token.set() if cancel_at is not None and
                  now >= cancel_at else None)
    policy = Policy(budget_ms=450) if shared_deadline else Policy()
    ctl = Controller(clock, policy)
    if failure:
        provider = ScriptedProvider([Step(20, '400')])
    elif shared_deadline:
        provider = ScriptedProvider([Step(290), Step(90)])
    else:
        provider = ScriptedProvider([Step(20, '503'), Step(80), Step(60)])
    texts = (['Prazo de devolução?', 'Prazo de postagem?']
             if language == 'pt-BR' else
             ['Returns window?', 'Shipping days?'])
    req = request(texts, language)
    req['request_id'] = 'demo-09'
    reports = []

    def guarded(store, actor, question, locale):
        report = ctl.run(provider, cancel=token)
        reports.append(report)
        if report['reason'] != 'success':
            raise ControlledFailure(report['reason'])
        return answer(store, actor, question, locale)

    store = seeded()
    try:
        frames = wire(store, req, cancel=token, engine=guarded)
        client = consume(fragments(b''.join(frames), 7),
                         req['request_id'], ['q1', 'q2'])
        return dict(language=language, state=client.state,
                    outcome=client.result['outcome'] if client.result else None,
                    provider_calls=provider.calls, elapsed_ms=clock.now,
                    reports=reports)
    finally:
        store.close()

