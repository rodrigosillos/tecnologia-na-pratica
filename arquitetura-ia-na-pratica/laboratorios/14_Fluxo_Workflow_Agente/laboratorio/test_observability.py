import copy,json,unittest
from observability import (safe_attributes,percentile,histogram,merge_histograms,
    burn_rate,Trace,MemoryExporter,VirtualClock,Measurements,stage_totals)
from observe_scenarios import run_case,regression,NAMES
from observe_exercises import exercise25,exercise26,page_decision


class SignalTests(unittest.TestCase):
    def test_allowlist(self):
        self.assertEqual(safe_attributes({'language':'pt-BR','release':'r1'}),({'language':'pt-BR','release':'r1'},0))
    def test_unknown_key(self):
        self.assertEqual(safe_attributes({'prompt':'secret'}),({},1))
    def test_secret_known_key(self):
        self.assertEqual(safe_attributes({'model':'secret'}),({},1))
    def test_attribute_object(self):
        self.assertEqual(safe_attributes({'model':['compact']}),({},1))
    def test_parent_and_duration(self):
        t=Trace('a')
        with t.span('request'):
            t.clock.advance(2)
            with t.span('model.call'):t.clock.advance(5)
        self.assertEqual(t.spans[1]['parent_id'],t.spans[0]['span_id'])
        self.assertEqual([s['end_ms']-s['start_ms'] for s in t.spans],[7,5])
    def test_exception_closes(self):
        t=Trace('a')
        with self.assertRaises(RuntimeError):
            with t.span('request'):
                with t.span('model.call'):raise RuntimeError('sensitive payload')
        self.assertEqual(t.stack,[])
        self.assertTrue(all(s['status']=='error' and s['end_ms']==0 for s in t.spans))
        self.assertNotIn('sensitive',json.dumps(t.spans))
    def test_fixed_names(self):
        with self.assertRaises(ValueError):
            with Trace('a').span('raw secret'):pass
    def test_bounded_attributes(self):
        t=Trace('a')
        with t.span('request',{'prompt':'secret','release':'r2'}):pass
        self.assertEqual(t.attributes_dropped,1)
        self.assertNotIn('secret',json.dumps(t.spans))
    def test_link(self):
        a=Trace('a');b=Trace('b')
        with b.span('job.run',links=[a.trace_id]):pass
        self.assertEqual(b.spans[0]['links'],[a.trace_id])
        self.assertIsNone(b.spans[0]['parent_id'])
    def test_bad_link(self):
        with self.assertRaises(ValueError):
            with Trace('a').span('job.run',links=['customer@example.test']):pass
    def test_cap(self):
        t=Trace('a',max_spans=1)
        with t.span('request'):
            with t.span('model.call'):t.clock.advance(7)
        self.assertEqual((len(t.spans),t.spans_dropped,t.stack),(1,1,[]))
    def test_bad_cap(self):
        for value in (0,-1,True):
            with self.assertRaises(ValueError):Trace('a',max_spans=value)
    def test_sampled_export(self):
        t=Trace('a')
        with t.span('request'):pass
        t.finish();self.assertEqual(len(t.exporter.traces),1)
    def test_unsampled(self):
        t=Trace('a',sampled=False)
        with t.span('request'):pass
        t.finish();self.assertEqual(t.exporter.traces,[])
    def test_export_failure(self):
        t=Trace('a',exporter=MemoryExporter(True));t.finish()
        self.assertEqual(t.export_failures,1)
    def test_open_span(self):
        t=Trace('a')
        with t.span('request'):
            with self.assertRaises(ValueError):t.finish()
    def test_export_snapshot(self):
        t=Trace('a')
        with t.span('request'):pass
        t.finish();t.spans.clear()
        self.assertEqual(len(t.exporter.traces[0]['spans']),1)
    def test_clock_validation(self):
        for value in (-1,1.5,True):
            with self.assertRaises(ValueError):VirtualClock().advance(value)
    def test_percentile_empty(self):self.assertIsNone(percentile([],.95))
    def test_percentile_rank(self):self.assertEqual(percentile([100,1,50,3],.5),3)
    def test_percentile_tail(self):self.assertEqual(percentile([1]*19+[900],.99),900)
    def test_percentile_bad_duration(self):
        for value in (-1,float('nan'),float('inf'),True,'1'):
            with self.assertRaises(ValueError):percentile([value],.95)
    def test_percentile_bad_p(self):
        for value in (0,-.1,1.1,float('nan')):
            with self.assertRaises(ValueError):percentile([1],value)
    def test_histogram_cumulative(self):
        h=histogram([0,25,26,900]);self.assertEqual(h['counts'],[2,3,3,3,3])
        self.assertEqual((h['infinity'],h['count'],h['sum']),(4,4,951))
    def test_histogram_merge(self):
        self.assertEqual(merge_histograms([histogram([10,1000]),histogram([100])]),histogram([10,1000,100]))
    def test_histogram_mismatch(self):
        with self.assertRaises(ValueError):merge_histograms([histogram([1]),histogram([2],(1,2))])
    def test_histogram_bad_bounds(self):
        for bounds in ((),(2,1),(1,1),(-1,2)):
            with self.assertRaises(ValueError):histogram([1],bounds)
    def test_burn_empty(self):self.assertIsNone(burn_rate(0,0))
    def test_burn_formula(self):self.assertEqual(burn_rate(60,1000),6)
    def test_burn_invalid(self):
        for args in ((-1,100),(101,100),(True,1),(1,2,1)):
            with self.assertRaises(ValueError):burn_rate(*args)


class ObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases={n:run_case(n,trace_output=True) for n in NAMES}
        cls.reg=regression()
    def row(self,name):return copy.deepcopy(self.cases[name][0])
    def test_base(self):
        r=self.row('baseline');self.assertEqual((r['duration_ms'],r['settled_units'],r['quality']),(102,24,'pass'))
    def test_warm(self):
        r=self.row('cached');self.assertEqual((r['duration_ms'],r['calls_started'],r['settled_units']),(23,0,4))
    def test_queue(self):
        r=self.row('queue_slow');self.assertEqual((r['duration_ms'],r['processing_ms']),(182,102))
    def test_sources(self):self.assertEqual(self.row('source_slow')['duration_ms'],210)
    def test_fallback(self):
        r=self.row('fallback');self.assertEqual((r['duration_ms'],r['calls_started'],r['settled_units']),(198,2,94))
    def test_unknown_attempt(self):
        r=self.row('unknown_cost');self.assertEqual((r['calls_started'],r['settled_units'],r['held_units']),(1,0,94))
    def test_partial_not_good(self):
        m=Measurements();m.add(self.row('partial'));self.assertEqual((m.summary()['full'],m.summary()['bad']),(0,1))
    def test_budget_no_model(self):self.assertEqual(self.row('budget')['calls_started'],0)
    def test_access_denominator(self):
        m=Measurements();m.add(self.row('access'));s=m.summary()
        self.assertEqual((s['requests'],s['eligible'],s['correct_denials']),(1,0,1));self.assertIsNone(s['burn'])
    def test_quality_missing(self):
        m=Measurements();m.add(self.row('quality_missing'));s=m.summary()
        self.assertEqual((s['full'],s['good'],s['unassessed_full']),(1,0,1))
    def test_export_down_business_same(self):
        a=self.row('baseline');b=self.row('export_down')
        for key in ('state','quality','duration_ms','settled_units'):self.assertEqual(a[key],b[key])
        self.assertEqual(b['export_failures'],1)
    def test_dedupe(self):
        m=Measurements();r=self.row('baseline');self.assertTrue(m.add(r));self.assertFalse(m.add(r))
        self.assertEqual(m.summary()['settled_units'],24)
    def test_conflict(self):
        m=Measurements();r=self.row('baseline');m.add(r);r['duration_ms']+=1
        with self.assertRaises(ValueError):m.add(r)
    def test_measurement_snapshot(self):
        m=Measurements();r=self.row('baseline');m.add(r);r['settled_units']=900
        self.assertEqual(m.summary()['settled_units'],24)
    def test_empty_summary(self):
        s=Measurements().summary();self.assertEqual(s['requests'],0);self.assertIsNone(s['p95_ms']);self.assertIsNone(s['units_per_full'])
    def test_stage_sum_sequential(self):
        for r,t in self.cases.values():self.assertEqual(sum(stage_totals(t).values()),r['duration_ms'])
    def test_regression_sample_independence(self):
        for v in self.reg.values():self.assertEqual((v['retained_traces'],v['summary']['requests']),(5,20))
    def test_regression_tail_cost(self):
        s=self.reg['regression']['summary'];self.assertEqual((s['p95_ms'],s['settled_units'],s['calls_started'],s['good']),(278,830,25,0))
    def test_queue_control(self):
        s=self.reg['queue_only']['summary'];self.assertEqual((s['p95_ms'],s['processing_p95_ms'],s['units_per_full']),(182,102,24))
    def test_all_languages(self):
        for n in NAMES:
            a=run_case(n,'pt-BR');b=run_case(n,'en-US')
            self.assertEqual({k:v for k,v in a.items() if k!='language'},{k:v for k,v in b.items() if k!='language'})
    def test_exercise25(self):
        r=exercise25();self.assertEqual((r['wrong_average'],r['pooled_p95'],r['pooled_p99']),(55,100,1000))
        self.assertEqual(r['histogram']['count'],40)
    def test_exercise26(self):
        r=exercise26();self.assertEqual(r['first_rates'],[3,10]);self.assertEqual(r['sustained_rates'],[6,10])
        self.assertEqual((r['first_decision'],r['sustained_decision']),('observe','page'))
    def test_alarm_no_data(self):self.assertEqual(page_decision((0,0),(0,0)),'no_data')
    def test_alarm_low_volume(self):self.assertEqual(page_decision((1,10),(1,10)),'insufficient_volume')
    def test_alarm_both_windows(self):self.assertEqual(page_decision((100,1000),(1,100)),'observe')
    def test_units_no_full(self):
        m=Measurements();m.add(self.row('unknown_cost'));s=m.summary()
        self.assertIsNone(s['units_per_full']);self.assertEqual(s['held_units'],94)


if __name__=='__main__':unittest.main()
