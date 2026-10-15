import copy
import json
import unittest
from threading import Event
from fixtures import seeded, ALICE, BOB
from retrieval import answer
from contract import (ContractError, MAX_FRAME, MAX_STREAM, encode_event,
                      strict_json, validate_event, validate_request)
from service import open_stream, events
from client import Client, consume, fragments
from scenarios import request, wire, run_scenarios
from solutions import exercise15, exercise16

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.store=seeded();self.req=request()
        self.frames=wire(self.store)
        self.events=list(events(self.store,ALICE,self.req))
    def tearDown(self):self.store.close()
    def client(self, frames=None, ids=None):
        return consume(self.frames if frames is None else frames,'demo-08',ids or ['q1','q2'])
    def test_valid_complete(self):
        c=self.client();self.assertEqual(c.state,'completed');self.assertEqual(c.result['outcome'],'complete')
    def test_one_byte_fragments(self):self.assertEqual(self.client(fragments(b''.join(self.frames),1)).result,self.client().result)
    def test_all_bytes_in_one_chunk(self):self.assertEqual(self.client([b''.join(self.frames)]).result,self.client().result)
    def test_truncated_before_result(self):
        with self.assertRaises(ContractError):self.client(self.frames[:-1])
    def test_truncated_inside_frame(self):
        with self.assertRaises(ContractError):self.client([b''.join(self.frames)[:-3]])
    def test_empty_stream(self):
        with self.assertRaises(ContractError):self.client([])
    def test_duplicate_frame(self):
        with self.assertRaises(ContractError):self.client(self.frames[:2]+self.frames[1:])
    def test_sequence_gap(self):
        with self.assertRaises(ContractError):self.client(self.frames[:1]+self.frames[2:])
    def test_missing_accepted(self):
        with self.assertRaises(ContractError):self.client(self.frames[1:])
    def test_event_after_terminal(self):
        with self.assertRaises(ContractError):self.client(self.frames+self.frames[-1:])
    def test_request_mismatch(self):
        with self.assertRaises(ContractError):consume(self.frames,'other',['q1','q2'])
    def test_missing_query_item(self):
        with self.assertRaises(ContractError):self.client(ids=['q1'])
    def test_query_order(self):
        with self.assertRaises(ContractError):self.client(ids=['q2','q1'])
    def test_boolean_sequence(self):
        event=copy.deepcopy(self.events[0]);event['seq']=True
        with self.assertRaises(ContractError):validate_event(event)
    def test_unknown_event(self):
        event=copy.deepcopy(self.events[0]);event['kind']='delta'
        with self.assertRaises(ContractError):validate_event(event)
    def test_unknown_version(self):
        event=copy.deepcopy(self.events[0]);event['schema_version']='2.0'
        with self.assertRaises(ContractError):validate_event(event)
    def test_extra_field(self):
        event=copy.deepcopy(self.events[0]);event['private_document']='secret'
        with self.assertRaises(ContractError):validate_event(event)
    def test_nonanswer_text(self):
        e=copy.deepcopy(self.events[-1]);e['data']['items'][0]['status']='abstain'
        with self.assertRaises(ContractError):validate_event(e)
    def test_wrong_outcome(self):
        e=copy.deepcopy(self.events[-1]);e['data']['outcome']='partial'
        with self.assertRaises(ContractError):validate_event(e)
    def test_quote_mismatch(self):
        e=copy.deepcopy(self.events[-1]);e['data']['items'][0]['citations'][0]['quote']='invented'
        with self.assertRaises(ContractError):validate_event(e)
    def test_duplicate_json_key(self):
        with self.assertRaises(ContractError):strict_json('{"a":1,"a":2}')
    def test_nonfinite_json(self):
        with self.assertRaises(ContractError):strict_json('{"a":NaN}')
    def test_frame_utf8(self):
        with self.assertRaises(ContractError):self.client([b'event: accepted\nid: x/1\ndata: \xff\n\n'])
    def test_frame_kind_mismatch(self):
        with self.assertRaises(ContractError):self.client([self.frames[0].replace(b'event: accepted',b'event: result')])
    def test_frame_id_mismatch(self):
        with self.assertRaises(ContractError):self.client([self.frames[0].replace(b'id: demo-08/1',b'id: demo-08/2')])
    def test_large_unfinished_frame(self):
        with self.assertRaises(ContractError):self.client([b'x'*(MAX_FRAME+1)])
    def test_large_stream(self):
        with self.assertRaises(ContractError):self.client([b'x'*(MAX_STREAM+1)])
    def test_invalid_request_does_not_start_engine(self):
        def broken(*args):raise AssertionError('must not run')
        status,headers,body=open_stream(self.store,ALICE,b'{}',engine=broken)
        self.assertEqual(status,400);self.assertEqual(headers['Content-Type'],'application/problem+json')
        self.assertEqual(json.loads(b''.join(body))['status'],status)
    def test_unsupported_media(self):self.assertEqual(open_stream(self.store,ALICE,b'{}','text/plain')[0],415)
    def test_large_request(self):self.assertEqual(open_stream(self.store,ALICE,b'x'*4097)[0],413)
    def test_actor_is_not_user_input(self):
        self.req['actor']='ana'
        with self.assertRaises(ContractError):validate_request(self.req)
    def test_duplicate_query_ids(self):
        self.req['queries'][1]['id']='q1'
        with self.assertRaises(ContractError):validate_request(self.req)
    def test_empty_question(self):
        self.req['queries'][0]['text']='  '
        with self.assertRaises(ContractError):validate_request(self.req)
    def test_too_many_queries(self):
        self.req['queries']*=2
        with self.assertRaises(ContractError):validate_request(self.req)
    def test_progress_contains_no_answer(self):
        for e in self.events:
            if e['kind']=='progress':self.assertEqual(set(e['data']),{'stage'})
    def test_cancel_before_engine(self):
        token=Event();token.set()
        def broken(*args):raise AssertionError('must not run')
        c=self.client(wire(self.store,cancel=token,engine=broken))
        self.assertEqual(c.state,'cancelled');self.assertIsNone(c.result)
    def test_cancel_after_compute(self):
        token=Event();c=self.client(wire(self.store,cancel=token,before_release=token.set))
        self.assertEqual(c.state,'cancelled');self.assertIsNone(c.result)
    def test_late_cancel_cannot_retract(self):
        token=Event();frames=wire(self.store,cancel=token);token.set()
        self.assertEqual(self.client(frames).state,'completed')
    def test_exception_redacted(self):
        def broken(*args):raise RuntimeError('SECRET private payroll')
        frames=wire(self.store,engine=broken)
        self.assertNotIn(b'SECRET',b''.join(frames));self.assertEqual(self.client(frames).state,'failed')
    def test_invalid_engine_response_is_error_without_gap(self):
        def malformed(*args):return dict(status='banana',text=None,citations=[])
        c=self.client(wire(self.store,engine=malformed));self.assertEqual(c.state,'failed')
    def test_forged_citation_is_not_released(self):
        def forged(*args):
            r=answer(*args);r['citations'][0]['text']='invented';r['text']='invented';return r
        c=self.client(wire(self.store,engine=forged));self.assertEqual(c.result['outcome'],'no_answer')
    def test_partial_retains_only_authorized_answer(self):
        def revoke():self.store.set_acl('acme','returns',['admin'])
        c=self.client(wire(self.store,before_release=revoke))
        self.assertEqual([i['status'] for i in c.result['items']],['abstain','answer'])
        self.assertNotIn('45',json.dumps(c.result))
    def test_other_tenant(self):
        req=request(['Prazo de devolução?'])
        body=json.dumps(req).encode();_,_,stream=open_stream(self.store,BOB,body)
        c=consume(stream,'demo-08',['q1']);self.assertEqual(c.result['items'][0]['text'],'Devolução: prazo de 7 dias.')
    def test_no_private_reason_in_public_result(self):
        c=self.client(wire(self.store,request(['Folha pagamento?'])),ids=['q1'])
        self.assertEqual(c.result['outcome'],'no_answer');self.assertNotIn('reason',json.dumps(c.result))
    def test_exercise15(self):self.assertEqual(exercise15()['truncated'],'rejected')
    def test_exercise16(self):self.assertEqual(exercise16()['revoked_item'],'abstain')
    def test_scenarios_bilingual_expected(self):
        data=run_scenarios();self.assertEqual(len(data['runs']),14)
        expected={'complete':('completed','complete',2),'partial':('completed','partial',1),
                  'clarify':('completed','no_answer',0),'revoked':('completed','partial',1),
                  'cancelled':('cancelled',None,0),'error':('failed',None,0),'truncated':('protocol_error',None,0)}
        for row in data['runs']:
            self.assertEqual((row['state'],row['outcome'],row['answers']),expected[row['case']],row)

if __name__=='__main__':unittest.main()
