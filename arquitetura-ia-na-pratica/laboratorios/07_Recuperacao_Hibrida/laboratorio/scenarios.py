from pathlib import Path
import json
from fixtures import seeded,ALICE,CASES,GOLD_CLAIMS
from retrieval import collect,rank,answer,verify_citation

def evaluate(mode):
    s=seeded();rows=[]
    try:
        for key,language,query,gold,status in CASES:
            ranked=rank(query,collect(s,ALICE,language),mode)
            docs=list(dict.fromkeys(e.snapshot.document for e in ranked))
            position=docs.index(gold)+1 if gold in docs else 0
            result=answer(s,ALICE,query,language,mode)
            correct=(result['status']==status and (gold is None or
                     (result['citations'] and result['citations'][0]['document']==gold
                      and result['text']==GOLD_CLAIMS[language][gold])))
            rows.append(dict(case=key,language=language,query=query,gold=gold,
                expected_status=status,rank=position,status=result['status'],
                correct=bool(correct),citation_valid=verify_citation(s,ALICE,result,language)))
        positives=[r for r in rows if r['gold']]
        negative=[r for r in rows if not r['gold']]
        eligible=len(positives)
        return dict(mode=mode,eligible=eligible,total=len(rows),
            recall1=sum(r['rank']==1 for r in positives)/eligible,
            recall3=sum(0<r['rank']<=3 for r in positives)/eligible,
            mrr=sum(1/r['rank'] if r['rank'] else 0 for r in positives)/eligible,
            supported_answers=sum(r['correct'] for r in positives),
            correct_nonanswers=sum(r['correct'] for r in negative),
            citation_violations=sum(not r['citation_valid'] for r in rows),cases=rows)
    finally:s.close()

def run_scenarios():
    return dict(kind='authored synthetic regression; not held-out evaluation',
                cases=len(CASES),eligible=sum(bool(c[3]) for c in CASES),
                variants=[evaluate(mode) for mode in ('lexical','vector','hybrid')])

if __name__=='__main__':
    result=run_scenarios()
    folder=Path(__file__).with_name('results');folder.mkdir(exist_ok=True)
    (folder/'scenarios.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({v['mode']:{k:x for k,x in v.items() if k!='cases'} for v in result['variants']},indent=2))
