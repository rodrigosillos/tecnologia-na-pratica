from control import parse_action,repeated
from control_scenarios import comparison,run_case


def exercise27():
    results=comparison()
    flow=results['workflow']['summary']
    agent=results['agent']['summary']
    return {'workflow':flow,'agent':agent,
            'extra_units':agent['units']-flow['units'],
            'extra_completions':agent['complete']-flow['complete'],
            'choice':'workflow_for_this_fixture'}


def exercise28():
    seen={}
    raw='{"tool":"read","document":"manual-a"}'
    checks=[repeated(parse_action(raw),seen,2) for _ in range(3)]
    early=run_case('premature_finish')
    revoked=run_case('revoked')
    return {'repeat_flags':checks,'early_reason':early['reason'],
            'revoked_reason':revoked['reason'],
            'outputs_absent':early['output'] is None
                              and revoked['output'] is None}


if __name__=='__main__':
    import json
    from pathlib import Path
    Path('results').mkdir(exist_ok=True)
    result={'exercise27':exercise27(),'exercise28':exercise28()}
    Path('results/exercises.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
