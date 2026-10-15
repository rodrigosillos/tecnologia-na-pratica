from readiness_scenarios import run_case,evidence_from,run_scenarios

def exercise35():
    r=run_case('queue_saturation')
    assert r['admitted']==2 and r['rejected']==1
    assert r['result_rows']==2 and r['peak_pending']==2
    return {'offered':3,'accepted':2,'completed':2,
            'completion_among_accepted':2/2,
            'completion_among_offered':2/3}

def exercise36():
    poison=run_case('poisoned_fact')
    assert poison['visible_results']==1
    assert poison['return_deltas']==[-69]
    review=evidence_from(run_scenarios()['runs'])
    assert review['decision']=='hold'
    return {'poisoned_delta':-69,'decision':'hold',
            'missing':review['unmeasured'],
            'source_truth_proven':False}
