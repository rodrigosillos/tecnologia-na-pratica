"""Exercises 7 and 8. Run without packages, network, or model credentials."""
import json
from evaluation import run_suite, bootstrap_delta


def exercise7():
    report=run_suite('refuse_all')
    metrics=report['summary']
    assert metrics['exposures']==0
    assert metrics['answers']==0
    assert metrics['answer_precision'] is None
    assert metrics['answer_recall']==0
    assert metrics['task_passes']==4
    assert not report['gate']['passed']
    return {'metrics':metrics,'gate':report['gate']}


def exercise8():
    base=run_suite('baseline')
    fast=run_suite('fast_unsafe')
    delta=bootstrap_delta(base,fast)
    assert delta['groups']==12
    assert abs(delta['delta']+5/12)<1e-12
    assert delta['upper']<0
    assert fast['summary']['exposures']==4
    assert not fast['gate']['passed']
    missing=run_suite('missing_meter')
    assert missing['summary']['cost_per_correct_answer'] is None
    assert 'unknown_cost' in missing['gate']['failures']
    return {'paired_comparison':delta,'candidate_gate':fast['gate'],
            'missing_meter_gate':missing['gate']}


if __name__=='__main__':
    print(json.dumps({'exercise7':exercise7(),'exercise8':exercise8()},indent=2))
