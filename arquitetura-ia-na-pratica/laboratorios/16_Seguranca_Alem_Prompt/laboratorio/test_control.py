import json,unittest
from threading import Event
from fixtures import ALICE
from job_worker import manuals
from control import (parse_action,unique_object,Limits,Meter,Halt,Session,
                     SimulatedPlanner,repeated,run,score)
from control_scenarios import run_case,comparison,NAMES
from control_exercises import exercise27,exercise28


class ActionTests(unittest.TestCase):
    def test_valid_read(self):self.assertEqual(parse_action('{"tool":"read","document":"manual-a"}')['document'],'manual-a')
    def test_valid_compare(self):self.assertEqual(parse_action('{"tool":"compare","left":"e1","right":"e2"}')['tool'],'compare')
    def test_valid_finish(self):self.assertEqual(parse_action('{"tool":"finish","result":"r1"}')['result'],'r1')
    def test_valid_stop(self):self.assertEqual(parse_action('{"tool":"stop","reason":"no_evidence"}')['tool'],'stop')
    def test_no_object_input(self):
        with self.assertRaises(ValueError):parse_action({'tool':'finish','result':'r1'})
    def test_size_bound(self):
        with self.assertRaises(ValueError):parse_action(' '*513)
    def test_bad_json(self):
        with self.assertRaises(ValueError):parse_action('{')
    def test_array(self):
        with self.assertRaises(ValueError):parse_action('[]')
    def test_duplicate_keys(self):
        with self.assertRaises(ValueError):parse_action('{"tool":"read","tool":"finish","result":"r1"}')
    def test_unknown_tool(self):
        with self.assertRaises(ValueError):parse_action('{"tool":"shell","command":"echo"}')
    def test_wrong_tool_type(self):
        with self.assertRaises(ValueError):parse_action('{"tool":[],"result":"r1"}')
    def test_extra_field(self):
        with self.assertRaises(ValueError):parse_action('{"tool":"read","document":"manual-a","tenant":"zen"}')
    def test_missing_field(self):
        with self.assertRaises(ValueError):parse_action('{"tool":"read"}')
    def test_empty_value(self):
        with self.assertRaises(ValueError):parse_action('{"tool":"read","document":""}')
    def test_long_value(self):
        with self.assertRaises(ValueError):parse_action(json.dumps({'tool':'read','document':'a'*65}))
    def test_nested_value(self):
        with self.assertRaises(ValueError):parse_action('{"tool":"read","document":{"name":"a"}}')
    def test_bad_reason(self):
        with self.assertRaises(ValueError):parse_action('{"tool":"stop","reason":"secret"}')
    def test_limits_type(self):
        for k in ('steps','units','ms','repeats'):
            with self.assertRaises(ValueError):Limits(**{k:True})
    def test_negative_limit(self):
        with self.assertRaises(ValueError):Limits(ms=-1)
    def test_repeat_limit_zero(self):
        with self.assertRaises(ValueError):Limits(repeats=0)
    def test_meter_exact(self):
        m=Meter(Limits(units=1,ms=5));m.spend(1,5);self.assertEqual((m.units,m.ms),(1,5))
    def test_meter_no_partial_budget(self):
        m=Meter(Limits(units=0))
        with self.assertRaisesRegex(Halt,'budget'):m.spend(1,5)
        self.assertEqual((m.units,m.ms),(0,0))
    def test_meter_no_partial_deadline(self):
        m=Meter(Limits(ms=4))
        with self.assertRaisesRegex(Halt,'deadline'):m.spend(1,5)
        self.assertEqual((m.units,m.ms),(0,0))
    def test_repeat_canonical(self):
        seen={};a={'tool':'read','document':'manual-a'}
        self.assertFalse(repeated(a,seen,2));self.assertFalse(repeated(dict(reversed(list(a.items()))),seen,2))
        self.assertTrue(repeated(a,seen,2))
    def test_empty_score(self):self.assertIsNone(score([])['units_per_complete'])


class ControlTests(unittest.TestCase):
    def setUp(self):self.store=manuals()
    def tearDown(self):self.store.close()
    def session(self,**kwargs):return Session(self.store,ALICE,**kwargs)
    def agent(self,script=(),**kwargs):return run(self.session(),'agent',planner=SimulatedPlanner(script),**kwargs)
    def test_workflow_complete(self):
        r=run(self.session());self.assertEqual((r['state'],r['units'],r['duration_ms'],r['steps']),('complete',4,15,4))
    def test_agent_complete(self):
        r=self.agent();self.assertEqual((r['state'],r['units'],r['duration_ms'],r['planning_calls']),('complete',12,43,4))
    def test_same_output(self):self.assertEqual(run(self.session())['output'],self.agent()['output'])
    def test_reverse_preserves_orientation(self):
        r=run(self.session(),'agent',planner=SimulatedPlanner(reverse=True))
        self.assertEqual(r['output']['rows'][0]['delta'],-15)
    def test_no_forged_result(self):
        r=self.agent([{'tool':'finish','result':'r1'}]);self.assertEqual(r['reason'],'evidence');self.assertIsNone(r['output'])
    def test_finish_extra_rows(self):
        r=self.agent([{'tool':'finish','result':'r1','rows':[]}]);self.assertEqual(r['reason'],'invalid_action')
    def test_compare_before_read(self):
        r=self.agent([{'tool':'compare','left':'e1','right':'e2'}]);self.assertEqual(r['reason'],'evidence')
    def test_same_handle(self):
        script=[{'tool':'read','document':d} for d in ('manual-a','manual-b')]+[{'tool':'compare','left':'e1','right':'e1'}]
        r=self.agent(script);self.assertEqual(r['reason'],'evidence')
    def test_reversed_comparison_rejected(self):
        script=[{'tool':'read','document':d} for d in ('manual-a','manual-b')]+[{'tool':'compare','left':'e2','right':'e1'}]
        self.assertEqual(self.agent(script)['reason'],'evidence')
    def test_scope(self):
        r=self.agent([{'tool':'read','document':'payroll'}]);self.assertEqual(r['reason'],'scope');self.assertEqual(r['events'],[])
    def test_repeated(self):
        r=self.agent([{'tool':'read','document':'manual-a'}]*3)
        self.assertEqual((r['reason'],r['steps'],r['tool_calls'],r['units']),('repeated',3,2,8))
    def test_transient_both(self):
        for mode,cost,ms in [('workflow',5,20),('agent',15,55)]:
            r=run(self.session(fail_reads=1),mode);self.assertEqual((r['state'],r['units'],r['duration_ms']),('complete',cost,ms))
    def test_persistent_read_stops(self):
        r=run(self.session(fail_reads=3),'agent');self.assertEqual(r['reason'],'no_evidence');self.assertIsNone(r['output'])
    def test_zero_steps(self):
        r=self.agent(limits=Limits(steps=0));self.assertEqual((r['reason'],r['planning_calls']),('steps',0))
    def test_step_exhaustion(self):
        r=self.agent(limits=Limits(steps=3));self.assertEqual(r['reason'],'steps');self.assertIsNone(r['output'])
    def test_budget_before_plan(self):
        r=self.agent(limits=Limits(units=1));self.assertEqual((r['reason'],r['units'],r['planning_calls']),('budget',0,0))
    def test_budget_after_plan(self):
        r=self.agent(limits=Limits(units=2));self.assertEqual((r['reason'],r['units'],r['tool_calls']),('budget',2,0))
    def test_deadline(self):
        r=self.agent(limits=Limits(ms=14));self.assertEqual((r['reason'],r['duration_ms']),('deadline',12))
    def test_cancel_before_plan(self):
        e=Event();e.set();r=self.agent(cancel=e);self.assertEqual((r['reason'],r['units']),('cancelled',0))
    def test_cancel_after_plan(self):
        e=Event()
        class Planner:
            def next(self,view):e.set();return '{"tool":"read","document":"manual-a"}'
        r=run(self.session(),'agent',planner=Planner(),cancel=e)
        self.assertEqual((r['reason'],r['tool_calls'],r['units']),('cancelled',0,2))
    def test_cancel_before_tool(self):
        e=Event();r=self.agent(cancel=e,before_action=lambda a,s:e.set())
        self.assertEqual((r['tool_calls'],r['units']),(0,2))
    def test_planner_exception(self):
        class Planner:
            def next(self,view):raise RuntimeError('private secret')
        r=run(self.session(),'agent',planner=Planner());self.assertEqual(r['reason'],'planner_error')
        self.assertNotIn('private secret',json.dumps(r))
    def test_view_isolated(self):
        class Planner:
            def next(self,view):view['remaining'].clear();return '{"tool":"finish","result":"r1"}'
        s=self.session();r=run(s,'agent',planner=Planner());self.assertEqual(r['reason'],'evidence');self.assertEqual(len(s.view()['remaining']),2)
    def test_session_once(self):
        s=self.session();run(s)
        with self.assertRaises(ValueError):run(s)
    def test_language(self):
        with self.assertRaises(ValueError):self.session(language='xx')
    def test_duplicate_documents(self):
        with self.assertRaises(ValueError):self.session(documents=('manual-a','manual-a'))
    def test_invalid_mode(self):
        with self.assertRaises(ValueError):run(self.session(),'free')
    def test_workflow_no_planner(self):
        with self.assertRaises(ValueError):run(self.session(),planner=SimulatedPlanner())
    def test_logs_no_body(self):
        r=self.agent();self.assertNotIn('Devolução',json.dumps(r['events']))
        self.assertTrue(all(set(e)=={'step','tool','status'} for e in r['events']))
    def test_revoked(self):self.assertEqual(run_case('revoked')['reason'],'stale')
    def test_revised(self):self.assertEqual(run_case('revised')['reason'],'stale')
    def test_other_tenant(self):self.assertEqual(run_case('other_tenant')['reason'],'unavailable')
    def test_comparison(self):
        c=comparison();a=c['agent']['summary'];w=c['workflow']['summary']
        self.assertEqual((w['units'],a['units'],w['complete'],a['complete']),(42,126,10,10))
        self.assertEqual((w['p95_ms'],a['p95_ms']),(20,55))
    def test_exercise27(self):
        r=exercise27();self.assertEqual((r['extra_units'],r['extra_completions']),(84,0))
    def test_exercise28(self):
        r=exercise28();self.assertEqual(r['repeat_flags'],[False,False,True]);self.assertTrue(r['outputs_absent'])
    def test_language_equivalence(self):
        for name in NAMES:
            a=run_case(name,'pt-BR');b=run_case(name,'en-US')
            self.assertEqual({k:v for k,v in a.items() if k!='language'},{k:v for k,v in b.items() if k!='language'})


if __name__=='__main__':unittest.main()
