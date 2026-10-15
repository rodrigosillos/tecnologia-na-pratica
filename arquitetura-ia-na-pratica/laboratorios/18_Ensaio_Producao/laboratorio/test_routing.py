import copy
from dataclasses import replace
from threading import Event
import unittest
from fixtures import ALICE,BOB
from job_worker import manuals,capture,compare
from resilience import Clock
from routing import (RoutePolicy,Model,Reply,SimulatedModels,registry,approvals,
                     OPERATION,rejection,fits,validate_rows,route)
from routing_exercises import exercise21,exercise22
from routing_scenarios import run_case,NAMES,cohort


class RoutingTests(unittest.TestCase):
    def setUp(self):self.store=manuals();self.models=registry()
    def tearDown(self):self.store.close()
    def run_route(self,**kw):return route(self.store,ALICE,**kw)
    def packet(self):
        saved=[capture(self.store,ALICE,d,'pt-BR') for d in ('manual-a','manual-b')]
        rows=compare(saved)['rows']
        return dict(schema_version='1.0',rows=copy.deepcopy(rows)),rows

    def test_private_cheapest_is_excluded(self):
        r=self.run_route();self.assertEqual(r['model'],'compact')
        self.assertEqual(r['trace'][0]['reason'],'privacy')
    def test_explicit_external_zone_can_enable_remote(self):
        r=self.run_route(policy=RoutePolicy(zones=('local','external')))
        self.assertEqual(r['model'],'remote');self.assertEqual(r['charged_units'],10)
    def test_no_approved_model(self):
        r=self.run_route(approved=());self.assertEqual(r['calls'],0)
        self.assertEqual(r['state'],'abstain')
    def test_revision_requires_new_approval(self):
        models=[replace(self.models[0],revision='r2')]
        r=self.run_route(models=models);self.assertEqual(r['calls'],0)
        self.assertEqual(r['trace'][0]['reason'],'unapproved')
    def test_quality_scoped_to_language(self):
        ap=approvals(self.models)-{('compact','r1',OPERATION,'en-US')}
        self.assertEqual(self.run_route(language='en-US',approved=ap)['model'],'large')
        self.assertEqual(self.run_route(language='pt-BR',approved=ap)['model'],'compact')
    def test_language_capability_is_hard(self):
        m=replace(self.models[0],languages=('pt-BR',))
        self.assertEqual(rejection(m,'en-US',1,RoutePolicy(),approvals(self.models)),'language')
    def test_operation_capability_is_hard(self):
        m=replace(self.models[0],capabilities=('summarize',))
        r=self.run_route(models=(m,));self.assertEqual(r['trace'][0]['reason'],'capability')
    def test_context_skip_without_call(self):
        r=run_case('context_skip');self.assertEqual(r['models'],['large'])
    def test_context_boundary(self):
        m=self.models[0];p=RoutePolicy();a=approvals(self.models)
        self.assertIsNone(rejection(m,'pt-BR',m.context_bytes,p,a))
        self.assertEqual(rejection(m,'pt-BR',m.context_bytes+1,p,a),'context')
    def test_disabled_is_not_quality_approval(self):
        r=self.run_route(disabled=('compact','large'))
        self.assertEqual(r['calls'],0);self.assertEqual(r['state'],'abstain')
    def test_transient_fallback(self):
        r=run_case('transient_fallback');self.assertEqual(r['models'],['compact','large'])
        self.assertEqual((r['units'],r['virtual_ms'],r['state']),(90,150,'full'))
    def test_invalid_output_fallback(self):
        self.assertEqual(run_case('invalid_fallback')['state'],'full')
    def test_wrong_fact_fallback(self):
        self.assertEqual(run_case('wrong_fallback')['models'],['compact','large'])
    def test_refusal_is_terminal(self):
        r=run_case('refusal');self.assertEqual(r['models'],['compact'])
        self.assertEqual(r['reason'],'refusal')
    def test_fatal_configuration_is_terminal(self):
        a=SimulatedModels({'compact':Reply('fatal')});r=self.run_route(adapter=a)
        self.assertEqual(a.calls,['compact']);self.assertEqual(r['reason'],'fatal')
    def test_timeout_consumes_permit(self):
        r=run_case('timeout_fallback');self.assertEqual((r['units'],r['virtual_ms']),(90,170))
    def test_timeout_exact_boundary(self):
        a=SimulatedModels({'compact':Reply(elapsed_ms=60)})
        r=self.run_route(adapter=a,policy=RoutePolicy(max_calls=1))
        self.assertEqual(r['state'],'abstain');self.assertEqual(r['trace'][1]['reason'],'timeout')
    def test_combined_budget_not_per_model(self):
        r=exercise21();self.assertEqual(r,dict(state='abstain',calls=['compact'],units=20))
    def test_budget_exact_boundary(self):
        a=SimulatedModels({'compact':Reply('transient')})
        self.assertEqual(self.run_route(adapter=a,policy=RoutePolicy(max_units=90))['state'],'full')
    def test_zero_budget_no_call(self):
        self.assertEqual(self.run_route(policy=RoutePolicy(max_units=0))['calls'],0)
    def test_partial_is_not_full(self):
        self.assertEqual(exercise22(),dict(state='partial',missing=['shipping'],delta=-15,units=20))
    def test_partial_disallowed(self):
        r=run_case('partial_disabled');self.assertEqual((r['state'],r['rows']),('abstain',0))
    def test_partial_promoted_to_full(self):
        r=run_case('partial_then_full');self.assertEqual((r['rows'],r['models']),(2,['compact','large']))
    def test_refusal_discards_earlier_partial(self):
        a=SimulatedModels({'compact':Reply('partial'),'large':Reply('refusal',90)})
        r=self.run_route(adapter=a);self.assertEqual((r['state'],r['rows']),('abstain',[]))
    def test_finalization_included(self):
        r=self.run_route();self.assertEqual(r['elapsed_ms'],60)
    def test_fallback_must_fit_remaining_deadline(self):
        r=run_case('deadline');self.assertEqual((r['models'],r['state']),(['compact'],'partial'))
    def test_external_deadline_not_reset(self):
        c=Clock();c.advance(100)
        r=self.run_route(clock=c,deadline_ms=179)
        self.assertEqual(r['calls'],0);self.assertEqual(c.now,100)
    def test_exact_deadline_reservation(self):
        r=self.run_route(policy=RoutePolicy(budget_ms=80))
        self.assertEqual(r['state'],'full');self.assertLessEqual(r['elapsed_ms'],80)
    def test_expired_before_admission(self):
        self.assertEqual(self.run_route(deadline_ms=0)['reason'],'deadline')
    def test_call_limit_counts_distinct_attempts(self):
        a=SimulatedModels({'compact':Reply('invalid')})
        r=self.run_route(adapter=a,policy=RoutePolicy(max_calls=1))
        self.assertEqual(r['calls'],1);self.assertEqual(r['state'],'abstain')
    def test_cancel_before_call(self):
        token=Event();token.set();r=self.run_route(cancel=token)
        self.assertEqual((r['calls'],r['reason']),(0,'cancelled'))
    def test_cancel_during_call_still_charges(self):
        token=Event();a=SimulatedModels(after_call=lambda _:token.set())
        r=self.run_route(cancel=token,adapter=a)
        self.assertEqual((r['charged_units'],r['reason'],r['rows']),(20,'cancelled',[]))
    def test_revoke_before_fallback(self):
        a=SimulatedModels({'compact':Reply('transient')},
                          lambda _:self.store.set_acl('acme','manual-a',['admin']))
        r=self.run_route(adapter=a);self.assertEqual(a.calls,['compact'])
        self.assertEqual(r['reason'],'source_changed')
    def test_revoke_before_return(self):
        r=run_case('revoked');self.assertEqual((r['state'],r['rows']),('abstain',0))
    def test_other_tenant_no_call(self):
        r=route(self.store,BOB);self.assertEqual((r['calls'],r['reason']),(0,'source_unavailable'))
    def test_missing_source_no_call(self):
        r=self.run_route(documents=('manual-a','missing'));self.assertEqual(r['calls'],0)
    def test_no_raw_payload_in_trace(self):
        r=self.run_route();self.assertNotIn('45',str(r['trace']))
        self.assertNotIn('alice',str(r['trace']));self.assertNotIn('manual-a',str(r['trace']))
    def test_extra_field_rejected(self):
        packet,rows=self.packet();packet['confidence']=1.0
        self.assertIsNone(validate_rows(packet,rows))
    def test_duplicate_topic_rejected(self):
        packet,rows=self.packet();packet['rows']=[rows[0],rows[0]]
        self.assertIsNone(validate_rows(packet,rows))
    def test_bool_not_integer(self):
        packet,rows=self.packet();packet['rows'][1]['delta']=False
        self.assertIsNone(validate_rows(packet,rows))
    def test_unknown_topic_rejected(self):
        packet,rows=self.packet();packet['rows'][0]['topic']='invented'
        self.assertIsNone(validate_rows(packet,rows))
    def test_bad_arithmetic_rejected(self):
        packet,rows=self.packet();packet['rows'][0]['delta']=15
        self.assertIsNone(validate_rows(packet,rows))
    def test_schema_version_rejected(self):
        packet,rows=self.packet();packet['schema_version']='2.0'
        self.assertIsNone(validate_rows(packet,rows))
    def test_empty_rows_not_partial(self):
        packet,rows=self.packet();packet['rows']=[]
        self.assertIsNone(validate_rows(packet,rows))
    def test_reorder_rows_normalized(self):
        packet,rows=self.packet();packet['rows'].reverse()
        self.assertEqual(validate_rows(packet,rows),rows)
    def test_duplicate_registry_id_rejected(self):
        with self.assertRaises(ValueError):self.run_route(models=(self.models[0],self.models[0]))
    def test_invalid_limits_rejected(self):
        for args in (dict(max_units=True),dict(max_calls=-1),dict(budget_ms=10),dict(allow_partial=1)):
            with self.subTest(args=args),self.assertRaises(ValueError):RoutePolicy(**args)
    def test_bad_model_charge_rejected(self):
        with self.assertRaises(ValueError):self.run_route(models=(replace(self.models[0],units=-1),))
    def test_bilingual_scenarios_equivalent(self):
        for name in NAMES:
            with self.subTest(name=name):
                a=run_case(name,'pt-BR');b=run_case(name,'en-US')
                a.pop('language');b.pop('language');self.assertEqual(a,b)
    def test_sources_and_translation_are_preserved(self):
        r=self.run_route(language='en-US')
        self.assertEqual(r['sources'][0]['document'],'manual-a')
        self.assertIn('Returns:',r['sources'][0]['quotes'][0])
    def test_cohort_arithmetic(self):
        result=cohort()
        self.assertEqual(result['cascade'],dict(requests=10,full=10,calls=12,units=340,total_virtual_ms=780))
        self.assertEqual(result['large_only'],dict(requests=10,full=10,calls=10,units=700,total_virtual_ms=1100))


if __name__=='__main__':unittest.main()
