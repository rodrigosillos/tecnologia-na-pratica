import json
import unittest
from pipeline import (Pipeline, Actor, Copilot, Conflict, LostLease,
                      chunk_text, extract, DEFAULT_CONFIG)
from scenarios import seeded, submit, stage, ALICE, BOB, raw_source
from solutions import exercise11, exercise12

class TextTests(unittest.TestCase):
    def test_exact_boundary(self):
        self.assertEqual(chunk_text('abcdefgh',8,2),[(0,8,'abcdefgh')])
    def test_overlap_and_offsets(self):
        text='abcdefghijklmnopq'
        rows=chunk_text(text,8,2)
        self.assertEqual([(a,b) for a,b,_ in rows],[(0,8),(6,14),(12,17)])
        self.assertEqual(rows[0][2]+''.join(r[2][2:] for r in rows[1:]),text)
    def test_empty_chunks(self):
        self.assertEqual(chunk_text('',8,2),[])
    def test_invalid_overlap(self):
        for value in (-1,8,9):
            with self.subTest(value=value),self.assertRaises(ValueError):chunk_text('abc',8,value)
    def test_nfc_and_newlines(self):
        raw=json.dumps({'pt-BR':' cafe\u0301\r\nx ','en-US':' x\ry '}).encode()
        self.assertEqual(extract(raw),{'pt-BR':'café\nx','en-US':'x\ny'})
    def test_duplicate_fields(self):
        with self.assertRaises(ValueError):extract(b'{"pt-BR":"a","pt-BR":"b","en-US":"c"}')
    def test_wrong_shape(self):
        for data in ([],{}, {'pt-BR':'a'}, {'pt-BR':4,'en-US':'b'}, {'pt-BR':'a','en-US':'b','x':'c'}):
            with self.subTest(data=data),self.assertRaises(ValueError):extract(json.dumps(data).encode())
    def test_invalid_text(self):
        for text in (' ','\x00','x'*6001):
            with self.subTest(length=len(text)),self.assertRaises(ValueError):extract(json.dumps({'pt-BR':text,'en-US':'a'}).encode())
    def test_bad_utf8(self):
        with self.assertRaises(UnicodeError):extract(b'\xff')

class PipelineTests(unittest.TestCase):
    def setUp(self):self.s=seeded()
    def tearDown(self):self.s.close()
    def ready(self):
        j=submit(self.s);lease=self.s.claim(j,'a',0);stage(self.s,lease,1)
        return j,lease
    def count(self,table):return self.s.db.execute('SELECT count(*) FROM '+table).fetchone()[0]
    def test_byte_admission(self):
        for raw in (b'',b'x'*8193,'text'):
            with self.subTest(length=len(raw)),self.assertRaises(ValueError):submit(self.s,raw=raw)
        self.assertEqual(self.count('jobs'),0)
    def test_invalid_config(self):
        for change in ({'size':True},{'size':7},{'overlap':72},{'extractor':'v2'},{'extra':1}):
            with self.subTest(change=change),self.assertRaises(ValueError):submit(self.s,config={**DEFAULT_CONFIG,**change})
    def test_invalid_intent(self):
        for change in ({'expected':-1},{'expected':True},{'roles':'staff'},{'roles':['']},{'source':''}):
            with self.subTest(change=change),self.assertRaises(ValueError):submit(self.s,**change)
    def test_same_intent(self):
        self.assertEqual(submit(self.s),submit(self.s));self.assertEqual(self.count('jobs'),1)
    def test_conflicting_key(self):
        submit(self.s)
        for change in ({'raw':b'other'},{'source':'urn:other'},{'roles':['admin']},{'config':{**DEFAULT_CONFIG,'size':80}}):
            with self.subTest(change=change),self.assertRaises(Conflict):submit(self.s,**change)
    def test_tenant_scoped_key(self):
        self.assertNotEqual(submit(self.s),submit(self.s,tenant='zen'))
    def test_new_config_requires_new_intent(self):
        first=submit(self.s)
        second=submit(self.s,request_id='rechunk',config={**DEFAULT_CONFIG,'size':80})
        self.assertNotEqual(first,second)
    def test_invalid_source_quarantine(self):
        j=submit(self.s,raw=b'{');lease=self.s.claim(j,'a',0)
        self.assertEqual(self.s.prepare_job(lease,1),'quarantined')
        self.assertIsNone(self.s.claim(j,'b',20));self.assertEqual(self.count('chunks'),0)
    def test_source_integrity(self):
        j=submit(self.s);lease=self.s.claim(j,'a',0)
        self.s.db.execute('UPDATE jobs SET raw=? WHERE job_id=?',(b'other',j))
        self.assertEqual(self.s.prepare_job(lease,1),'quarantined')
    def test_prepare_is_repeatable(self):
        j=submit(self.s);lease=self.s.claim(j,'a',0)
        self.s.prepare_job(lease,1);before=self.s.job(j)
        self.s.prepare_job(lease,2);self.assertEqual(before,self.s.job(j))
    def test_staging_not_visible(self):
        j,lease=self.ready()
        self.assertEqual(self.s.visible_chunks(ALICE,'returns'),[])
        self.assertEqual(Copilot(self.s).answer(ALICE,'returns')['answer'],'Prazo: 30 dias.')
    def test_batch_and_checkpoint_rollback(self):
        j=submit(self.s);lease=self.s.claim(j,'a',0);self.s.prepare_job(lease,1)
        with self.assertRaises(RuntimeError):self.s.write_batch(lease,2,fail=True)
        self.assertEqual((self.count('chunks'),self.s.job(j)['cursor']),(0,0))
        self.assertEqual(self.s.write_batch(lease,3),2)
    def test_durable_restart(self):self.assertEqual(exercise11()['duplicates'],0)
    def test_busy_lease(self):
        j=submit(self.s);self.s.claim(j,'a',0)
        self.assertIsNone(self.s.claim(j,'b',9))
    def test_fencing_at_expiry(self):
        j=submit(self.s);old=self.s.claim(j,'a',0);self.s.prepare_job(old,1)
        new=self.s.claim(j,'b',10);self.assertEqual(new.token,old.token+1)
        with self.assertRaises(LostLease):self.s.write_batch(old,10)
        with self.assertRaises(LostLease):self.s.renew(old,10)
        self.assertEqual(self.count('chunks'),0)
    def test_expired_without_replacement(self):
        j=submit(self.s);lease=self.s.claim(j,'a',0)
        with self.assertRaises(LostLease):self.s.prepare_job(lease,10)
    def test_renewal(self):
        j=submit(self.s);lease=self.s.claim(j,'a',0);self.s.renew(lease,9)
        self.assertIsNone(self.s.claim(j,'b',10))
        self.assertEqual(self.s.prepare_job(lease,18),'staging')
    def test_claim_budget(self):
        j=submit(self.s)
        for t in (0,10,20):self.assertIsNotNone(self.s.claim(j,'worker',t))
        self.assertIsNone(self.s.claim(j,'worker',30))
        self.assertEqual(self.s.job(j)['error'],'claim_budget')
    def test_partial_cannot_activate(self):
        j=submit(self.s);lease=self.s.claim(j,'a',0);self.s.prepare_job(lease,1)
        self.s.write_batch(lease,2)
        with self.assertRaises(Conflict):self.s.activate(lease,3)
        self.assertEqual(self.count('heads'),0)
    def test_missing_chunk(self):
        j,lease=self.ready()
        self.s.db.execute('DELETE FROM chunks WHERE job_id=? AND ordinal=0',(j,))
        self.assertIsNone(self.s.activate(lease,2));self.assertEqual(self.s.job(j)['error'],'chunk_integrity')
    def test_altered_chunk(self):
        j,lease=self.ready();self.s.db.execute('UPDATE chunks SET body=? WHERE job_id=?',('bad',j))
        self.assertIsNone(self.s.activate(lease,2));self.assertEqual(self.count('heads'),0)
    def test_altered_plan(self):
        j=submit(self.s);lease=self.s.claim(j,'a',0);self.s.prepare_job(lease,1)
        self.s.db.execute('UPDATE jobs SET normalized=? WHERE job_id=?',(json.dumps({'pt-BR':'changed','en-US':'changed'}),j))
        self.assertEqual(self.s.write_batch(lease,2),0)
        self.assertEqual(self.s.job(j)['error'],'plan_changed')
    def test_activation_rollback(self):
        j,lease=self.ready();before=(self.count('versions'),self.count('outbox'))
        with self.assertRaises(RuntimeError):self.s.activate(lease,2,fail=True)
        self.assertEqual(before,(self.count('versions'),self.count('outbox')))
        self.assertEqual(self.count('heads'),0);self.assertEqual(self.s.job(j)['state'],'ready')
        self.assertEqual(self.s.activate(lease,3),2)
    def test_activation_replay(self):
        j,lease=self.ready();self.s.activate(lease,2)
        before=(self.count('versions'),self.count('outbox'))
        self.assertEqual(self.s.activate(lease,100),2)
        self.assertEqual(before,(self.count('versions'),self.count('outbox')))
    def test_projection_lag_and_visibility(self):
        j,lease=self.ready();self.s.activate(lease,2)
        self.assertEqual(self.s.visible_chunks(ALICE,'returns'),[])
        self.s.drain();rows=self.s.visible_chunks(ALICE,'returns')
        self.assertEqual(len(rows),3);self.assertTrue(rows[0]['body'].startswith('Prazo: 45'))
        self.assertEqual(len(self.s.visible_chunks(ALICE,'returns','en-US')),3)
    def test_stale_version(self):
        j,lease=self.ready()
        self.s.publish('acme','returns','Outro','Other','urn:new',['admin'],1,'other')
        self.assertIsNone(self.s.activate(lease,2));self.assertEqual(self.s.job(j)['state'],'obsolete')
    def test_acl_change(self):self.assertEqual(exercise12()['state'],'obsolete')
    def test_membership_change(self):
        j,lease=self.ready();self.s.principal('acme','alice','staff',False)
        self.assertIsNone(self.s.activate(lease,2));self.assertEqual(self.s.job(j)['state'],'obsolete')
    def test_isolation_and_unknown_user(self):
        j,lease=self.ready();self.s.activate(lease,2);self.s.drain()
        self.assertEqual(self.s.visible_chunks(BOB,'returns'),[])
        self.assertEqual(self.s.visible_chunks(Actor('acme','bob'),'returns'),[])
        self.assertEqual(Copilot(self.s).answer(BOB,'returns')['answer'],'Prazo: 7 dias.')
    def test_new_document_not_visible_early(self):
        j=submit(self.s,doc='new',expected=0);lease=self.s.claim(j,'a',0);stage(self.s,lease,1)
        self.assertEqual(Copilot(self.s).answer(ALICE,'new')['status'],'unavailable')
        self.assertEqual(self.s.activate(lease,2),1);self.s.drain()
        self.assertEqual(len(self.s.visible_chunks(ALICE,'new')),3)
    def test_delete_and_purge(self):
        j,lease=self.ready();self.s.activate(lease,2);self.s.drain()
        self.s.delete('acme','returns',10,2)
        self.assertEqual(self.s.visible_chunks(ALICE,'returns'),[])
        self.assertEqual(self.s.purge(11),0);self.assertEqual(self.count('jobs'),1)
        self.assertEqual(self.s.purge(12),1)
        for table in ('jobs','chunks','heads'):self.assertEqual(self.count(table),0)
        self.assertEqual(Copilot(self.s).answer(BOB,'returns')['answer'],'Prazo: 7 dias.')
    def test_deleted_during_ingestion(self):
        j,lease=self.ready();self.s.delete('acme','returns',10,2)
        self.assertIsNone(self.s.activate(lease,2));self.assertEqual(self.s.job(j)['state'],'obsolete')

if __name__=='__main__':unittest.main(verbosity=2)
