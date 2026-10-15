import json
from pathlib import Path
from threading import Event
from resilience import (Clock, Policy, Controller, RetryBudget,
                        ScriptedProvider, Step)
from integration import integrated_case
from exercises import exercise17, exercise18


def experiment(case):
    token = Event()
    clock = Clock()
    kwargs = {}
    options = dict(cancel=token)
    scripts = {
        'success': [Step(80)],
        'recovered_503': [Step(40, '503'), Step(80)],
        'timeout_recovered': [Step(450), Step(80)],
        'permanent_400': [Step(20, '400')],
        'invalid_output': [Step(20, 'invalid')],
        'retry_quota': [Step(40, '503')],
        'unsafe_operation': [Step(40, '503')],
        'attempt_limit': [Step(10, '503')] * 3,
        'cancel_wait': [Step(40, '503'), Step(80)],
        'deadline': [Step(450)] * 3,
    }
    if case == 'retry_quota': kwargs['retries'] = RetryBudget(0)
    if case == 'unsafe_operation': options['read_only'] = False
    if case == 'deadline': kwargs['policy'] = Policy(budget_ms=650)
    if case == 'cancel_wait':
        clock.after_advance = lambda now: token.set() if now >= 50 else None
    ctl = Controller(clock, **kwargs)
    report = ctl.run(ScriptedProvider(scripts[case]), **options)
    return dict(case=case, **report)


def cascade(layers, attempts):
    """Count leaf calls in an explicit all-failing synchronous retry tree."""
    if layers == 0:
        return 1
    return sum(cascade(layers-1, attempts) for _ in range(attempts))


def run_scenarios():
    names = ['success', 'recovered_503', 'timeout_recovered',
             'permanent_400', 'invalid_output', 'retry_quota',
             'unsafe_operation', 'attempt_limit', 'cancel_wait', 'deadline']
    runs = [experiment(name) for name in names]
    integrations = [dict(case=name, **integrated_case(lang, **options))
                    for lang in ('pt-BR', 'en-US')
                    for name, options in [
                        ('complete', {}), ('failure', {'failure':True}),
                        ('cancelled', {'cancel_at':50}),
                        ('shared_deadline', {'shared_deadline':True})]]
    return dict(cases=len(runs)+len(integrations), runs=runs,
                integration=integrations,
                retry_after=exercise17(), breaker=exercise18(),
                amplification=dict(three_owners=cascade(3,3),
                                   one_owner=cascade(1,3)),
                measurement='Virtual milliseconds, synthetic failures; no benchmark')


if __name__ == '__main__':
    data = run_scenarios()
    out = Path('results'); out.mkdir(exist_ok=True)
    (out/'scenarios.json').write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(data, ensure_ascii=False, indent=2))
