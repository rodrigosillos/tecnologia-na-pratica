from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
import unittest
from scenarios import ALICE, BOB, new_version, run_scenarios, seeded
from solutions import exercise9, exercise10
from store import Actor, Conflict, Copilot, Store, cache_key

class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.s = seeded()
        self.c = Copilot(self.s)

    def tearDown(self):
        self.s.close()

    def test_01_same_id_two_tenants(self):
        self.assertEqual(self.c.answer(ALICE,'returns')['answer'],'Prazo: 30 dias.')
        self.assertEqual(self.c.answer(BOB,'returns')['answer'],'Prazo: 7 dias.')

    def test_02_no_cross_tenant_membership(self):
        self.assertIsNone(self.s.prepare(Actor('zen','alice'),'returns','pt-BR'))

    def test_03_role_denied_before_generation(self):
        self.assertEqual(self.c.answer(ALICE,'payroll')['status'],'unavailable')
        self.assertEqual(self.c.generations,0)

    def test_04_admin_allowed(self):
        self.assertEqual(self.c.answer(Actor('acme','ana'),'payroll')['status'],'answer')

    def test_05_inactive_member(self):
        self.s.principal('acme','alice','staff',False)
        self.assertIsNone(self.s.prepare(ALICE,'returns','pt-BR'))

    def test_06_empty_acl_denies(self):
        self.s.set_acl('acme','returns',[])
        self.assertIsNone(self.s.prepare(ALICE,'returns','pt-BR'))

    def test_07_language_cache_separation(self):
        self.c.answer(ALICE,'returns')
        en=self.c.answer(ALICE,'returns','en-US')
        self.assertEqual(en['answer'],'Window: 30 days.')
        self.assertFalse(en['cached'])

    def test_08_cache_hit(self):
        self.c.answer(ALICE,'returns')
        self.assertTrue(self.c.answer(ALICE,'returns')['cached'])
        self.assertEqual(self.c.generations,1)

    def test_09_revoke_cached(self):
        self.c.answer(ALICE,'returns')
        self.s.set_acl('acme','returns',['admin'])
        self.assertIsNone(self.c.answer(ALICE,'returns')['answer'])

    def test_10_revoke_between_checks(self):
        reply=self.c.answer(ALICE,'returns',between=lambda:self.s.set_acl('acme','returns',[]))
        self.assertIsNone(reply['answer'])
        self.assertEqual(self.c.generations,1)
        self.assertEqual(len(self.c.cache),0)

    def test_11_new_version_blocks_stale_projection(self):
        new_version(self.s)
        self.assertIsNone(self.s.prepare(ALICE,'returns','pt-BR'))

    def test_12_worker_updates_version(self):
        new_version(self.s);self.s.drain()
        self.assertEqual(self.s.prepare(ALICE,'returns','pt-BR').version,2)

    def test_13_old_event_cannot_roll_back(self):
        new_version(self.s);self.s.drain();self.s.process(1,replay=True)
        self.assertEqual(self.s.prepare(ALICE,'returns','pt-BR').version,2)

    def test_14_publish_rollback_whole_state(self):
        before=[tuple(r) for r in self.s.db.execute('SELECT * FROM epochs')]
        with self.assertRaises(RuntimeError): new_version(self.s,fail=True)
        self.assertEqual(self.s.prepare(ALICE,'returns','pt-BR').version,1)
        self.assertEqual([tuple(r) for r in self.s.db.execute('SELECT * FROM epochs')],before)
        self.assertEqual(self.s.db.execute('SELECT count(*) FROM versions').fetchone()[0],3)
        self.assertEqual(self.s.db.execute('SELECT count(*) FROM outbox').fetchone()[0],3)
        self.assertEqual(self.s.db.execute('SELECT count(*) FROM commands').fetchone()[0],3)

    def test_15_publish_retry_no_duplicate(self):
        new_version(self.s)
        count=self.s.db.execute('SELECT count(*) FROM outbox').fetchone()[0]
        self.assertEqual(new_version(self.s),2)
        self.assertEqual(self.s.db.execute('SELECT count(*) FROM outbox').fetchone()[0],count)

    def test_16_key_reuse_conflicts(self):
        with self.assertRaises(Conflict):
            self.s.publish('acme','returns','x','x','urn:x',['staff'],1,'a-1')

    def test_17_stale_writer_rejected(self):
        new_version(self.s)
        with self.assertRaises(Conflict):
            self.s.publish('acme','returns','x','x','urn:x',['staff'],1,'new-key')

    def test_18_worker_rollback_then_retry(self):
        new_version(self.s)
        with self.assertRaises(RuntimeError): self.s.process(4,fail=True)
        self.assertEqual(self.s.db.execute('SELECT done FROM outbox WHERE event_id=4').fetchone()[0],0)
        self.assertIsNone(self.s.prepare(ALICE,'returns','pt-BR'))
        self.s.process(4)
        self.assertEqual(self.s.prepare(ALICE,'returns','pt-BR').version,2)

    def test_19_worker_duplicate(self):
        self.assertEqual(self.s.process(1),'duplicate')

    def test_20_delete_immediate(self):
        self.s.delete('acme','returns',10,2)
        self.assertIsNone(self.s.prepare(ALICE,'returns','pt-BR'))
        self.assertEqual(self.s.db.execute("SELECT count(*) FROM projection WHERE tenant='acme' AND doc_id='returns'").fetchone()[0],1)

    def test_21_late_event_after_delete(self):
        self.s.delete('acme','returns',10,2);self.s.process(1,replay=True)
        self.assertEqual(self.s.db.execute("SELECT count(*) FROM projection WHERE tenant='acme' AND doc_id='returns'").fetchone()[0],0)

    def test_22_retention_boundary(self):
        self.s.delete('acme','returns',10,2)
        self.assertEqual(self.s.purge(11),0)
        self.assertEqual(self.s.purge(12),1)
        self.assertEqual(self.s.purge(12),0)
        self.assertEqual(self.s.db.execute("SELECT count(*) FROM versions WHERE tenant='acme' AND doc_id='returns'").fetchone()[0],0)
        self.assertEqual(self.c.answer(BOB,'returns')['answer'],'Prazo: 7 dias.')

    def test_23_tombstone_survives_purge(self):
        self.s.delete('acme','returns',10,0);self.s.purge(10)
        with self.assertRaises(Conflict): new_version(self.s)
        self.s.process(1,replay=True)
        self.assertIsNone(self.s.prepare(ALICE,'returns','pt-BR'))

    def test_24_invalid_language(self):
        with self.assertRaises(ValueError): self.s.prepare(ALICE,'returns','xx')

    def test_25_provenance_required(self):
        with self.assertRaises(ValueError):
            self.s.publish('acme','x','pt','en','',[],0,'blank')

    def test_26_hash_tamper_blocks(self):
        self.s.db.execute("UPDATE versions SET body_pt='changed' WHERE tenant='acme' AND doc_id='returns'")
        self.assertIsNone(self.s.prepare(ALICE,'returns','pt-BR'))

    def test_27_parameters_not_sql(self):
        self.assertIsNone(self.s.prepare(ALICE,"returns' OR 1=1 --",'pt-BR'))

    def test_28_foreign_key_scope(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.s.db.execute("INSERT INTO acl VALUES ('unknown','returns','staff')")

    def test_29_citation_version_and_hash(self):
        r=self.c.answer(ALICE,'returns')['citations'][0]
        self.assertEqual(r['version'],1)
        self.assertEqual(r['source'],'urn:acme:returns:v1')
        self.assertEqual(len(r['digest']),64)

    def test_30_key_changes_on_acl_epoch(self):
        before=self.s.prepare(ALICE,'returns','pt-BR')
        self.s.set_acl('acme','returns',['staff'])
        after=self.s.prepare(ALICE,'returns','pt-BR')
        self.assertNotEqual(cache_key(before),cache_key(after))

    def test_31_persistent_store_two_connections(self):
        with TemporaryDirectory(dir=Path(__file__).parent) as folder:
            path=Path(folder)/'case.db'
            first=seeded(path);second=Store(path)
            try:
                new_version(first)
                with self.assertRaises(Conflict):
                    second.publish('acme','returns','x','x','urn:x',[],1,'other')
                self.assertEqual(second.db.execute('SELECT count(*) FROM outbox WHERE done=0').fetchone()[0],1)
            finally: first.close();second.close()

    def test_32_scenarios_and_exercises(self):
        result=run_scenarios()
        self.assertEqual((result['passed'],result['total']),(12,12))
        self.assertEqual(exercise9()['version'],2)
        self.assertEqual(exercise10()['cache_entries'],0)

if __name__ == '__main__': unittest.main()
