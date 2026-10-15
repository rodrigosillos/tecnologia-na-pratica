from dataclasses import replace
import ast
import json
from pathlib import Path
import unittest
from adapters import JsonRepository, ManualClock, ROOT, StubGenerator
from contracts import Completion, DependencyFailure, Principal, Query, Usage
from policy import strict_json
from service import AnswerService
from settings import Settings
from solutions import exercise5, exercise6, TimedGenerator, SlowRepository


class ArchitectureTests(unittest.TestCase):
    def setUp(self):
        self.repo=JsonRepository(ROOT/'documents.json')
        self.clock=ManualClock()
        self.generator=TimedGenerator(self.clock,0)
        self.svc=AnswerService(self.repo,self.generator,self.clock,Settings())
        self.principal=Principal('acme','operator')

    def test_current_policy_not_expired(self):
        r=self.svc.answer(self.principal,Query('returns'))
        self.assertEqual((r.status,r.citation,r.cost_microusd),
                         ('answer','acme-returns-v2',660))
        self.assertIn('30 dias',r.answer)

    def test_locale_changes_rendering_not_evidence(self):
        pt=self.svc.answer(self.principal,Query('returns'))
        en=self.svc.answer(self.principal,Query('returns','en-US'))
        self.assertEqual(pt.citation,en.citation)
        self.assertNotEqual(pt.answer,en.answer)

    def test_no_evidence_does_not_call_generator(self):
        r=self.svc.answer(self.principal,Query('sunday'))
        self.assertEqual((r.status,r.cost_microusd),('abstain',0))
        self.assertEqual(self.generator.calls,0)

    def test_role_denied_does_not_confirm_document(self):
        r=self.svc.answer(self.principal,Query('payroll'))
        self.assertEqual(r.reason,'insufficient_evidence')
        self.assertIsNone(r.citation)
        self.assertEqual(self.generator.calls,0)

    def test_conflicting_evidence_abstains(self):
        self.assertEqual(self.svc.answer(self.principal,Query('emergency')).reason,
                         'conflicting_evidence')
        self.assertEqual(self.generator.calls,0)

    def test_core_rechecks_faulty_repository(self):
        docs=self.repo.documents
        class LeakyRepo:
            def search(self,*args):return docs
        self.svc.repository=LeakyRepo()
        r=self.svc.answer(self.principal,Query('refund'))
        self.assertEqual(r.citation,'acme-refund-v1')

    def test_tenant_switch_and_adapter_substitution(self):
        self.assertTrue(exercise5()['adapters_equivalent'])

    def test_deadline_shared_across_steps(self):
        self.assertEqual(exercise6()['late']['received_remaining_ms'],900)

    def test_zero_budget_prevents_generation(self):
        self.svc.settings=Settings(budget_microusd=0)
        self.assertEqual(self.svc.answer(self.principal,Query('returns')).reason,
                         'budget_exceeded')
        self.assertEqual(self.generator.calls,0)

    def test_output_failures_normalized_and_cost_retained(self):
        for mode,reason in [('malformed','invalid_output'),('unsupported','invalid_output'),
             ('incomplete','generation_incomplete'),('refused','generation_refused'),
             ('expensive','budget_exceeded'),('unknown_usage','usage_unknown')]:
            self.svc.generator=StubGenerator(mode)
            r=self.svc.answer(self.principal,Query('returns'))
            self.assertEqual(r.reason,reason)
            self.assertIsNone(r.answer)
            if mode=='unknown_usage':self.assertIsNone(r.cost_microusd)
            elif mode=='expensive':self.assertEqual(r.cost_microusd,1560)
            else:self.assertEqual(r.cost_microusd,660)

    def test_dependency_errors_are_not_abstentions(self):
        for mode in ('timeout','unavailable'):
            self.svc.generator=StubGenerator(mode)
            r=self.svc.answer(self.principal,Query('returns'))
            self.assertEqual(r.status,'error')
            self.assertIsNone(r.cost_microusd)

    def test_unexpected_bug_propagates_to_transport_boundary(self):
        self.svc.generator=StubGenerator('unexpected')
        with self.assertRaises(RuntimeError):self.svc.answer(self.principal,Query('returns'))

    def test_repository_failure_has_no_generation_cost(self):
        class Down:
            def search(self,*args):raise DependencyFailure('dependency_unavailable')
        self.svc.repository=Down()
        r=self.svc.answer(self.principal,Query('returns'))
        self.assertEqual((r.reason,r.cost_microusd),('dependency_unavailable',0))
        self.assertEqual(self.generator.calls,0)

    def test_configuration_fails_early(self):
        for kwargs in ({'timeout_ms':0},{'timeout_ms':True},
                       {'budget_microusd':-1},{'snapshot':'2026-99-99'}):
            with self.assertRaises(ValueError):Settings(**kwargs)

    def test_query_rejects_invalid_values(self):
        for topic,lang in [(None,'pt-BR'),('a'*41,'en-US'),('refund','fr'),
                           ('../secret','en-US')]:
            with self.assertRaises(ValueError):Query(topic,lang)

    def test_json_ambiguity_rejected(self):
        for s in ('{"x":1,"x":2}','{"x":NaN}'):
            with self.assertRaises(ValueError):strict_json(s)

    def test_core_has_no_concrete_adapter_import(self):
        for filename in ('service.py','policy.py','ports.py','contracts.py'):
            tree=ast.parse((ROOT/filename).read_text(encoding='utf-8'))
            imports={n.module.split('.')[0] for n in ast.walk(tree)
                     if isinstance(n,ast.ImportFrom) and n.module}
            imports|={a.name.split('.')[0] for n in ast.walk(tree)
                      if isinstance(n,ast.Import) for a in n.names}
            self.assertFalse(imports & {'http_api','adapters','bootstrap',
                                      'http','urllib','os','pathlib'})

    def test_fixture_contains_no_evaluation_oracle(self):
        self.assertNotIn('expected_fact',(ROOT/'documents.json').read_text(encoding='utf-8'))


if __name__=='__main__':unittest.main()
