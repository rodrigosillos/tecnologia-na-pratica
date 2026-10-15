import copy,json,unittest
from readiness import Drill,BoundedJobs,AdmissionClosed,release_decision
from readiness_scenarios import NAMES,run_case,run_scenarios,evidence_from
from readiness_exercises import exercise35,exercise36
from async_jobs import IdempotencyConflict
from job_worker import payload,read_job
from job_scenarios import scratch_directory
from fixtures import ALICE,BOB

EXPECTED={
 'baseline':(1,0,1,1,1),'provider_outage':(1,0,0,0,3),
 'provider_recovery':(1,0,1,1,3),'queue_saturation':(2,1,2,2,2),
 'paused_admission':(0,1,0,0,0),'replay_full':(2,1,2,2,2),
 'replay_paused':(1,0,1,1,1),'conflict':(1,0,1,1,1),
 'expired_queue':(1,0,0,0,0),'malicious_document':(1,0,0,0,1),
 'forged_approval':(1,0,0,0,1),'source_revoked':(1,0,1,0,1),
 'poisoned_fact':(1,0,1,1,1),'duplicate_delivery':(1,0,1,1,1),
 'source_changed':(1,0,0,0,1),'combined':(2,1,0,0,4),
 'tenant_isolation':(1,0,0,0,0),'restart':(1,0,1,1,1)}

class Matrix(unittest.TestCase):pass
def case_test(name,language):
    def test(self):
        r=run_case(name,language)
        self.assertEqual(tuple(r[k] for k in ('admitted','rejected','result_rows','visible_results','provider_calls')),EXPECTED[name])
        self.assertEqual(r['pending_messages'],0)
        self.assertLessEqual(r['peak_pending'],2)
        self.assertEqual(r['return_deltas'],[-69] if name=='poisoned_fact' else [-15]*r['visible_results'])
        self.assertNotIn('queued',r['states']);self.assertNotIn('running',r['states'])
    return test
for language in ('pt-BR','en-US'):
    for name in NAMES:setattr(Matrix,'test_'+language.replace('-','_')+'_'+name,case_test(name,language))

class AdmissionTests(unittest.TestCase):
    def setUp(self):self.d=Drill(capacity=1)
    def tearDown(self):self.d.close()
    def test_rejection_has_no_job_or_outbox(self):
        self.d.submit('one');self.d.submit('two')
        self.assertEqual(self.d.jobs.db.execute('SELECT count(*) FROM jobs').fetchone()[0],1)
        self.assertEqual(self.d.jobs.db.execute('SELECT count(*) FROM dispatch_outbox').fetchone()[0],1)
    def test_terminal_releases_capacity(self):
        self.d.submit('one');self.d.drain();self.assertIsNotNone(self.d.submit('two'))
    def test_expiry_releases_capacity(self):
        self.d.submit('one',validity_ms=1);self.d.clock.advance(1)
        self.assertIsNotNone(self.d.submit('two'))
    def test_replay_no_extra_capacity(self):
        a=self.d.submit('one');self.assertEqual(a,self.d.submit('one'));self.assertEqual(self.d.jobs.pending(),1)
    def test_conflict_before_pause(self):
        self.d.submit('one');self.d.jobs.pause()
        with self.assertRaises(IdempotencyConflict):self.d.submit('one',spec=payload('en-US'))
    def test_other_tenant_not_replay(self):
        self.d.submit('one');self.assertIsNone(self.d.submit('one',actor=BOB))
    def test_pause_only_new_admissions(self):
        self.d.submit('one');self.d.jobs.pause();self.d.drain()
        self.assertEqual(self.d.report()['visible_results'],1);self.assertIsNone(self.d.submit('two'))
    def test_invalid_payload_does_not_write(self):
        with self.assertRaises(ValueError):self.d.submit('one',spec={'language':'xx'})
        self.assertEqual(self.d.jobs.pending(),0)
    def test_boolean_capacity_rejected(self):
        with self.assertRaises(ValueError):BoundedJobs(capacity=True)
    def test_pause_type(self):
        with self.assertRaises(ValueError):self.d.jobs.pause(1)
    def test_two_connections_share_capacity(self):
        with scratch_directory() as path:
            a=BoundedJobs(path/'j.db',1);b=BoundedJobs(path/'j.db',9)
            try:
                a.submit(ALICE,'one',payload(),0)
                with self.assertRaises(AdmissionClosed):b.submit(ALICE,'two',payload(),0)
                self.assertEqual(b.submit(ALICE,'one',payload(),0)['job_id'],1)
            finally:a.close();b.close()
    def test_pause_persists_reopen(self):
        with scratch_directory() as path:
            a=BoundedJobs(path/'j.db');a.pause();a.close();b=BoundedJobs(path/'j.db')
            try:
                with self.assertRaisesRegex(AdmissionClosed,'paused'):b.submit(ALICE,'one',payload(),0)
            finally:b.close()

class IntegrationTests(unittest.TestCase):
    def test_retry_bounded(self):
        r=run_case('provider_outage');self.assertEqual(r['states'],{'failed':1})
        self.assertEqual(r['provider_calls'],3)
    def test_security_never_retried(self):
        r=run_case('malicious_document');self.assertEqual(r['provider_calls'],1)
        self.assertEqual([e['reason'] for e in r['events'] if e['stage']=='result'],['security:invalid_candidate'])
    def test_recovery_closes_circuit(self):
        r=run_case('provider_recovery');self.assertEqual(r['circuit'],'closed')
    def test_revocation_preserves_row_hides_read(self):
        r=run_case('source_revoked');self.assertEqual(r['states'],{'succeeded':1})
        self.assertEqual((r['result_rows'],r['visible_results']),(1,0))
    def test_audit_has_no_source_or_hostile_payload(self):
        r=run_case('malicious_document');raw=json.dumps(r['events'])
        for marker in ('SYSTEM','sink.invalid','Devolução','Returns:'):self.assertNotIn(marker,raw)
        for event in r['events']:self.assertEqual(set(event),{'at_ms','stage','reason','job'})
    def test_tenant_isolation_at_public_read(self):
        d=Drill()
        try:
            jid=d.submit('one');d.drain();self.assertIsNone(read_job(d.jobs,d.store,BOB,jid,d.clock.now))
        finally:d.close()
    def test_late_completion_cannot_commit(self):
        d=Drill()
        try:
            d.submit('one');d.before_complete=lambda x:x.clock.advance(300)
            self.assertEqual(d.step(),'lease_lost');self.assertEqual(d.report()['result_rows'],0)
        finally:d.close()
    def test_duplicate_does_not_repeat_provider(self):
        self.assertEqual(run_case('duplicate_delivery')['provider_calls'],1)
    def test_core_scenarios_share_real_path(self):
        for name in ('provider_outage','queue_saturation','malicious_document'):
            r=run_case(name);self.assertTrue(any(e['stage']=='provider' for e in r['events']))
    def test_complete_bilingual_evidence(self):
        report=run_scenarios();review=evidence_from(report['runs'])
        self.assertEqual(review['decision'],'hold');self.assertEqual(review['failed'],[])
        for a,b in zip(report['runs'][:18],report['runs'][18:]):
            self.assertEqual({k:v for k,v in a.items() if k!='language'},{k:v for k,v in b.items() if k!='language'})

class ReviewTests(unittest.TestCase):
    def evidence(self):
        return {k:{'status':'pass','reference':'local-evidence'} for k in ('containment','capacity','recovery','live_quality','operations')}
    def test_all_pass_not_authorization(self):self.assertEqual(release_decision(self.evidence())['decision'],'review_candidate')
    def test_unknown_holds(self):
        e=self.evidence();e['live_quality']={'status':'unmeasured','reference':''}
        self.assertEqual(release_decision(e)['unmeasured'],['live_quality'])
    def test_failure_holds(self):
        e=self.evidence();e['capacity']['status']='fail';self.assertEqual(release_decision(e)['failed'],['capacity'])
    def test_missing_reference_rejected(self):
        e=self.evidence();e['capacity']['reference']=''
        with self.assertRaises(ValueError):release_decision(e)
    def test_missing_dimension_rejected(self):
        e=self.evidence();del e['recovery']
        with self.assertRaises(ValueError):release_decision(e)
    def test_unexpected_field_rejected(self):
        e=self.evidence();e['capacity']['approved']=True
        with self.assertRaises(ValueError):release_decision(e)
    def test_absent_language_not_pass(self):
        review=evidence_from([run_case('queue_saturation')])
        self.assertIn('capacity',review['failed'])
    def test_exercise35(self):self.assertEqual(exercise35()['completion_among_offered'],2/3)
    def test_exercise36(self):self.assertEqual(exercise36()['poisoned_delta'],-69)

if __name__=='__main__':unittest.main()
