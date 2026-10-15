import json
from pipeline import Pipeline,Actor,DEFAULT_CONFIG

ALICE=Actor('acme','alice');ADMIN=Actor('acme','ana');BOB=Actor('zen','bob')
DOCUMENTS={
 'returns':('[POL-RET-01] Devolução: prazo de 45 dias. Exige comprovante de compra.',
            '[POL-RET-01] Returns: window of 45 days. Proof of purchase is required.'),
 'shipping':('[POL-SHIP-01] Postagem: despacho em 3 dias. Consulte o rastreio no portal.',
             '[POL-SHIP-01] Shipping: dispatch in 3 days. Track the parcel in the portal.'),
 'reset':('[POL-AUTH-01] Redefinição de senha: link válido por 15 minutos. Não compartilhe o link.',
          '[POL-AUTH-01] Password reset: link valid for 15 minutes. Do not share the link.'),
 'backup':('[POL-BAK-01] Backup: retenção de 30 dias. A restauração exige autorização.',
           '[POL-BAK-01] Backup: retention of 30 days. Restore requires authorization.'),
 'rate':('[POL-API-01] Erro 429: aguarde 60 segundos antes de repetir. Respeite o limite da API.',
         '[POL-API-01] Error 429: wait 60 seconds before retry. Respect the API rate limit.'),
 'support':('[POL-SUP-01] Suporte: resposta em até 24 horas. Use o canal de atendimento.',
            '[POL-SUP-01] Support: response within 24 hours. Use the helpdesk channel.'),
 'payroll':('Folha: pagamento confidencial no dia 20. Apenas administradores.',
            'Payroll: confidential payment on day 20. Administrators only.')}

def ingest(s,doc,pt,en,tenant='acme',roles=None,expected=0,key=None,drain=True):
    roles=['staff','admin'] if roles is None else roles
    source=f'urn:{tenant}:{doc}:v{expected+1}'
    raw=json.dumps({'pt-BR':pt,'en-US':en},ensure_ascii=False).encode()
    job=s.submit(tenant,doc,raw,source,roles,expected,key or source,
                 {**DEFAULT_CONFIG,'size':160,'overlap':20})
    lease=s.claim(job,'fixture',0,ttl=10)
    s.prepare_job(lease,1)
    while s.job(job)['state']=='staging':s.write_batch(lease,2)
    version=s.activate(lease,3)
    if drain:s.drain()
    return job,version

def seeded():
    s=Pipeline()
    s.principal('acme','alice','staff');s.principal('acme','ana','admin')
    s.principal('zen','bob','staff')
    for doc,(pt,en) in DOCUMENTS.items():
        ingest(s,doc,pt,en,roles=['admin'] if doc=='payroll' else None)
    ingest(s,'returns','[POL-RET-01] Devolução: prazo de 7 dias.',
           '[POL-RET-01] Returns: window of 7 days.',tenant='zen',roles=['staff'])
    return s

# Authored synthetic regression cases, not a held-out benchmark.
GOLD_CLAIMS={
 'pt-BR':dict(returns='Devolução: prazo de 45 dias.',shipping='Postagem: despacho em 3 dias.',
              reset='Redefinição de senha: link válido por 15 minutos.',backup='Backup: retenção de 30 dias.',
              rate='Erro 429: aguarde 60 segundos antes de repetir.',support='Suporte: resposta em até 24 horas.'),
 'en-US':dict(returns='Returns: window of 45 days.',shipping='Shipping: dispatch in 3 days.',
              reset='Password reset: link valid for 15 minutes.',backup='Backup: retention of 30 days.',
              rate='Error 429: wait 60 seconds before retry.',support='Support: response within 24 hours.')}
CASES=[
 ('pt-id','pt-BR','POL-RET-01','returns','answer'),
 ('en-id','en-US','POL-RET-01','returns','answer'),
 ('pt-alias','pt-BR','Arrependimento?','returns','answer'),
 ('en-alias','en-US','Exchange?','returns','answer'),
 ('pt-ship','pt-BR','Prazo de postagem?','shipping','answer'),
 ('en-ship','en-US','Shipping days?','shipping','answer'),
 ('pt-reset','pt-BR','Validade da senha?','reset','answer'),
 ('en-reset','en-US','Password reset minutes?','reset','answer'),
 ('pt-backup','pt-BR','Tempo de backup?','backup','answer'),
 ('en-backup','en-US','Backup retention days?','backup','answer'),
 ('pt-rate','pt-BR','429 segundos?','rate','answer'),
 ('en-rate','en-US','429 seconds?','rate','answer'),
 ('pt-support','pt-BR','Suporte horas?','support','answer'),
 ('en-support','en-US','Support hours?','support','answer'),
 ('pt-ambiguous','pt-BR','Qual o prazo?',None,'clarify'),
 ('en-ambiguous','en-US','What window?',None,'clarify'),
 ('pt-multiple','pt-BR','Prazo de devolução e postagem?',None,'clarify'),
 ('en-multiple','en-US','Returns and shipping?',None,'clarify'),
 ('pt-unknown','pt-BR','Feriados municipais?',None,'abstain'),
 ('en-unknown','en-US','Office holidays?',None,'abstain'),
 ('pt-unsupported','pt-BR','Devolução sem comprovante?',None,'abstain'),
 ('en-unsupported','en-US','Returns without receipt?',None,'abstain'),
 ('pt-payroll','pt-BR','Folha pagamento?',None,'abstain'),
 ('en-payroll','en-US','Confidential payroll?',None,'abstain'),
]
