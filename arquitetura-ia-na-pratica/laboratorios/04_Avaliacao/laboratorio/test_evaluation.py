import ast, copy, json, tempfile, unittest
from dataclasses import replace, fields
from pathlib import Path
from systems import Request, System
from evaluation import (ROOT,load_cases,task_passes,ratio,percentile,run_suite,
    summarize,gate,bootstrap_delta,paired_groups,manifest,review_packet,decision)
from solutions import exercise7,exercise8


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load_cases()
        cls.base=run_suite('baseline')
        cls.fast=run_suite('fast_unsafe')

    def temporary_data(self,data):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            assert Path(d).resolve().parent==ROOT.resolve()
            p=Path(d)/'cases.json';p.write_text(json.dumps(data),encoding='utf-8')
            return load_cases(p)

    def test_fixture_24_rows_12_groups(self):
        self.assertEqual(len(self.data['cases']),24)
        self.assertEqual(len({c['group'] for c in self.data['cases']}),12)

    def test_no_empty_dataset(self):
        data=copy.deepcopy(self.data);data['cases']=[]
        with self.assertRaises(ValueError):self.temporary_data(data)

    def test_duplicate_ids_fail(self):
        data=copy.deepcopy(self.data);data['cases'].append(data['cases'][0])
        with self.assertRaises(ValueError):self.temporary_data(data)

    def test_translation_group_cannot_cross_split(self):
        data=copy.deepcopy(self.data);data['cases'][0]['split']='holdout'
        with self.assertRaises(ValueError):self.temporary_data(data)

    def test_unknown_label_fails(self):
        data=copy.deepcopy(self.data);data['cases'][0]['expected']['decision']='ok'
        with self.assertRaises(ValueError):self.temporary_data(data)

    def test_request_has_no_expected_field(self):
        self.assertEqual({x.name for x in fields(Request)}, {'tenant','role','topic','language'})

    def test_system_source_never_imports_evaluator(self):
        for p in [ROOT/'systems.py',*(ROOT/'app').glob('*.py')]:
            tree=ast.parse(p.read_text(encoding='utf-8'))
            imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
            self.assertNotIn('evaluation',imports)
            self.assertNotIn('cases.v1.json',p.read_text(encoding='utf-8'))

    def test_baseline_passes_authored_suite(self):
        self.assertTrue(self.base['gate']['passed'])
        self.assertEqual(self.base['summary']['task_passes'],24)

    def test_fast_failure_counts(self):
        m=self.fast['summary']
        self.assertEqual((m['task_passes'],m['exposures'],m['correct_answers']),(14,4,12))

    def test_fast_uses_old_return_document(self):
        row=next(r for r in self.fast['rows'] if r['id']=='returns_pt-BR')
        self.assertEqual(row['observed']['citation'],'acme-returns-v1')
        self.assertFalse(row['task_pass'])

    def test_no_leak_and_no_help_is_rejected(self):
        self.assertFalse(exercise7()['gate']['passed'])

    def test_cost_known_versus_unknown(self):
        m=run_suite('missing_meter')['summary']
        self.assertEqual(m['unknown_cost_cases'],18)
        self.assertIsNone(m['cost_per_correct_answer'])

    def test_baseline_cost_and_denominator(self):
        m=self.base['summary']
        self.assertEqual((m['eligible'],m['known_cost_microusd'],m['cost_per_correct_answer']),(18,11880,660))

    def test_empty_ratio_is_not_zero(self):self.assertIsNone(ratio(0,0))

    def test_p95_nearest_rank(self):
        self.assertEqual(percentile(list(range(1,25)),.95),23)
        self.assertIsNone(percentile([],.95))

    def test_exact_output_and_reference_both_matter(self):
        c=self.data['cases'][0];out=System('baseline').run(Request(**c['input']))
        self.assertTrue(task_passes(c['expected'],out))
        self.assertFalse(task_passes(c['expected'],replace(out,answer='15 days')))
        self.assertFalse(task_passes(c['expected'],replace(out,citation='acme-returns-v1')))

    def test_conflict_is_only_review_decision_not_action(self):
        c=next(c for c in self.data['cases'] if c['group']=='conflict')
        out=System('baseline').run(Request(**c['input']))
        self.assertEqual(decision(out),'human_review')
        self.assertIsNone(out.answer)

    def test_global_score_does_not_hide_missing_slice(self):
        policy=json.loads((ROOT/'policy.v1.json').read_text())
        slices=dict(self.base['slices']);del slices['tenant:zen']
        self.assertFalse(gate(self.base['summary'],slices,policy)['passed'])

    def test_exposure_blocks_otherwise_perfect_summary(self):
        m=dict(self.base['summary']);m['exposures']=1
        p=json.loads((ROOT/'policy.v1.json').read_text())
        self.assertIn('exposure',gate(m,self.base['slices'],p)['failures'])

    def test_paired_comparison_matches_case_ids(self):
        reordered=copy.deepcopy(self.fast);reordered['rows'].reverse()
        self.assertEqual(paired_groups(self.base,self.fast),paired_groups(self.base,reordered))

    def test_unpaired_comparison_fails(self):
        incomplete=copy.deepcopy(self.fast);incomplete['rows'].pop()
        with self.assertRaises(ValueError):paired_groups(self.base,incomplete)

    def test_bootstrap_seed_reproducible(self):
        self.assertEqual(bootstrap_delta(self.base,self.fast),bootstrap_delta(self.base,self.fast))

    def test_identity_comparison_zero(self):
        r=bootstrap_delta(self.base,self.base)
        self.assertEqual((r['lower'],r['upper'],r['delta']),(0,0,0))

    def test_manifest_contains_dataset_policy_and_runtime(self):
        keys=manifest()['sha256']
        self.assertIn('cases.v1.json',keys);self.assertIn('policy.v1.json',keys)
        self.assertIn('app/service.py',keys)

    def test_review_packet_remains_unrated(self):
        import csv
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            assert Path(d).resolve().parent==ROOT.resolve()
            p=Path(d);review_packet(p,{'baseline':self.base,'fast_unsafe':self.fast})
            with (p/'revisao_humana_pt.csv').open(encoding='utf-8-sig') as handle:
                rows=list(csv.DictReader(handle))
            self.assertEqual(len(rows),12)
            self.assertTrue(all(not r['verdict'] for r in rows))

    def test_solved_exercise8(self):
        self.assertEqual(exercise8()['paired_comparison']['groups'],12)


if __name__=='__main__':unittest.main()
