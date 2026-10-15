import json
from pathlib import Path
from threading import Event
from fixtures import seeded, ALICE
from service import open_stream
from client import consume, fragments
from contract import ContractError

def request(texts=None, language='pt-BR'):
    if texts is None:
        texts = ['Prazo de devolução?', 'Prazo de postagem?']
    return dict(schema_version='1.0', request_id='demo-08', language=language,
                queries=[dict(id=f'q{i+1}', text=q) for i,q in enumerate(texts)])

def wire(store, req=None, **options):
    req = req or request()
    body = json.dumps(req, ensure_ascii=False).encode('utf-8')
    status, headers, stream = open_stream(store, ALICE, body, **options)
    assert status == 200 and headers['Content-Type'] == 'text/event-stream'
    return list(stream)

def run_case(name, language='pt-BR'):
    store = seeded()
    token = Event()
    texts = ['Prazo de devolução?', 'Prazo de postagem?'] if language == 'pt-BR' else ['Returns window?', 'Shipping days?']
    options = {'cancel':token}
    if name == 'partial':texts[1] = 'Orbital mechanics?'
    if name == 'clarify':texts = ['Qual o prazo?' if language=='pt-BR' else 'What window?']
    if name == 'cancelled':options['before_release'] = token.set
    if name == 'revoked':options['before_release'] = lambda: store.set_acl('acme','returns',['admin'])
    if name == 'error':
        def broken(*args):raise RuntimeError('secret document and token must not escape')
        options['engine'] = broken
    req = request(texts, language)
    try:
        frames = wire(store, req, **options)
        if name == 'truncated':frames = frames[:-1]
        client = consume(fragments(b''.join(frames), 7), req['request_id'], [q['id'] for q in req['queries']])
        return dict(case=name, language=language, state=client.state,
                    outcome=client.result['outcome'] if client.result else None,
                    answers=sum(i['status']=='answer' for i in client.result['items']) if client.result else 0,
                    progress_events=len(client.progress))
    except ContractError:
        return dict(case=name, language=language, state='protocol_error', outcome=None, answers=0, progress_events=None)
    finally:
        store.close()

def run_scenarios():
    names = ['complete','partial','clarify','cancelled','revoked','error','truncated']
    return {'cases':14, 'measurement':'Deterministic in-process contract scenarios, not network or LLM benchmarks',
            'runs':[run_case(name,lang) for lang in ('pt-BR','en-US') for name in names]}

if __name__ == '__main__':
    data=run_scenarios(); out=Path('results');out.mkdir(exist_ok=True)
    (out/'scenarios.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(data,ensure_ascii=False,indent=2))
