from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import json
import unittest
from async_jobs import (Jobs, LocalQueue, Crash, LeaseLost,
                        IdempotencyConflict, request_fingerprint)
from fixtures import ALICE, ADMIN, BOB, ingest
from job_worker import manuals, payload, capture, compare, work_once, read_job
from job_scenarios import restart_case, scratch_directory, run_case
from job_exercises import exercise19, exercise20
from resilience import Clock


class JobTests(unittest.TestCase):
    def setUp(self):
        self.jobs=Jobs();self.queue=LocalQueue();self.store=manuals();self.clock=Clock()

    def tearDown(self):
        self.jobs.close();self.queue.close();self.store.close()

    def submit(self, **options):
        return self.jobs.submit(ALICE,'key',payload(),0,**options)['job_id']

    def start(self):
        jid=self.submit();return jid,self.jobs.claim(jid,'a',0)

    def finish_job(self):
        jid=self.submit();self.jobs.relay(self.queue,0)
        work_once(self.jobs,self.queue,self.store,self.clock);return jid

    def count(self,table):
        assert table in {'jobs','dispatch_outbox','checkpoints','job_results','dead_letters'}
        return self.jobs.db.execute('SELECT count(*) FROM '+table).fetchone()[0]

    def test_acceptance_is_durable_intent_not_success(self):
        jid=self.submit()
        self.assertEqual((self.jobs.job(jid)['state'],self.count('dispatch_outbox')),('queued',1))
        self.assertEqual(self.count('job_results'),0)

    def test_repeat_returns_same_job_without_extending_deadline(self):
        jid=self.submit()
        replay=self.jobs.submit(ALICE,'key',payload(),1900,validity_ms=9999)
        self.assertEqual((jid,replay['status'],replay['replay']),(replay['job_id'],200,True))
        self.assertEqual(self.jobs.job(jid)['deadline_ms'],2000)

    def test_key_conflict_does_not_create_second_job(self):
        self.submit()
        with self.assertRaises(IdempotencyConflict):
            self.jobs.submit(ALICE,'key',payload('en-US'),0)
        self.assertEqual(self.count('jobs'),1)

    def test_fingerprint_object_order_stable_document_order_significant(self):
        a=payload();b={'documents':a['documents'],'language':a['language']}
        self.assertEqual(request_fingerprint(a),request_fingerprint(b))
        b['documents']=list(reversed(b['documents']))
        self.assertNotEqual(request_fingerprint(a),request_fingerprint(b))

    def test_key_scope_is_tenant_and_principal(self):
        ids={self.jobs.submit(actor,'same',payload(),0)['job_id'] for actor in (ALICE,ADMIN,BOB)}
        self.assertEqual(len(ids),3)

    def test_distinct_intent_keys_are_not_content_deduplication(self):
        a=self.submit();b=self.jobs.submit(ALICE,'another',payload(),0)['job_id']
        self.assertNotEqual(a,b)

    def test_invalid_payload_never_creates_job(self):
        for p in ({}, {'language':'fr','documents':['a','b']},
                  {'language':'pt-BR','documents':['a','a']},
                  {**payload(),'tenant':'injected'}):
            with self.assertRaises(ValueError):self.jobs.submit(ALICE,'key',p,0)
        self.assertEqual(self.count('jobs'),0)

    def test_invalid_time_and_key_rejected(self):
        for key in ('',123,'a'*101):
            with self.assertRaises(ValueError):self.jobs.submit(ALICE,key,payload(),0)
        with self.assertRaises(ValueError):self.submit(validity_ms=True)

    def test_acceptance_transaction_rolls_back_job_and_outbox(self):
        with self.assertRaises(Crash):self.submit(crash_before_commit=True)
        self.assertEqual((self.count('jobs'),self.count('dispatch_outbox')),(0,0))

    def test_outbox_can_publish_twice_without_duplicate_result(self):
        self.assertEqual(exercise19(),dict(jobs=1,deliveries=2,result_rows=1,pending=0))

    def test_no_message_before_relay(self):
        self.submit();self.assertIsNone(self.queue.receive(0))
        self.assertEqual(self.jobs.relay(self.queue,0),1)

    def test_queue_visibility_boundary_and_old_receipt(self):
        self.queue.publish(1,1,0);old=self.queue.receive(0)
        self.assertIsNone(self.queue.receive(99))
        new=self.queue.receive(100)
        self.assertFalse(self.queue.ack(old,100))
        self.assertTrue(self.queue.ack(new,100))
        self.assertFalse(self.queue.ack(new,100))

    def test_ack_at_expiry_is_rejected(self):
        self.queue.publish(1,1,0);r=self.queue.receive(0)
        self.assertFalse(self.queue.ack(r,100))

    def test_live_job_lease_blocks_duplicate_worker(self):
        jid,lease=self.start()
        self.assertIsNone(self.jobs.claim(jid,'b',99))
        self.assertEqual(self.jobs.job(jid)['attempts'],1)

    def test_reclaim_at_lease_boundary_fences_old_worker(self):
        jid,old=self.start();new=self.jobs.claim(jid,'b',100)
        self.assertGreater(new.generation,old.generation)
        with self.assertRaises(LeaseLost):self.jobs.checkpoint(old,0,{},100)
        with self.assertRaises(LeaseLost):self.jobs.heartbeat(old,100)

    def test_heartbeat_cannot_extend_beyond_job_deadline(self):
        jid=self.submit(validity_ms=150);lease=self.jobs.claim(jid,'a',0)
        self.jobs.heartbeat(lease,90,lease_ms=500)
        self.assertEqual(self.jobs.job(jid)['lease_until'],150)

    def test_expired_lease_cannot_be_renewed(self):
        _,lease=self.start()
        with self.assertRaises(LeaseLost):self.jobs.heartbeat(lease,100)

    def test_checkpoint_and_progress_commit_together(self):
        jid,lease=self.start()
        with self.assertRaises(Crash):self.jobs.checkpoint(lease,0,{'a':1},10,crash=True)
        self.assertEqual((self.jobs.job(jid)['stage'],self.count('checkpoints')),(0,0))

    def test_checkpoint_sequence_cannot_skip_or_repeat(self):
        jid,lease=self.start()
        with self.assertRaises(ValueError):self.jobs.checkpoint(lease,1,{},10)
        self.jobs.checkpoint(lease,0,{},10)
        with self.assertRaises(ValueError):self.jobs.checkpoint(lease,0,{},11)
        self.assertEqual(self.jobs.job(jid)['stage'],1)

    def test_completion_requires_two_checkpoints(self):
        _,lease=self.start()
        with self.assertRaises(ValueError):self.jobs.complete(lease,{},10)

    def test_result_and_terminal_state_rollback_together(self):
        jid,lease=self.start()
        for pos in range(2):self.jobs.checkpoint(lease,pos,{},10)
        with self.assertRaises(Crash):self.jobs.complete(lease,{},20,crash=True)
        self.assertEqual((self.count('job_results'),self.jobs.job(jid)['state']),(0,'running'))
        self.jobs.complete(lease,{},21)
        self.assertEqual(self.count('job_results'),1)

    def test_stale_worker_cannot_publish_result(self):
        jid,old=self.start()
        for pos in range(2):self.jobs.checkpoint(old,pos,{},10)
        self.jobs.claim(jid,'b',100)
        with self.assertRaises(LeaseLost):self.jobs.complete(old,{},100)

    def test_restart_in_new_process_resumes_committed_checkpoint(self):
        r=restart_case()
        self.assertEqual((r['checkpoint_at_stop'],r['attempts'],r['virtual_ms']),(1,2,110))
        self.assertEqual(r['process_exits'],[75,0])

    def test_restart_after_result_commit_does_not_recompute(self):
        r=restart_case(crash_at='result')
        self.assertEqual((r['attempts'],r['result_rows'],r['pending']),(1,1,0))

    def test_retry_wait_not_admitted_early(self):
        jid,lease=self.start();self.jobs.fail(lease,0)
        self.assertIsNone(self.jobs.claim(jid,'b',199))
        self.assertIsNotNone(self.jobs.claim(jid,'b',200))

    def test_three_transient_attempts_quarantined(self):
        r=run_case('dead_letter')
        self.assertEqual((r['state'],r['attempts'],r['result_rows']),('failed',3,0))

    def test_dead_letter_contains_code_not_exception_text(self):
        jid,lease=self.start();self.jobs.fail(lease,0,transient=False)
        row=dict(self.jobs.db.execute('SELECT * FROM dead_letters').fetchone())
        self.assertEqual(row,dict(job_id=jid,reason='source_changed',attempts=1))

    def test_repeated_worker_crashes_eventually_stop(self):
        jid=self.submit()
        for now in (0,100,200):self.assertIsNotNone(self.jobs.claim(jid,'w',now))
        self.assertIsNone(self.jobs.claim(jid,'w',300))
        self.assertEqual(self.jobs.job(jid)['state'],'failed')

    def test_retry_delay_beyond_validity_expires(self):
        jid=self.submit(validity_ms=200);lease=self.jobs.claim(jid,'a',0)
        self.jobs.fail(lease,0,delay_ms=200)
        self.assertEqual(self.jobs.job(jid)['state'],'expired')

    def test_waiting_time_consumes_job_validity(self):
        jid=self.submit(validity_ms=20)
        self.assertIsNone(self.jobs.claim(jid,'a',20))
        self.assertEqual((self.jobs.job(jid)['state'],self.jobs.job(jid)['attempts']),('expired',0))

    def test_deadline_during_work_prevents_publication(self):
        jid=self.submit(validity_ms=15);self.jobs.relay(self.queue,0)
        self.assertEqual(work_once(self.jobs,self.queue,self.store,self.clock),'lease_lost')
        self.assertEqual((self.jobs.job(jid)['state'],self.count('job_results')),('expired',0))

    def test_cancel_pending_prevents_claim(self):
        jid=self.submit();self.assertTrue(self.jobs.cancel(ALICE,jid))
        self.assertIsNone(self.jobs.claim(jid,'a',0))

    def test_cancel_running_invalidates_worker(self):
        jid,lease=self.start();self.jobs.cancel(ALICE,jid)
        with self.assertRaises(LeaseLost):self.jobs.checkpoint(lease,0,{},10)

    def test_cancel_just_before_commit_wins(self):
        jid=self.submit();self.jobs.relay(self.queue,0)
        work_once(self.jobs,self.queue,self.store,self.clock,
                  before_complete=lambda:self.jobs.cancel(ALICE,jid))
        self.assertEqual((self.jobs.job(jid)['state'],self.count('job_results')),('cancelled',0))

    def test_completion_before_cancel_remains_terminal(self):
        jid=self.finish_job();self.assertFalse(self.jobs.cancel(ALICE,jid))
        self.assertEqual(self.jobs.job(jid)['state'],'succeeded')

    def test_other_principal_cannot_poll_or_cancel(self):
        jid=self.submit()
        for actor in (BOB,ADMIN):
            self.assertIsNone(read_job(self.jobs,self.store,actor,jid,0))
            self.assertFalse(self.jobs.cancel(actor,jid))

    def test_unknown_job_has_same_public_absence(self):
        self.assertIsNone(read_job(self.jobs,self.store,ALICE,9999,0))

    def test_permissions_rechecked_before_computation(self):
        jid=self.submit();self.jobs.relay(self.queue,0)
        self.store.set_acl('acme','manual-a',['admin'])
        work_once(self.jobs,self.queue,self.store,self.clock)
        self.assertEqual((self.jobs.job(jid)['state'],self.count('job_results')),('failed',0))

    def test_revocation_after_checkpoint_invalidates_resume(self):
        self.assertEqual(exercise20(),dict(saved_stage=1,state='failed',result=None))

    def test_revoke_after_success_hides_stored_result(self):
        jid=self.finish_job();self.store.set_acl('acme','manual-a',['admin'])
        view=read_job(self.jobs,self.store,ALICE,jid,20)
        self.assertEqual((view['state'],view['result_access'],view['result']),('succeeded','unavailable',None))

    def test_source_version_change_hides_previous_result(self):
        jid=self.finish_job()
        ingest(self.store,'manual-a','Devolução: prazo de 90 dias. Postagem: despacho em 3 dias.',
               'Returns: window of 90 days. Shipping: dispatch in 3 days.',expected=1)
        self.assertIsNone(read_job(self.jobs,self.store,ALICE,jid,20)['result'])

    def test_bilingual_comparison_facts_and_citations(self):
        for lang in ('pt-BR','en-US'):
            values=[capture(self.store,ALICE,doc,lang) for doc in payload()['documents']]
            result=compare(values)
            self.assertEqual([(r['left'],r['right'],r['delta'],r['same']) for r in result['rows']],
                             [(45,30,-15,False),(3,3,0,True)])

    def test_final_result_uses_public_sources_not_identity_snapshot(self):
        jid=self.finish_job();view=read_job(self.jobs,self.store,ALICE,jid,20)
        raw=json.dumps(view)
        self.assertNotIn('fingerprint',raw);self.assertNotIn('subject',raw)
        self.assertNotIn('snapshot',raw)
        self.assertEqual(len(view['result']['sources']),2)

    def test_simultaneous_submissions_converge_on_one_job(self):
        with scratch_directory() as folder:
            path=folder/'jobs.db';db=Jobs(path);db.close();barrier=Barrier(2)
            def submit(_):
                other=Jobs(path)
                try:
                    barrier.wait(timeout=5)
                    return other.submit(ALICE,'one',payload(),0)['job_id']
                finally:other.close()
            with ThreadPoolExecutor(max_workers=2) as pool:
                ids=list(pool.map(submit,range(2)))
            self.assertEqual(ids[0],ids[1])

    def test_simultaneous_claims_admit_one_worker(self):
        with scratch_directory() as folder:
            path=folder/'jobs.db';db=Jobs(path)
            jid=db.submit(ALICE,'one',payload(),0)['job_id'];db.close();barrier=Barrier(2)
            def claim(i):
                other=Jobs(path)
                try:
                    barrier.wait(timeout=5)
                    return other.claim(jid,str(i),0)
                finally:other.close()
            with ThreadPoolExecutor(max_workers=2) as pool:
                leases=list(pool.map(claim,range(2)))
            self.assertEqual(sum(lease is not None for lease in leases),1)


if __name__=='__main__':unittest.main()
