import copy
import json
from pathlib import Path
import tempfile
from contextlib import contextmanager
import shutil
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event
import unittest
from dataclasses import asdict
from cache_cost import (AnswerCache, Ledger, Gate, answer_key, snapshot,
                        execute, cached_valid, reusable)
from cache_scenarios import UnknownAdapter, revise, cohort, run_scenarios
from cache_exercises import exercise23, exercise24
from fixtures import ALICE, ADMIN, BOB, ingest
from job_worker import manuals
from routing import RoutePolicy, SimulatedModels, Reply


@contextmanager
def scratch_directory():
    root=(Path(__file__).resolve().parent/'scratch').resolve()
    folder=root/('cache-'+uuid.uuid4().hex)
    folder.mkdir(parents=True)
    try:yield str(folder)
    finally:
        assert folder.resolve().is_relative_to(root) and folder!=root
        shutil.rmtree(folder)


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.store=manuals();self.cache=AnswerCache();self.ledger=Ledger()
        self.ledger.configure('acme',1000);self.gate=Gate();self.seq=0
    def tearDown(self):
        self.store.close();self.cache.close();self.ledger.close()
    def run_request(self,actor=ALICE,**kw):
        self.seq+=1;task=kw.pop('task',str(self.seq))
        return execute(self.store,actor,self.cache,self.ledger,self.gate,task,**kw)
    def test_cold_complete(self):
        r=self.run_request();self.assertEqual((r['state'],r['task_units'],r['model_calls']),('full',24,1))
    def test_hot_new_task_cost(self):
        self.run_request();r=self.run_request()
        self.assertEqual((r['cache_hit'],r['model_calls'],r['task_units']),(True,0,4))
    def test_cache_contains_no_request_metering(self):
        self.run_request();body=self.cache.db.execute('SELECT body FROM answers').fetchone()[0]
        self.assertEqual(set(json.loads(body)),{'rows','sources','model'})
    def test_user_isolation(self):
        self.run_request();self.assertFalse(self.run_request(ADMIN)['cache_hit'])
    def test_tenant_isolation(self):
        self.run_request();r=self.run_request(BOB)
        self.assertEqual((r['state'],r['payload']),('abstain',None))
    def test_language_isolation(self):
        self.run_request();r=self.run_request(language='en-US')
        self.assertFalse(r['cache_hit']);self.assertIn('Returns',r['payload']['sources'][0]['quotes'][0])
    def test_ordered_documents(self):
        self.run_request();r=self.run_request(documents=('manual-b','manual-a'))
        self.assertFalse(r['cache_hit']);self.assertEqual(r['payload']['rows'][0]['delta'],15)
    def test_prompt_version(self):
        self.run_request();self.assertFalse(self.run_request(prompt='compare-v2')['cache_hit'])
    def test_route_policy_versioned(self):
        self.run_request();self.assertFalse(self.run_request(policy=RoutePolicy(max_calls=1))['cache_hit'])
    def test_source_revision(self):
        self.run_request();revise(self.store);r=self.run_request()
        self.assertFalse(r['cache_hit']);self.assertEqual(r['payload']['rows'][0]['delta'],-30)
    def test_revoked_before_lookup(self):
        self.run_request();self.store.set_acl('acme','manual-a',['admin'])
        self.assertEqual(self.run_request()['reason'],'access')
    def test_revoked_during_hit(self):
        self.run_request()
        r=self.run_request(after_lookup=lambda:self.store.set_acl('acme','manual-a',['admin']))
        self.assertEqual((r['reason'],r['payload']),('source_changed',None))
    def test_source_change_during_hit(self):
        self.run_request();r=self.run_request(after_lookup=lambda:revise(self.store))
        self.assertEqual((r['reason'],r['payload']),('source_changed',None))
    def test_revoke_during_generation(self):
        a=SimulatedModels(after_call=lambda _:self.store.set_acl('acme','manual-a',['admin']))
        r=self.run_request(adapter=a)
        self.assertEqual((r['state'],r['task_units'],r['payload']),('abstain',24,None))
        self.assertEqual(self.cache.db.execute('SELECT count(*) FROM answers').fetchone()[0],0)
    def test_exact_expiration(self):
        self.run_request(now=10,ttl=10)
        self.assertTrue(self.run_request(now=19)['cache_hit'])
        self.assertFalse(self.run_request(now=20)['cache_hit'])
    def test_partial_not_reused(self):
        for i in range(2):
            r=self.run_request(policy=RoutePolicy(max_units=20),adapter=SimulatedModels({'compact':Reply('partial')}))
            self.assertEqual((r['state'],r['model_calls']),('partial',1))
    def test_refusal_not_reused(self):
        self.run_request(adapter=SimulatedModels({'compact':Reply('refusal')}))
        self.assertEqual(self.run_request()['model_calls'],1)
    def test_corrupt_json_miss(self):
        self.run_request();self.cache.db.execute("UPDATE answers SET body='invalid'")
        self.assertEqual(self.run_request()['model_calls'],1)
    def test_tampered_fact_miss(self):
        r=self.run_request();p=r['payload'];p['rows'][0]['delta']=999
        self.cache.db.execute('UPDATE answers SET body=?',(json.dumps(p),))
        self.assertEqual(self.run_request()['payload']['rows'][0]['delta'],-15)
    def test_tampered_source_miss(self):
        r=self.run_request();p=r['payload'];p['sources'][0]['source']='forged'
        self.cache.db.execute('UPDATE answers SET body=?',(json.dumps(p),))
        self.assertEqual(self.run_request()['model_calls'],1)
    def test_known_timeout_counts_both_attempts(self):
        r=self.run_request(adapter=SimulatedModels({'compact':Reply(elapsed_ms=500)}))
        self.assertEqual((r['state'],r['task_units'],r['model_calls']),('full',94,2))
    def test_unknown_retains_reservation(self):
        r=self.run_request(adapter=UnknownAdapter())
        self.assertEqual((r['reason'],r['held_units']),('cost_unknown',94))
        self.assertEqual(self.ledger.balance('acme')['held'],94)
    def test_unknown_releases_local_capacity_only(self):
        self.run_request(adapter=UnknownAdapter());self.assertEqual(self.gate.active,set())
        self.assertEqual(self.ledger.balance('acme')['available'],906)
    def test_duplicate_task_never_reexecutes(self):
        self.run_request(task='same');r=self.run_request(task='same')
        self.assertEqual((r['reason'],r['payload']),('duplicate',None))
        self.assertEqual(self.ledger.balance('acme')['spent'],24)
    def test_task_reuse_changed_payload_conflicts(self):
        self.run_request(task='same');r=self.run_request(task='same',prompt='v2')
        self.assertEqual(r['reason'],'conflict')
    def test_coalescing_deferred_without_nested_provider_call(self):
        nested=[]
        a=SimulatedModels(after_call=lambda _:nested.append(self.run_request()))
        self.run_request(adapter=a)
        self.assertEqual((nested[0]['reason'],a.calls),('in_flight',['compact']))
    def test_capacity_denial_has_no_admitted_charge(self):
        self.gate.enter('a');self.gate.enter('b');r=self.run_request()
        self.assertEqual((r['reason'],self.ledger.balance('acme')['spent']),('capacity',0))
    def test_fingerprints_no_source_body(self):
        saved=snapshot(self.store,ALICE,('manual-a','manual-b'),'pt-BR')
        self.assertTrue(all('body' not in s['snapshot'] for s in saved))
        a=answer_key(ALICE,saved,'pt-BR',{'a':1,'b':2})
        b=answer_key(ALICE,saved,'pt-BR',{'b':2,'a':1})
        self.assertEqual(a,b);self.assertEqual(len(a),64)
    def test_invalid_input_precedes_execution(self):
        for kw in (dict(language='fr'),dict(documents=('manual-a','manual-a')),dict(ttl=0),dict(now=True)):
            with self.subTest(kw=kw),self.assertRaises(ValueError):self.run_request(**kw)


class StorageTests(unittest.TestCase):
    def test_cache_capacity_eviction(self):
        c=AnswerCache(max_entries=2)
        try:
            for i in range(3):c.put(str(i),{'n':i},i,100)
            self.assertIsNone(c.get('0',3));self.assertEqual(c.get('2',3),{'n':2})
        finally:c.close()
    def test_oversize_not_written(self):
        c=AnswerCache(max_bytes=4)
        try:self.assertFalse(c.put('a',{'large':'value'},0,10));self.assertIsNone(c.get('a',0))
        finally:c.close()
    def test_cache_persists_and_expires(self):
        with scratch_directory() as d:
            p=str(Path(d)/'cache.db');c=AnswerCache(p);c.put('a',{'n':1},10,10);c.close()
            c=AnswerCache(p)
            try:self.assertEqual(c.get('a',19),{'n':1});self.assertIsNone(c.get('a',20))
            finally:c.close()
    def test_bad_cached_shapes(self):
        s=manuals()
        try:
            saved=snapshot(s,ALICE,('manual-a','manual-b'),'pt-BR')
            for p in (None,[],{},dict(rows=[],sources=[],model='compact')):
                self.assertFalse(cached_valid(p,saved))
        finally:s.close()


class LedgerTests(unittest.TestCase):
    def setUp(self):self.l=Ledger();self.l.configure('acme',200)
    def tearDown(self):self.l.close()
    def test_exact_cap(self):
        self.assertEqual(self.l.reserve('acme','a','key',200),'admitted')
        self.assertEqual(self.l.reserve('acme','b','key',1),'budget')
    def test_partial_release(self):
        self.l.reserve('acme','a','key',94);self.l.settle('acme','a',24)
        self.assertEqual(self.l.balance('acme'),dict(cap=200,spent=24,held=0,available=176))
    def test_duplicate_reservation(self):
        self.l.reserve('acme','a','key',94)
        self.assertEqual(self.l.reserve('acme','a','key',94),'duplicate')
        self.assertEqual(self.l.balance('acme')['held'],94)
    def test_reservation_conflict(self):
        self.l.reserve('acme','a','key',94)
        self.assertEqual(self.l.reserve('acme','a','other',94),'conflict')
    def test_settlement_replay(self):
        self.l.reserve('acme','a','key',94)
        for _ in range(2):self.l.settle('acme','a',24)
        self.assertEqual(self.l.balance('acme')['spent'],24)
    def test_conflicting_settlement_rejected(self):
        self.l.reserve('acme','a','key',94);self.l.settle('acme','a',24)
        with self.assertRaises(ValueError):self.l.settle('acme','a',25)
        self.assertEqual(self.l.balance('acme')['spent'],24)
    def test_over_reservation_settlement_rejected(self):
        self.l.reserve('acme','a','key',94)
        with self.assertRaises(ValueError):self.l.settle('acme','a',95)
        self.assertEqual(self.l.balance('acme')['held'],94)
    def test_unknown_not_freed(self):
        self.l.reserve('acme','a','key',94);self.l.uncertain('acme','a')
        self.assertEqual(self.l.balance('acme')['held'],94)
    def test_reconciliation(self):
        self.l.reserve('acme','a','key',94);self.l.uncertain('acme','a');self.l.settle('acme','a',74)
        self.assertEqual(self.l.balance('acme'),dict(cap=200,spent=74,held=0,available=126))
    def test_cannot_mark_settled_unknown(self):
        self.l.reserve('acme','a','key',94);self.l.settle('acme','a',24)
        with self.assertRaises(ValueError):self.l.uncertain('acme','a')
    def test_tenant_budget_independent(self):
        self.l.configure('zen',20);self.l.reserve('acme','a','k',200)
        self.assertEqual(self.l.reserve('zen','a','k',20),'admitted')
    def test_limits_immutable_during_run(self):
        with self.assertRaises(ValueError):self.l.configure('acme',201)
        self.assertEqual(self.l.balance('acme')['cap'],200)
    def test_unknown_tenant_and_task(self):
        with self.assertRaises(ValueError):self.l.reserve('missing','a','k',1)
        with self.assertRaises(ValueError):self.l.settle('acme','missing',0)
    def test_invalid_numeric_types(self):
        for n in (-1,True,1.5):
            with self.subTest(n=n),self.assertRaises(ValueError):self.l.reserve('acme','a','k',n)
    def test_persisted_unknown_survives_reopen(self):
        with scratch_directory() as d:
            p=str(Path(d)/'ledger.db');l=Ledger(p);l.configure('x',100)
            l.reserve('x','a','k',94);l.uncertain('x','a');l.close();l=Ledger(p)
            try:self.assertEqual(l.balance('x')['held'],94);self.assertEqual(l.reserve('x','b','j',94),'budget')
            finally:l.close()
    def test_simultaneous_connections_cannot_overspend(self):
        with scratch_directory() as d:
            p=str(Path(d)/'ledger.db');l=Ledger(p);l.configure('x',100);l.close();barrier=Barrier(2)
            def worker(i):
                ledger=Ledger(p)
                try:barrier.wait(timeout=5);return ledger.reserve('x',str(i),str(i),94)
                finally:ledger.close()
            with ThreadPoolExecutor(max_workers=2) as pool:answers=list(pool.map(worker,range(2)))
            self.assertCountEqual(answers,['admitted','budget']);l=Ledger(p)
            try:self.assertEqual(l.balance('x')['held'],94)
            finally:l.close()


class GateAndReportTests(unittest.TestCase):
    def test_simultaneous_same_key_one_winner(self):
        gate=Gate(8);barrier=Barrier(4)
        def enter(_):barrier.wait(timeout=5);return gate.enter('same')
        with ThreadPoolExecutor(max_workers=4) as pool:answers=list(pool.map(enter,range(4)))
        self.assertEqual(answers.count('admitted'),1);self.assertEqual(answers.count('in_flight'),3)
    def test_simultaneous_different_keys_bounded(self):
        gate=Gate(2);barrier=Barrier(4)
        def enter(i):barrier.wait(timeout=5);return gate.enter(str(i))
        with ThreadPoolExecutor(max_workers=4) as pool:answers=list(pool.map(enter,range(4)))
        self.assertEqual(answers.count('admitted'),2);self.assertEqual(len(gate.active),2)
    def test_capacity_restored_after_work(self):
        g=Gate(1);g.enter('a');self.assertEqual(g.enter('b'),'capacity');g.leave('a')
        self.assertEqual(g.enter('b'),'admitted')
    def test_cohort_arithmetic(self):
        r=cohort();self.assertEqual(r['without_cache']['units'],240)
        self.assertEqual(r['with_cache']['units'],60);self.assertEqual(r['with_cache']['hits'],9)
    def test_exercise23(self):
        self.assertEqual(exercise23(),{'states':['full','full','abstain'],'calls':[1,0,0],'spent':28})
    def test_exercise24(self):
        r=exercise24();self.assertEqual(r['before'],dict(cap=200,spent=24,held=94,available=82))
        self.assertEqual(r['after'],dict(cap=200,spent=98,held=0,available=102))
    def test_bilingual_scenario_equivalence(self):
        r=run_scenarios();self.assertEqual(r['cases'],28)
        for a,b in zip(r['runs'][:14],r['runs'][14:]):
            self.assertEqual({k:v for k,v in a.items() if k!='language'},
                             {k:v for k,v in b.items() if k!='language'})


if __name__=='__main__':unittest.main()
