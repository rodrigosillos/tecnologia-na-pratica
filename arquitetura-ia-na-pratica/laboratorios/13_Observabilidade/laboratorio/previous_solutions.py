from pathlib import Path
import json
from fixtures import seeded,ALICE
from retrieval import answer,verify_citation

def exercise13():
    s=seeded()
    try:
        result={}
        for query in ('POL-RET-01','Arrependimento?'):
            result[query]={}
            for mode in ('lexical','vector','hybrid'):
                reply=answer(s,ALICE,query,mode=mode)
                assert verify_citation(s,ALICE,reply,'pt-BR')
                result[query][mode]=reply['status']
        assert result['POL-RET-01']==dict(
            lexical='answer',vector='abstain',hybrid='answer')
        assert result['Arrependimento?']==dict(
            lexical='abstain',vector='answer',hybrid='answer')
        return result
    finally:
        s.close()

def exercise14():
    s=seeded()
    try:
        initial=answer(s,ALICE,'Prazo de devolução?')
        assert initial['status']=='answer'
        assert verify_citation(s,ALICE,initial,'pt-BR')
        def revoke():
            s.set_acl('acme','returns',['admin'])
        interrupted=answer(s,ALICE,'Prazo de devolução?',
                           between=revoke)
        after=answer(s,ALICE,'Prazo de devolução?')
        assert interrupted['status']=='abstain'
        assert interrupted['reason']=='state_changed'
        assert interrupted['citations']==[]
        assert after['status']=='abstain'
        assert not verify_citation(s,ALICE,initial,'pt-BR')
        return dict(before=initial['status'],
                    during=interrupted['status'],after=after['status'],
                    released_citations=len(interrupted['citations']))
    finally:
        s.close()

if __name__=='__main__':
    result={'exercise13':exercise13(),'exercise14':exercise14()}
    folder=Path(__file__).with_name('results');folder.mkdir(exist_ok=True)
    (folder/'solutions.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
