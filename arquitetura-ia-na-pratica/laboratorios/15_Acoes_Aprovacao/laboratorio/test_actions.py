import copy,json,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from base.store import Actor
from fixtures import ALICE,BOB,ingest
from actions import *
from action_scenarios import fixture,approve,DRAFT,REVIEWER,run_case,run_scenarios,SCRATCH
from action_exercises import exercise29,exercise30


class ActionTests(unittest.TestCase):
    def setUp(self):self.store,self.s,self.d=fixture()
    def tearDown(self):self.s.close();self.d.close();self.store.close()
    def new(self,**kw):return self.s.propose(ALICE,DRAFT,**kw)
    def ready(self):
        id=self.new();approve(self.s,id);return id
    def test_propose_has_no_effect(self):
        id=self.new();self.assertEqual(self.s.row(id)['state'],'pending');self.assertEqual(self.d.count(),0)
    def test_preview_facts(self):
        v=self.s.preview(REVIEWER,self.new());self.assertIn('45 -> 30',v['action']['body']);self.assertEqual(v['action']['project'],'ops')
    def test_success(self):
        id=self.ready();self.assertEqual(self.s.dispatch(id,self.d),'succeeded');self.assertEqual(self.d.count(),1)
    def test_pending_cannot_execute(self):
        self.assertEqual(self.s.dispatch(self.new(),self.d),'pending');self.assertEqual(self.d.calls,0)
    def test_duplicate_dispatch(self):
        id=self.ready();self.s.dispatch(id,self.d);self.s.dispatch(id,self.d);self.assertEqual(self.d.calls,1)
    def test_duplicate_decision(self):
        id=self.ready()
        with self.assertRaisesRegex(Denied,'state'):approve(self.s,id)
    def test_reject_terminal(self):
        id=self.new();self.s.decide(REVIEWER,id,self.s.row(id)['hash'],False)
        self.assertEqual(self.s.dispatch(id,self.d),'rejected');self.assertEqual(self.d.calls,0)
    def test_cancel_pending(self):
        self.assertEqual(self.s.cancel(ALICE,self.new()),'cancelled')
    def test_cancel_approved(self):
        id=self.ready();self.s.cancel(ALICE,id);self.assertEqual(self.s.dispatch(id,self.d),'cancelled')
    def test_cancel_unknown_too_late(self):
        id=self.ready();self.s.dispatch(id,self.d,fault='after')
        with self.assertRaisesRegex(Denied,'too_late'):self.s.cancel(ALICE,id)
    def test_cancel_wrong_actor(self):
        with self.assertRaises(Denied):self.s.cancel(BOB,self.new())
    def test_self_approval(self):
        id=self.new();self.s.grant(ALICE,'reviewer')
        with self.assertRaisesRegex(Denied,'reviewer'):self.s.decide(ALICE,id,self.s.row(id)['hash'],True)
    def test_wrong_tenant_reviewer(self):
        bob=Actor('zen','carol');self.s.grant(bob,'reviewer');id=self.new()
        with self.assertRaises(Denied):self.s.decide(bob,id,self.s.row(id)['hash'],True)
    def test_viewer_isolation(self):
        with self.assertRaises(Denied):self.s.preview(BOB,self.new())
    def test_requester_own_preview(self):
        self.assertEqual(self.s.preview(ALICE,self.new())['state'],'pending')
    def test_wrong_hash(self):
        with self.assertRaisesRegex(Denied,'preview_mismatch'):self.s.decide(REVIEWER,self.new(),'bad',True)
    def test_decision_bool(self):
        with self.assertRaisesRegex(Denied,'decision'):self.s.decide(REVIEWER,self.new(),'bad',1)
    def test_approval_at_expiry(self):
        id=self.new()
        with self.assertRaisesRegex(Denied,'expired'):approve(self.s,id,30)
    def test_execution_at_expiry(self):
        id=self.ready();self.assertEqual(self.s.dispatch(id,self.d,30),'expired');self.assertEqual(self.d.calls,0)
    def test_just_before_expiry(self):
        self.assertEqual(self.s.dispatch(self.ready(),self.d,29),'succeeded')
    def test_requester_revoke(self):
        id=self.ready();self.s.grant(ALICE,'requester',False);self.assertEqual(self.s.dispatch(id,self.d),'invalidated')
    def test_reviewer_revoke(self):
        id=self.ready();self.s.grant(REVIEWER,'reviewer',False);self.s.dispatch(id,self.d)
        self.assertEqual(self.s.row(id)['reason'],'reviewer_revoked');self.assertEqual(self.d.calls,0)
    def test_source_revoke(self):
        id=self.ready();self.store.set_acl('acme','manual-a',['admin']);self.s.dispatch(id,self.d)
        self.assertEqual(self.s.row(id)['reason'],'stale');self.assertEqual(self.d.calls,0)
    def test_source_revised(self):
        self.assertEqual(run_case('revised')['reason'],'stale')
    def test_preview_after_revoke(self):
        id=self.new();self.store.set_acl('acme','manual-a',['admin'])
        with self.assertRaisesRegex(Denied,'stale'):self.s.preview(REVIEWER,id)
    def test_tamper_packet(self):
        id=self.ready();packet=json.loads(self.s.row(id)['packet']);packet['payload']['project']='other'
        self.s.db.execute('UPDATE intents SET packet=? WHERE id=?',(canonical(packet),id))
        self.s.dispatch(id,self.d);self.assertEqual(self.s.row(id)['reason'],'integrity');self.assertEqual(self.d.calls,0)
    def test_approved_hash_tamper(self):
        id=self.ready();self.s.db.execute('UPDATE intents SET approved_hash=? WHERE id=?',('bad',id))
        self.s.dispatch(id,self.d);self.assertEqual(self.s.row(id)['reason'],'approval_mismatch')
    def test_after_timeout_unknown(self):
        id=self.ready();self.assertEqual(self.s.dispatch(id,self.d,fault='after'),'unknown');self.assertEqual(self.d.count(),1)
    def test_before_timeout_unknown(self):
        id=self.ready();self.assertEqual(self.s.dispatch(id,self.d,fault='before'),'unknown');self.assertEqual(self.d.count(),0)
    def test_reconcile_no_resend(self):
        id=self.ready();self.s.dispatch(id,self.d,fault='after');self.s.reconcile(id,self.d)
        self.assertEqual((self.d.calls,self.d.lookups,self.d.count()),(1,1,1))
    def test_retry_after_absent(self):
        id=self.ready();self.s.dispatch(id,self.d,fault='before');self.s.reconcile(id,self.d,retry=True)
        self.assertEqual((self.d.calls,self.d.count()),(2,1))
    def test_no_retry_by_default(self):
        id=self.ready();self.s.dispatch(id,self.d,fault='before');self.s.reconcile(id,self.d)
        self.assertEqual((self.d.calls,self.s.row(id)['state']),(1,'unknown'))
    def test_retry_expired_stays_unknown(self):
        id=self.ready();self.s.dispatch(id,self.d,fault='before');self.s.reconcile(id,self.d,30,retry=True)
        self.assertEqual((self.d.calls,self.s.row(id)['state'],self.s.row(id)['reason']),(1,'unknown','expired'))
    def test_retry_revoked_stays_unknown(self):
        id=self.ready();self.s.dispatch(id,self.d,fault='before');self.s.grant(REVIEWER,'reviewer',False)
        self.s.reconcile(id,self.d,retry=True);self.assertEqual(self.d.calls,1);self.assertEqual(self.s.row(id)['state'],'unknown')
    def test_receipt_despite_expiry_revoke(self):
        self.assertEqual(exercise30(),{'before':'unknown','after':'succeeded','effects':1,'create_calls':1,'lookups':1,'reason':'reconciled'})
    def test_lookup_failure_stays_unknown(self):
        id=self.ready();self.s.dispatch(id,self.d,fault='after')
        class Offline:
            def lookup(self,*a):raise TimeoutError()
        self.assertEqual(self.s.reconcile(id,Offline(),retry=True),'unknown')
    def test_destination_reject(self):
        id=self.ready();self.assertEqual(self.s.dispatch(id,self.d,fault='reject'),'rejected');self.assertEqual(self.d.count(),0)
    def test_adapter_error_ambiguous(self):
        class Broken:
            def create(self,*a):raise RuntimeError('sensitive internal error')
        id=self.ready();self.s.dispatch(id,Broken());self.assertEqual(self.s.row(id)['reason'],'ambiguous')
    def test_restart_before(self):
        r=run_case('crash_before');self.assertEqual((r['state'],r['effects'],r['attempts'],r['create_calls']),('succeeded',1,2,1))
    def test_restart_after(self):
        r=run_case('restart_after');self.assertEqual((r['state'],r['effects'],r['attempts'],r['create_calls']),('succeeded',1,1,1))
    def test_claim_not_lease(self):
        id=self.ready();self.assertIsNotNone(self.s.claim(id,2));self.assertIsNone(self.s.claim(id,3));self.assertEqual(self.s.row(id)['state'],'dispatching')
    def test_recovery_only_dispatching(self):
        id=self.new();self.assertEqual(self.s.recover(id),'pending')
    def test_attempt_cap(self):
        r=run_case('attempt_limit');self.assertEqual((r['state'],r['reason'],r['create_calls'],r['effects']),('unknown','attempt_limit',2,0))
    def test_provider_same_key(self):
        payload={'x':1};a=self.d.create('a','k',payload);b=self.d.create('a','k',payload)
        self.assertEqual(a,b);self.assertEqual(self.d.count(),1)
    def test_provider_payload_conflict(self):
        self.d.create('a','k',{'x':1})
        with self.assertRaisesRegex(Denied,'key_conflict'):self.d.create('a','k',{'x':2})
        self.assertEqual(self.d.count(),1)
    def test_provider_tenant_scoped(self):
        self.d.create('a','k',{});self.d.create('b','k',{});self.assertEqual(self.d.count(),2)
    def test_provider_key_durability(self):
        with TemporaryDirectory(dir=SCRATCH) as p:
            path=Path(p)/'d.db';d=TaskDestination(path);receipt=d.create('a','k',{});d.close()
            d=TaskDestination(path)
            try:self.assertEqual(d.create('a','k',{}),receipt);self.assertEqual(d.count(),1)
            finally:d.close()
    def test_audit_no_content(self):
        id=self.ready();self.s.dispatch(id,self.d);events=self.s.events(id)
        self.assertEqual([e['event'] for e in events],['pending','approved','dispatching','succeeded'])
        self.assertNotIn('45',json.dumps(events));self.assertNotIn('source',json.dumps(events))
    def test_intent_identity(self):
        self.assertEqual(exercise29(),{'same_payload_hash':True,'unapproved_state':'pending','wrong_preview':'preview_mismatch','effects':1})
    def test_translation_parity(self):
        r=run_scenarios();self.assertEqual(r['cases'],36)
        for a,b in zip(r['runs'][:18],r['runs'][18:]):self.assertEqual({k:v for k,v in a.items() if k!='language'},{k:v for k,v in b.items() if k!='language'})
    def test_incomplete_evidence(self):
        self.store.set_acl('acme','manual-a',['admin'])
        with self.assertRaisesRegex(Denied,'evidence'):self.new()
    def test_unchanged_topic(self):
        raw=json.dumps({'tool':'prepare_task','project':'ops','topic':'shipping'})
        with self.assertRaisesRegex(Denied,'no_change'):self.s.propose(ALICE,raw)
    def test_unknown_requester(self):
        with self.assertRaisesRegex(Denied,'requester'):self.s.propose(BOB,DRAFT)
    def test_bad_ttl(self):
        for ttl in (0,-1,3601,True,1.2):
            with self.assertRaises(Denied):self.new(ttl=ttl)
    def test_bad_now(self):
        for now in (-1,True,1.2):
            with self.assertRaises(Denied):self.new(now=now)
    def test_clock_backwards(self):
        id=self.new(now=10)
        with self.assertRaisesRegex(Denied,'clock'):self.s.cancel(ALICE,id,9)
        approve(self.s,id,20)
        with self.assertRaisesRegex(Denied,'clock'):self.s.dispatch(id,self.d,19)
    def test_schema_negative_matrix(self):
        invalid=[None,[],1,'[]','null','{}','not json','"text"','x'*513,
            '{"tool":"prepare_task","tool":"prepare_task","project":"ops","topic":"returns"}']
        for raw in invalid:
            with self.assertRaises(Denied):parse_draft(raw)
    def test_schema_extra_authority(self):
        for key,value in [('approved',True),('tenant','zen'),('url','https://example.com'),('token','secret'),('user','carol')]:
            raw=json.loads(DRAFT);raw[key]=value
            with self.assertRaisesRegex(Denied,'schema'):parse_draft(json.dumps(raw))
    def test_schema_values(self):
        for key,value in [('project','other'),('topic','payroll'),('tool','send'),('topic',[]),('project',None)]:
            raw=json.loads(DRAFT);raw[key]=value
            with self.assertRaises(Denied):parse_draft(json.dumps(raw))
    def test_canonical_order(self):
        self.assertEqual(digest({'b':2,'a':1}),digest({'a':1,'b':2}));self.assertNotEqual(digest({'a':1}),digest({'a':2}))


if __name__=='__main__':unittest.main()
