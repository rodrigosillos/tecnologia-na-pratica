import copy
import json
import unittest
from boundary import (toy_tokens, plan_context, cosine, decode_strict,
    usage_cost, prepare_context, finalize, run_case, summarize, evaluate)
from chapter1 import read_data


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.data = read_data()
        self.case = self.data['cases'][0]
        self.docs, _ = prepare_context(self.case, self.data['documents'])
        self.payload = {'status':'answer', 'fact_id':'return_30d',
                        'citation':'acme-returns-v2', 'reason':None}
        self.event = {'state':'completed', 'chunks':[json.dumps(self.payload)],
                      'usage':{'input_tokens':180, 'output_tokens':50},
                      'first_ms':80, 'end_ms':240}

    def decide(self):
        return finalize(self.event, self.case, self.docs)[0]

    def test_toy_roundtrip_unicode_and_empty(self):
        for s in ('', 'refund', 'reembolso', 'café', 'cafe\u0301', '🤖'):
            self.assertEqual(b''.join(toy_tokens(s)).decode('utf-8'), s)

    def test_toy_counts_are_not_character_counts(self):
        self.assertEqual([len(toy_tokens(s)) for s in
                          ('refund','reembolso','café','cafe\u0301')],
                         [1,8,5,6])

    def test_context_reservation_and_no_input_mutation(self):
        chunks=[{'id':'A','tokens':1200},{'id':'B','tokens':1000},
                {'id':'C','tokens':900}]
        before=copy.deepcopy(chunks)
        p=plan_context(900,chunks)
        self.assertEqual((p['selected'],p['input_tokens'],p['slack']),
                         (['A','B'],3100,356))
        self.assertEqual(chunks,before)
        self.assertEqual(plan_context(900,chunks,output=1024)['selected'],['A'])

    def test_context_exact_fit_and_skip_whole_chunks(self):
        p=plan_context(5,[{'id':'big','tokens':6},{'id':'fit','tokens':5}],
                       limit=10,output=0,margin=0)
        self.assertEqual(p['selected'],['fit'])
        self.assertEqual(p['slack'],0)

    def test_context_rejects_bad_numbers_overflow_and_duplicates(self):
        for value in (-1,True,3.5):
            with self.assertRaises(ValueError):plan_context(value,[])
        with self.assertRaises(ValueError):plan_context(4000,[])
        with self.assertRaises(ValueError):
            plan_context(0,[{'id':'x','tokens':1},{'id':'x','tokens':2}])

    def test_cosine_is_not_authorization(self):
        self.assertAlmostEqual(cosine([1,0],[.8,.6]),.8)
        self.assertGreater(cosine([1,0],[.98,.2]),.97)
        with self.assertRaises(ValueError):cosine([1,0],[0,0])
        with self.assertRaises(ValueError):cosine([1,0],[1])
        with self.assertRaises(ValueError):cosine([1,0],[float('nan'),0])

    def test_strict_parser_duplicate_keys_and_nonfinite(self):
        for text in ('{"a":1,"a":2}','{"a":NaN}','{"a":Infinity}'):
            with self.assertRaises(ValueError):decode_strict(text)

    def test_incomplete_even_with_valid_json(self):
        self.event['state']='incomplete'
        self.assertEqual(self.decide(),'incomplete')

    def test_schema_and_json_are_distinct_failures(self):
        for raw,expected in [('[]','invalid_schema'),('{}','invalid_schema'),
                             ('{"status":','invalid_json')]:
            self.event['chunks']=[raw]
            self.assertEqual(self.decide(),expected)
        self.payload['reason']=[]
        self.event['chunks']=[json.dumps(self.payload)]
        self.assertEqual(self.decide(),'invalid_schema')

    def test_same_json_shape_wrong_fact(self):
        self.payload['fact_id']='return_999d'
        self.event['chunks']=[json.dumps(self.payload)]
        self.assertEqual(self.decide(),'unsupported')

    def test_citation_must_have_been_sent(self):
        self.assertEqual(finalize(self.event,self.case,[])[0],'unsupported')
        self.assertEqual(self.decide(),'accepted')

    def test_unauthorized_and_stale_docs_rejected_again(self):
        for docid,fact in [('acme-returns-v1','return_15d'),
                           ('zen-refund-v1','refund_2d')]:
            self.payload.update(citation=docid,fact_id=fact)
            self.event['chunks']=[json.dumps(self.payload)]
            self.assertEqual(finalize(self.event,self.case,
                                     self.data['documents'])[0],'unsupported')

    def test_oracle_never_controls_boundary(self):
        before=self.decide()
        self.case['expected_fact']='fabricated_oracle'
        self.assertEqual(self.decide(),before)

    def test_provider_refusal_is_not_business_abstention(self):
        self.event['state']='refused'
        self.assertEqual(self.decide(),'refused')
        self.assertIsNone(finalize(self.event,self.case,self.docs)[1])

    def test_unavailable_usage_unknown_not_zero(self):
        self.event.update(state='unavailable',usage=None)
        row=run_case({'id':'x','event':self.event},self.case,
                     self.data['documents'])
        self.assertIsNone(row['cost_microusd'])
        self.assertEqual(row['decision'],'unavailable')

    def test_no_evidence_never_reads_event(self):
        missing=next(c for c in self.data['cases'] if c['id']=='u02')
        row=run_case({'id':'x'},missing,self.data['documents'])
        self.assertFalse(row['attempted'])
        self.assertEqual(row['decision'],'business_abstention')
        self.assertEqual(row['cost_microusd'],0)

    def test_whitespace_and_field_order_do_not_change_meaning(self):
        original=finalize(self.event,self.case,self.docs)
        raw=json.dumps(dict(reversed(list(self.payload.items()))),indent=2)
        self.event['chunks']=[raw[:10],raw[10:]]
        self.assertEqual(finalize(self.event,self.case,self.docs),original)

    def test_cost_deadline_and_size_are_enforced(self):
        self.event['end_ms']=2501
        self.assertEqual(self.decide(),'late')
        self.event['end_ms']=2500
        self.assertEqual(self.decide(),'accepted')
        self.event['usage']['output_tokens']=200
        self.assertEqual(self.decide(),'over_budget')
        self.event['usage']=None
        self.assertEqual(self.decide(),'unknown_cost')
        self.event['chunks']=[' '*8193]
        self.assertEqual(self.decide(),'oversized')

    def test_accounting_unknown_and_zero_denominator(self):
        self.assertEqual(usage_cost({'input_tokens':180,'output_tokens':50}),660)
        self.assertIsNone(usage_cost(None))
        self.assertIsNone(summarize([])['microusd_per_accepted'])
        r=evaluate()['summary']
        self.assertEqual(r['known_cost_microusd'],6150)
        self.assertEqual(r['unmetered_attempts'],1)
        self.assertIsNone(r['total_cost_microusd'])
        self.assertIsNone(r['microusd_per_accepted'])

    def test_failure_matrix_and_sanitized_results(self):
        report=evaluate()
        self.assertEqual(report['summary']['attempted'],11)
        self.assertEqual(report['summary']['decisions'],{
            'accepted':2,'unsupported':4,'invalid_json':1,
            'invalid_schema':1,'incomplete':1,'refused':1,
            'unavailable':1,'business_abstention':1})
        for row in report['rows']:
            if row['decision'] not in ('accepted','business_abstention'):
                self.assertIsNone(row['response'])
            if row['decision']=='accepted':
                self.assertTrue(row['oracle_correct_if_accepted'])


if __name__=='__main__':unittest.main()
