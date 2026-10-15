import copy
import unittest
from chapter1 import (read_data, lookup, score, evaluate, percentile,
                     valid_shape, abstain, answer, current)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.data = read_data()
        self.docs = self.data["documents"]
        self.case = self.data["cases"][0]

    def test_guarded_passes_finite_suite(self):
        self.assertTrue(evaluate("guarded", self.data)["summary"]["suite_pass"])

    def test_naive_is_rejected(self):
        s = evaluate("naive", self.data)["summary"]
        self.assertFalse(s["suite_pass"])
        self.assertGreater(s["unauthorized_disclosures"], 0)

    def test_candidate_replay_exposes_independent_failures(self):
        s = evaluate("candidate", self.data)["summary"]
        self.assertEqual((s["correct_answers"], s["accepted_tasks"]), (5, 3))
        self.assertEqual(s["scenario_total_microusd"], 6800)
        self.assertEqual(s["invalid_outputs"], 1)
        self.assertEqual(s["unauthorized_disclosures"], 1)

    def test_abstain_all_cannot_game_quality(self):
        s = evaluate("abstain", self.data)["summary"]
        self.assertEqual((s["accepted_tasks"], s["controlled_abstentions"]), (0, 4))
        self.assertIsNone(s["scenario_microusd_per_accepted_task"])
        self.assertFalse(s["suite_pass"])

    def test_tenant_change_requires_new_evidence(self):
        c = dict(self.case, tenant="unknown")
        self.assertEqual(lookup(c, self.docs)["status"], "abstain")

    def test_access_revocation_changes_result(self):
        docs = copy.deepcopy(self.docs)
        for doc in docs:
            doc["roles"] = []
        self.assertEqual(lookup(self.case, docs)["status"], "abstain")

    def test_expired_evidence_never_accepted(self):
        stale = self.docs[0]
        self.assertFalse(current(stale))
        self.assertFalse(score(self.case, answer(stale), self.docs, 20, 0)["grounded"])

    def test_unknown_citation_rejected(self):
        r = lookup(self.case, self.docs)
        r["citation"] = "invented"
        self.assertFalse(score(self.case, r, self.docs, 20, 0)["correct_answer"])

    def test_unknown_fields_rejected(self):
        self.assertFalse(valid_shape(dict(abstain(), confidence=1.0)))
        self.assertFalse(valid_shape(dict(abstain(), reason=[])))
        self.assertFalse(valid_shape(dict(abstain(), reason="unknown")))

    def test_conflict_must_not_depend_on_document_order(self):
        case = self.data["cases"][-1]
        self.assertEqual(lookup(case, self.docs), lookup(case, list(reversed(self.docs))))
        self.assertEqual(lookup(case, self.docs)["reason"], "conflicting_evidence")

    def test_limits_are_inclusive(self):
        response = lookup(self.case, self.docs)
        self.assertTrue(score(self.case, response, self.docs, 2500, 1000)["accepted_task"])
        self.assertFalse(score(self.case, response, self.docs, 2501, 1000)["accepted_task"])
        self.assertFalse(score(self.case, response, self.docs, 2500, 1001)["accepted_task"])

    def test_relaxing_budgets_does_not_fix_access(self):
        s = evaluate("candidate", self.data, 5000, 2000)["summary"]
        self.assertEqual(s["accepted_tasks"], 5)
        self.assertFalse(s["suite_pass"])

    def test_oracle_not_used_by_lookup(self):
        changed = dict(self.case, expected_fact="wrong_oracle")
        self.assertEqual(lookup(self.case, self.docs), lookup(changed, self.docs))

    def test_empty_dataset_is_not_a_pass(self):
        s = evaluate("guarded", dict(self.data, cases=[]))["summary"]
        self.assertFalse(s["suite_pass"])
        self.assertIsNone(s["accepted_fraction"])
        self.assertIsNone(s["scenario_p95_ms"])

    def test_nearest_rank_small_sample(self):
        self.assertEqual(percentile(list(range(1, 13)), 0.95), 12)
        self.assertIsNone(percentile([], 0.95))

    def test_invalid_payload_does_not_hide_access_violation(self):
        c = self.data["cases"][8]
        r = {"citation": "acme-payroll-v1"}
        row = score(c, r, self.docs, 20, 0)
        self.assertFalse(row["valid_shape"])
        self.assertTrue(row["unauthorized_disclosure"])


if __name__ == "__main__":
    unittest.main()
