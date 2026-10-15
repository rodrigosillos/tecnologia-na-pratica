from pathlib import Path
from tempfile import TemporaryDirectory
import json
from fixtures import ingest
from job_worker import manuals
from releases import Registry,manifest,migration_v2,Refused,AckLost

SCRATCH=Path(__file__).resolve().parent/'scratch';SCRATCH.mkdir(exist_ok=True)
NAMES=('baseline','migration_required','evaluation_required','quality_fail',
       'evaluation_expired','promote','rollback','stale_operator','crash_before',
       'ack_lost','pinned_job','new_job','source_changed','source_revoked',
       'manifest_corrupt','evidence_mismatch','migration_crash','restart',
       'restore','restore_quarantine')


def fixture(path=':memory:'):
    store=manuals();r=Registry(path)
    for id,run in [('r1','v1'),('r2','v2'),('bad','broken')]:r.stage(manifest(store,id,run))
    r.evaluate('r1',store);r.switch('r1',0,store)
    return store,r


def revised(store):
    ingest(store,'manual-a','Devolução: prazo de 46 dias. Postagem: despacho em 3 dias.',
           'Returns: window of 46 days. Shipping: dispatch in 3 days.',expected=1)


def run_case(name,language='pt-BR'):
    if name not in NAMES:raise ValueError('case')
    with TemporaryDirectory(dir=SCRATCH) as tmp:
        root=Path(tmp);path=root/'registry.db';store,r=fixture(path)
        error=None;job_release=None;provenance=False;lost_jobs=0
        try:
            if name=='baseline':pass
            elif name=='migration_crash':migration_v2(r.db,fail=True)
            elif name in ('restore','restore_quarantine'):
                r.pin('old',language);backup=root/'backup.db';r.backup(backup)
                migration_v2(r.db);r.evaluate('r2',store);r.switch('r2',1,store)
                r.pin('new',language);r.close();r=Registry.restore(backup,root/'restored.db')
                lost_jobs=int(r.db.execute("SELECT 1 FROM jobs WHERE id='new'").fetchone() is None)
                if name=='restore_quarantine':r.pin('denied',language)
                else:
                    r.evaluate('r1',store,20);r.resume(store,21)
                    result=r.execute('old',store);job_release='r1';provenance='provenance' in result
            else:
                if name!='migration_required':migration_v2(r.db)
                target='bad' if name=='quality_fail' else 'r2'
                if name!='evaluation_required':r.evaluate(target,store)
                if name=='source_changed':revised(store)
                if name=='source_revoked':store.set_acl('acme','manual-a',['admin'])
                if name=='manifest_corrupt':r.db.execute("UPDATE releases SET body='{}' WHERE id='r2'")
                if name=='evidence_mismatch':
                    e=json.loads(r.db.execute("SELECT body FROM assessments WHERE id='r2'").fetchone()[0]);e['manifest_digest']='0'*64
                    r.db.execute("UPDATE assessments SET body=? WHERE id='r2'",(json.dumps(e),))
                if name=='pinned_job':job_release=r.pin('job',language)
                r.switch(target,1,store,now=15 if name=='evaluation_expired' else 2,
                    fault='before' if name=='crash_before' else ('after' if name=='ack_lost' else None))
                if name=='rollback':r.switch('r1',2,store,3,reason='rollback')
                if name=='stale_operator':r.switch('r1',1,store,3,reason='rollback')
                if name=='new_job':job_release=r.pin('job',language)
                if name in ('pinned_job','new_job'):provenance='provenance' in r.execute('job',store)
                if name=='restart':r.close();r=Registry(path)
        except (Refused,RuntimeError) as exc:
            error=('ack_lost' if isinstance(exc,AckLost) else
                   'crash' if type(exc) is RuntimeError else str(exc))
        result={'case':name,'language':language,**r.head(),'schema':r.schema(),
                'mode':r.mode(),'error':error,'job_release':job_release,
                'provenance':provenance,'lost_jobs':lost_jobs}
        r.close();store.close();return result


def run_scenarios():
    return {'measurement':'Local SQLite transitions and deterministic fixture evaluation; no real rollout, model, or production RTO.',
            'cases':40,'language_pairs':20,
            'runs':[run_case(n,l) for l in ('pt-BR','en-US') for n in NAMES]}


if __name__=='__main__':print(json.dumps(run_scenarios(),ensure_ascii=False,indent=2))
