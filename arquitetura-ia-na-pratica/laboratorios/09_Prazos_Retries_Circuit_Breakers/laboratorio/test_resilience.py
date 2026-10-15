import unittest
from dataclasses import FrozenInstanceError
from random import Random
from threading import Event
from resilience import (Clock, Policy, Step, ScriptedProvider, RetryBudget,
                        CircuitBreaker, CircuitOpen, Controller,
                        attempt_allowance, retry_delay, health_of)
from experiments import experiment, run_scenarios, cascade
from exercises import exercise17, exercise18
from integration import integrated_case


class ResilienceTests(unittest.TestCase):
    def run_steps(self, steps, **kwargs):
        c = Clock(); p = ScriptedProvider(steps)
        ctl = Controller(c, **kwargs)
        return ctl.run(p), p, ctl

    def test_integer_configuration_rejects_bool_negative_float(self):
        for value in (-1, True, 1.5):
            with self.subTest(value=value):
                with self.assertRaises(ValueError): Clock(value)
                with self.assertRaises(ValueError): RetryBudget(value)
                with self.assertRaises(ValueError): Step(value)

    def test_policy_consistency_and_immutability(self):
        for kw in ({'attempt_ms':20}, {'base_ms':500},
                   {'max_attempts':0}, {'reserve_ms':-1}):
            with self.assertRaises(ValueError): Policy(**kw)
        with self.assertRaises(FrozenInstanceError): Policy().budget_ms=1

    def test_clock_never_goes_back(self):
        c=Clock(10)
        with self.assertRaises(ValueError): c.advance(-1)
        self.assertEqual(c.now,10)
        c.advance(0); c.advance(7); self.assertEqual(c.now,17)

    def test_allowance_preserves_reserve(self):
        self.assertEqual(attempt_allowance(450,290,Policy()),60)

    def test_minimum_admission_boundary(self):
        self.assertEqual(attempt_allowance(150,0,Policy()),50)
        self.assertEqual(attempt_allowance(149,0,Policy()),0)

    def test_expired_deadline_has_no_attempt(self):
        c=Clock(); ctl=Controller(c); c.advance(1200)
        p=ScriptedProvider([Step(1)])
        self.assertEqual(ctl.run(p)['reason'],'deadline')
        self.assertEqual(p.calls,0)

    def test_result_at_timeout_boundary_is_late(self):
        r,p,_=self.run_steps([Step(300)],policy=Policy(max_attempts=1))
        self.assertEqual(r['reason'],'attempt_limit')
        self.assertEqual(r['trace'][0]['status'],'timeout')
        self.assertEqual(r['elapsed_ms'],300)

    def test_result_before_timeout_is_accepted(self):
        r,_,_=self.run_steps([Step(299)])
        self.assertEqual(r['reason'],'success')

    def test_long_attempt_is_clipped(self):
        r,_,_=self.run_steps([Step(5000)],policy=Policy(max_attempts=1))
        self.assertEqual(r['elapsed_ms'],300)

    def test_full_jitter_within_window_and_cap(self):
        p=Policy()
        for retry,maximum in [(1,100),(2,200),(3,400),(10000,400)]:
            values={retry_delay(retry,p,Random(seed)) for seed in range(40)}
            self.assertGreater(len(values),10)
            self.assertTrue(all(0<=v<=maximum for v in values))

    def test_seeded_backoff_reproduces(self):
        self.assertEqual(experiment('recovered_503')['waits_ms'],[41])
        self.assertEqual(experiment('recovered_503')['elapsed_ms'],161)

    def test_retry_after_is_lower_bound_not_cap(self):
        self.assertEqual(retry_delay(1,Policy(),Random(7),500),500)
        with self.assertRaises(ValueError): retry_delay(1,Policy(),Random(),-1)

    def test_retry_after_fits(self):
        r=exercise17()['fits']
        self.assertEqual((r['attempts'],r['elapsed_ms']),(2,520))

    def test_retry_after_too_late_never_waits_or_retries(self):
        r=exercise17()['too_late']
        self.assertEqual((r['attempts'],r['elapsed_ms'],r['waits_ms']),(1,40,[]))

    def test_400_never_retried(self):
        r=experiment('permanent_400')
        self.assertEqual((r['reason'],r['attempts']),('non_retryable',1))

    def test_invalid_output_is_not_transport_failure(self):
        self.assertEqual(experiment('invalid_output')['reason'],'non_retryable')
        self.assertEqual(health_of('invalid'),'neutral')

    def test_unsafe_operation_has_no_retry(self):
        r=experiment('unsafe_operation')
        self.assertEqual((r['reason'],r['attempts']),('unsafe_to_retry',1))

    def test_max_attempts_includes_first(self):
        r=experiment('attempt_limit')
        self.assertEqual((r['reason'],r['attempts']),('attempt_limit',3))

    def test_initial_attempt_does_not_consume_retry_quota(self):
        r,_,_=self.run_steps([Step(1)],retries=RetryBudget(0))
        self.assertEqual((r['reason'],r['attempts']),('success',1))

    def test_empty_quota_stops_before_backoff(self):
        r=experiment('retry_quota')
        self.assertEqual((r['reason'],r['waits_ms']),('retry_budget',[]))

    def test_quota_shared_across_operations(self):
        c=Clock(); quota=RetryBudget(1)
        a=Controller(c,retries=quota).run(ScriptedProvider([Step(1,'503'),Step(1)]))
        b=Controller(c,retries=quota).run(ScriptedProvider([Step(1,'503'),Step(1)]))
        self.assertEqual((a['attempts'],b['attempts']),(2,1))
        self.assertEqual(b['reason'],'retry_budget')

    def test_deadline_consumed_by_attempts_and_waits(self):
        r=experiment('deadline')
        self.assertEqual((r['reason'],r['attempts'],r['elapsed_ms']),('deadline',2,550))
        self.assertEqual(r['trace'][1]['allowance_ms'],209)

    def test_cancel_before_start_no_call(self):
        token=Event();token.set(); p=ScriptedProvider([Step(1)])
        r=Controller(Clock()).run(p,cancel=token)
        self.assertEqual((r['reason'],p.calls),('cancelled',0))

    def test_cancel_during_wait_no_second_call(self):
        r=experiment('cancel_wait')
        self.assertEqual((r['reason'],r['attempts'],r['elapsed_ms']),('cancelled',1,81))

    def test_cancel_during_attempt_discards_success(self):
        token=Event(); c=Clock(after_advance=lambda _:token.set())
        ctl=Controller(c)
        r=ctl.run(ScriptedProvider([Step(40)]),cancel=token)
        self.assertEqual(r['reason'],'cancelled')
        self.assertEqual(ctl.breaker.inflight,{})

    def test_breaker_opens_on_threshold(self):
        b=CircuitBreaker(threshold=2)
        for _ in range(2): b.finish(b.acquire(0),'unhealthy',0)
        self.assertEqual(b.state,'open')
        with self.assertRaises(CircuitOpen): b.acquire(499)

    def test_healthy_resets_consecutive_failures(self):
        b=CircuitBreaker(threshold=2)
        for health in ('unhealthy','healthy','unhealthy'):
            b.finish(b.acquire(0),health,0)
        self.assertEqual((b.state,b.failures),('closed',1))

    def test_neutral_does_not_increment_or_reset(self):
        b=CircuitBreaker();b.finish(b.acquire(0),'unhealthy',0)
        b.finish(b.acquire(0),'neutral',0)
        self.assertEqual(b.failures,1)
        self.assertEqual(health_of('429'),'neutral')

    def test_probe_admitted_at_cooldown_boundary(self):
        b=CircuitBreaker(threshold=1);b.finish(b.acquire(0),'unhealthy',0)
        p=b.acquire(500)
        self.assertTrue(p.probe);self.assertEqual(b.state,'half_open')

    def test_only_one_half_open_probe(self):
        self.assertEqual(exercise18()['second_probe'],'blocked')

    def test_failed_probe_starts_new_cooldown(self):
        b=CircuitBreaker(threshold=1);b.finish(b.acquire(0),'unhealthy',0)
        b.finish(b.acquire(500),'unhealthy',540)
        self.assertEqual(b.open_until,1040)

    def test_neutral_probe_reopens_conservatively(self):
        b=CircuitBreaker(threshold=1);b.finish(b.acquire(0),'unhealthy',0)
        b.finish(b.acquire(500),'neutral',520)
        self.assertEqual((b.state,b.open_until),('open',1020))

    def test_stale_success_does_not_close_new_generation(self):
        self.assertEqual(exercise18()['after_stale'],'open')

    def test_successful_probe_closes(self):
        self.assertEqual(exercise18()['final'],'closed')

    def test_permit_cannot_finish_twice(self):
        b=CircuitBreaker();p=b.acquire(0);b.finish(p,'healthy',0)
        with self.assertRaises(ValueError): b.finish(p,'unhealthy',0)

    def test_open_circuit_spends_no_provider_call_or_quota(self):
        b=CircuitBreaker(threshold=1);b.finish(b.acquire(0),'unhealthy',0)
        p=ScriptedProvider([Step(1)]);q=RetryBudget(2)
        r=Controller(Clock(),breaker=b,retries=q).run(p)
        self.assertEqual((r['reason'],p.calls,q.tokens),('circuit_open',0,2))

    def test_programming_error_not_retried_and_probe_released(self):
        b=CircuitBreaker(threshold=1);b.finish(b.acquire(0),'unhealthy',0)
        ctl=Controller(Clock(500),breaker=b)
        with self.assertRaises(RuntimeError): ctl.run(ScriptedProvider([]))
        self.assertEqual((b.state,b.inflight),('open',{}))

    def test_bilingual_contract_success_and_failure(self):
        for lang in ('pt-BR','en-US'):
            good=integrated_case(lang)
            bad=integrated_case(lang,failure=True)
            self.assertEqual((good['state'],good['outcome']),('completed','complete'))
            self.assertEqual((bad['state'],bad['outcome']),('failed',None))

    def test_bilingual_contract_cancelled(self):
        for lang in ('pt-BR','en-US'):
            self.assertEqual(integrated_case(lang,cancel_at=50)['state'],'cancelled')

    def test_deadline_not_reset_for_second_question(self):
        for lang in ('pt-BR','en-US'):
            r=integrated_case(lang,shared_deadline=True)
            self.assertEqual((r['state'],r['elapsed_ms']),('failed',350))
            self.assertEqual(r['reports'][1]['trace'][0]['allowance_ms'],60)

    def test_retry_amplification_is_executed_tree(self):
        self.assertEqual((cascade(3,3),cascade(1,3)),(27,3))

    def test_all_scenarios_deterministic(self):
        a=run_scenarios();b=run_scenarios()
        self.assertEqual(a,b);self.assertEqual(a['cases'],18)


if __name__ == '__main__': unittest.main()
