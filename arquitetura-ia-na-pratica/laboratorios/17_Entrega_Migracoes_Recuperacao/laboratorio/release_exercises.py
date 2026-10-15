from release_scenarios import run_case


def exercise33():
    lost=run_case('ack_lost')
    stale=run_case('stale_operator')
    rollback=run_case('rollback')
    assert lost['release']=='r2' and lost['epoch']==2
    assert stale['error']=='stale_operator'
    assert rollback['release']=='r1'
    assert rollback['epoch']==3 and rollback['schema']==2
    return {'commit_survived':True,'stale_rejected':True,
            'rollback_epoch':3,'schema_after_rollback':2}


def exercise34():
    old=run_case('pinned_job');new=run_case('new_job')
    restored=run_case('restore')
    assert old['job_release']=='r1'
    assert not old['provenance'] and new['provenance']
    assert restored['release']=='r1'
    assert restored['lost_jobs']==1
    return {'old_job':'r1','new_job':'r2',
            'restore_release':'r1','lost_jobs':1,
            'external_effects_reversed':False}
