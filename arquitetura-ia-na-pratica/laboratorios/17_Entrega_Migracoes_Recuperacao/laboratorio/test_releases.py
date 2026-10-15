import json,sqlite3,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from releases import Registry,manifest,migration_v2,Refused,AckLost,check_epoch
from release_scenarios import SCRATCH,NAMES,fixture,revised,run_case
from release_exercises import exercise33,exercise34

EXPECTED={
 'baseline':('r1',1,1,None),'migration_required':('r1',1,1,'migration_required'),
 'evaluation_required':('r1',1,2,'evaluation_required'),'quality_fail':('r1',1,2,'quality_gate'),
 'evaluation_expired':('r1',1,2,'evaluation_expired'),'promote':('r2',2,2,None),
 'rollback':('r1',3,2,None),'stale_operator':('r2',2,2,'stale_operator'),
 'crash_before':('r1',1,2,'crash'),'ack_lost':('r2',2,2,'ack_lost'),
 'pinned_job':('r2',2,2,None),'new_job':('r2',2,2,None),
 'source_changed':('r1',1,2,'index_changed'),'source_revoked':('r1',1,2,'source_access'),
 'manifest_corrupt':('r1',1,2,'manifest_integrity'),'evidence_mismatch':('r1',1,2,'evaluation_mismatch'),
 'migration_crash':('r1',1,1,'crash'),'restart':('r2',2,2,None),
 'restore':('r1',1,1,None),'restore_quarantine':('r1',1,1,'recovery_mode')}
class ScenarioTests(unittest.TestCase):pass
def scenario_test(name,language):
    def test(self):
        r=run_case(name,language)
        self.assertEqual(tuple(r[k] for k in ('release','epoch','schema','error')),EXPECTED[name])
        self.assertEqual(r['mode'],'recovery' if name=='restore_quarantine' else 'serving')
        self.assertEqual(r['lost_jobs'],int(name in ('restore','restore_quarantine')))
        if name=='pinned_job':self.assertEqual(r['job_release'],'r1');self.assertFalse(r['provenance'])
        if name=='new_job':self.assertEqual(r['job_release'],'r2');self.assertTrue(r['provenance'])
    return test
for lang in ('pt-BR','en-US'):
    for name in NAMES:setattr(ScenarioTests,'test_'+lang.replace('-','_')+'_'+name,scenario_test(name,lang))

class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory(dir=SCRATCH);self.root=Path(self.tmp.name)
        self.store,self.r=fixture(self.root/'registry.db')
    def tearDown(self):self.r.close();self.store.close();self.tmp.cleanup()
    def ready(self):migration_v2(self.r.db);self.r.evaluate('r2',self.store)
    def promote(self):self.ready();return self.r.switch('r2',1,self.store)
    def test_migration_idempotent(self):
        migration_v2(self.r.db);before=self.r.logical();migration_v2(self.r.db)
        self.assertEqual(before,self.r.logical())
    def test_failed_migration_leaves_no_column(self):
        with self.assertRaises(RuntimeError):migration_v2(self.r.db,True)
        self.assertNotIn('provenance',[r[1] for r in self.r.db.execute('PRAGMA table_info(jobs)')])
        self.assertEqual(self.r.schema(),1)
    def test_rollback_keeps_v2_data_and_old_writer_works(self):
        self.promote();self.r.pin('new');self.r.execute('new',self.store)
        proof=self.r.db.execute("SELECT provenance FROM jobs WHERE id='new'").fetchone()[0]
        self.r.switch('r1',2,self.store,reason='rollback');self.r.pin('old');self.r.execute('old',self.store)
        self.assertEqual(self.r.db.execute("SELECT provenance FROM jobs WHERE id='new'").fetchone()[0],proof)
        self.assertIsNone(self.r.db.execute("SELECT provenance FROM jobs WHERE id='old'").fetchone()[0])
    def test_pin_retry_does_not_rebind(self):
        self.r.pin('job');self.promote();self.assertEqual(self.r.pin('job'),'r1')
    def test_pin_conflicting_language_rejected(self):
        self.r.pin('job')
        with self.assertRaisesRegex(Refused,'job_conflict'):self.r.pin('job','en-US')
    def test_unknown_job_rejected(self):
        with self.assertRaisesRegex(Refused,'unknown_job'):self.r.execute('unknown',self.store)
    def test_empty_registry_cannot_admit(self):
        empty=Registry()
        try:
            with self.assertRaisesRegex(Refused,'no_active_release'):empty.pin('job')
        finally:empty.close()
    def test_manifest_id_is_immutable(self):
        with self.assertRaisesRegex(Refused,'immutable_release'):self.r.stage(manifest(self.store,'r1','v2'))
    def test_staging_retry_is_idempotent(self):
        before=self.r.logical();self.r.stage(self.r.get('r1'));self.assertEqual(before,self.r.logical())
    def test_secret_field_rejected(self):
        b=manifest(self.store,'extra');b['api_key']='SYNTHETIC_NOT_A_KEY'
        with self.assertRaisesRegex(Refused,'manifest_schema'):self.r.stage(b)
    def test_code_digest_drift_rejected(self):
        b=manifest(self.store,'other');b['code_digest']='0'*64;self.r.stage(b)
        with self.assertRaisesRegex(Refused,'code_changed'):self.r.evaluate('other',self.store)
    def test_cached_result_rechecks_source(self):
        self.r.pin('job');self.r.execute('job',self.store);revised(self.store)
        with self.assertRaisesRegex(Refused,'index_changed'):self.r.execute('job',self.store)
    def test_rollback_cannot_undo_permission_revocation(self):
        self.promote();self.store.set_acl('acme','manual-a',['admin'])
        with self.assertRaisesRegex(Refused,'source_access'):self.r.switch('r1',2,self.store,reason='rollback')
        self.assertEqual(self.r.head()['release'],'r2')
    def test_rollback_requires_fresh_evaluation(self):
        self.promote()
        with self.assertRaisesRegex(Refused,'evaluation_expired'):self.r.switch('r1',2,self.store,20,reason='rollback')
        self.r.evaluate('r1',self.store,20);self.r.switch('r1',2,self.store,21,reason='rollback')
        self.assertEqual(self.r.head()['epoch'],3)
    def test_clock_inputs_checked(self):
        for now in (-1,True,0.5):
            with self.subTest(now=now):
                with self.assertRaisesRegex(Refused,'clock'):self.r.evaluate('r1',self.store,now)
    def test_evaluation_clock_cannot_regress(self):
        self.r.evaluate('r1',self.store,3)
        with self.assertRaisesRegex(Refused,'clock_regression'):self.r.evaluate('r1',self.store,2)
    def test_broken_candidate_has_four_of_six(self):
        e=self.r.evaluate('bad',self.store);self.assertEqual(e['passed'],4);self.assertEqual(e['total'],6)
    def test_rollback_to_never_active_is_denied(self):
        self.ready()
        with self.assertRaisesRegex(Refused,'not_previously_active'):self.r.switch('r2',1,self.store,reason='rollback')
    def test_pointer_and_event_rollback_together(self):
        self.ready();before=self.r.logical()
        with self.assertRaises(RuntimeError):self.r.switch('r2',1,self.store,fault='before')
        self.assertEqual(before,self.r.logical())
    def test_lost_ack_retry_does_not_create_second_event(self):
        self.ready()
        with self.assertRaises(AckLost):self.r.switch('r2',1,self.store,fault='after')
        with self.assertRaisesRegex(Refused,'stale_operator'):self.r.switch('r2',1,self.store)
        self.assertEqual(self.r.db.execute('SELECT count(*) FROM events').fetchone()[0],2)
    def test_two_connections_reject_stale_operator(self):
        self.ready();other=Registry(self.root/'registry.db');seen=other.head()['epoch']
        try:
            self.r.switch('r2',1,self.store)
            with self.assertRaisesRegex(Refused,'stale_operator'):other.switch('r1',seen,self.store,reason='rollback')
        finally:other.close()
    def test_backup_restore_requires_resume(self):
        self.r.pin('job');p=self.root/'backup.db';self.r.backup(p);restored=Registry.restore(p,self.root/'restore.db')
        try:
            with self.assertRaisesRegex(Refused,'recovery_mode'):restored.execute('job',self.store)
            restored.evaluate('r1',self.store,20);restored.resume(self.store,21)
            self.assertEqual(restored.execute('job',self.store)['status'],'answered')
        finally:restored.close()
    def test_backup_corruption_detected_without_overwrite(self):
        p=self.root/'backup.db';self.r.backup(p);d=sqlite3.connect(p)
        d.execute('UPDATE head SET epoch=42');d.commit();d.close();destination=self.root/'restore.db'
        with self.assertRaisesRegex(Refused,'backup_digest'):Registry.restore(p,destination)
        self.assertFalse(destination.exists())
    def test_existing_restore_target_preserved(self):
        p=self.root/'backup.db';self.r.backup(p);dest=self.root/'keep.db';dest.write_bytes(b'keep')
        with self.assertRaisesRegex(Refused,'destination_exists'):Registry.restore(p,dest)
        self.assertEqual(dest.read_bytes(),b'keep')
    def test_existing_backup_preserved(self):
        p=self.root/'backup.db';self.r.backup(p);old=p.read_bytes()
        with self.assertRaisesRegex(Refused,'backup_exists'):self.r.backup(p)
        self.assertEqual(p.read_bytes(),old)
    def test_resume_after_source_change_blocked(self):
        p=self.root/'backup.db';self.r.backup(p);restored=Registry.restore(p,self.root/'restore.db')
        try:
            revised(self.store)
            with self.assertRaisesRegex(Refused,'index_changed'):restored.resume(self.store,2)
            self.assertEqual(restored.mode(),'recovery')
        finally:restored.close()
    def test_unknown_schema_not_assumed_compatible(self):
        self.ready();self.r.db.execute("UPDATE meta SET value='3' WHERE key='schema'")
        with self.assertRaisesRegex(Refused,'unsupported_schema'):self.r.switch('r2',1,self.store)
    def test_printed_epoch_guard(self):
        check_epoch({'release':'r1','epoch':1},1,'r2')
        with self.assertRaisesRegex(Refused,'already_active'):check_epoch({'release':'r1','epoch':1},1,'r1')
    def test_exercise33(self):self.assertEqual(exercise33()['rollback_epoch'],3)
    def test_exercise34(self):self.assertEqual(exercise34()['lost_jobs'],1)

if __name__=='__main__':unittest.main()
