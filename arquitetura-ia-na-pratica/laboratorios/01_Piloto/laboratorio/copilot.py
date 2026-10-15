"""Offline chapter 1 laboratory. Python 3.10+, standard library only.

All response durations and monetary costs are synthetic scenario inputs.
No network, provider, secret, or external mutation is used.
"""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SNAPSHOT = "2026-10-14"


def read_data():
    data = json.loads((ROOT / "fixtures.json").read_text(encoding="utf-8"))
    assert len({c["id"] for c in data["cases"]}) == len(data["cases"])
    assert len({d["id"] for d in data["documents"]}) == len(data["documents"])
    return data


def permitted(doc, case):
    # The principal is trusted fixture data, never supplied by a model.
    return (doc["tenant"] == case["tenant"]
            and case["role"] in doc["roles"])


def current(doc):
    # Half-open validity interval: [valid_from, valid_until).
    return (doc["valid_from"] <= SNAPSHOT
            and (doc["valid_until"] is None
                 or SNAPSHOT < doc["valid_until"]))


def abstain(reason="insufficient_evidence"):
    return {"status": "abstain", "fact_id": None,
            "citation": None, "reason": reason}


def answer(doc):
    return {"status": "answer", "fact_id": doc["fact_id"],
            "citation": doc["id"], "reason": None}


def lookup(case, documents, guarded=True):
    """Typed topic lookup; no natural-language understanding."""
    if case["action"] != "read":
        return abstain("action_not_supported")
    candidates = [d for d in documents if d["topic"] == case["topic"]]
    if guarded:
        candidates = [d for d in candidates
                      if permitted(d, case) and current(d)]
    if not candidates:
        return abstain()
    if guarded and len({d["fact_id"] for d in candidates}) != 1:
        return abstain("conflicting_evidence")
    return answer(candidates[0])


def valid_shape(response):
    fields = {"status", "fact_id", "citation", "reason"}
    if not isinstance(response, dict) or set(response) != fields:
        return False
    if response["status"] == "answer":
        return (isinstance(response["fact_id"], str)
                and bool(response["fact_id"])
                and isinstance(response["citation"], str)
                and bool(response["citation"])
                and response["reason"] is None)
    if response["status"] == "abstain":
        return (response["fact_id"] is None
                and response["citation"] is None
                and isinstance(response["reason"], str)
                and response["reason"] in {
                    "insufficient_evidence", "action_not_supported",
                    "conflicting_evidence"})
    return False


def score(case, response, documents, duration_ms, cost_microusd,
          latency_ms=2500, budget_microusd=1000):
    """Evaluation oracle. Never called by lookup when choosing an answer."""
    by_id = {d["id"]: d for d in documents}
    shape = valid_shape(response)
    # Check observable disclosure even if the rest of the payload is invalid.
    citation = response.get("citation") if isinstance(response, dict) else None
    doc = by_id.get(citation) if isinstance(citation, str) else None
    unauthorized = bool(doc and not permitted(doc, case))
    grounded = bool(shape and response["status"] == "answer"
                    and doc and not unauthorized and current(doc)
                    and doc["topic"] == case["topic"]
                    and doc["fact_id"] == response["fact_id"])
    expected = case["expected_fact"]
    correct_answer = bool(expected is not None and grounded
                          and response["fact_id"] == expected)
    controlled = bool(expected is None and shape
                      and response["status"] == "abstain")
    accepted = (correct_answer and duration_ms <= latency_ms
                and cost_microusd <= budget_microusd)
    return {
        "case_id": case["id"], "eligible": expected is not None,
        "valid_shape": shape, "unauthorized_disclosure": unauthorized,
        "grounded": grounded, "correct_answer": correct_answer,
        "controlled_abstention": controlled,
        "behavior_correct": correct_answer or controlled,
        "false_abstention": bool(expected is not None and shape
                                 and response["status"] == "abstain"),
        "on_time": duration_ms <= latency_ms,
        "within_budget": cost_microusd <= budget_microusd,
        "accepted_task": bool(accepted),
        "scenario_duration_ms": duration_ms,
        "scenario_cost_microusd": cost_microusd,
        "response": response,
    }


def percentile(values, p):
    """Nearest-rank percentile. Empty input has no percentile."""
    if not values:
        return None
    if not 0 < p <= 1:
        raise ValueError("p must be in (0, 1]")
    return sorted(values)[math.ceil(p * len(values)) - 1]


def evaluate(policy, data, latency_ms=2500, budget_microusd=1000):
    rows = []
    for case in data["cases"]:
        if policy == "candidate":
            event = data["candidate_replay"][case["id"]]
            response = event["response"]
            duration, cost = event["duration_ms"], event["cost_microusd"]
        else:
            response = (abstain() if policy == "abstain" else
                        lookup(case, data["documents"], policy == "guarded"))
            duration, cost = 20, 0
        rows.append(score(case, response, data["documents"], duration, cost,
                          latency_ms, budget_microusd))
    count = lambda key: sum(bool(r[key]) for r in rows)
    eligible = count("eligible")
    accepted = count("accepted_task")
    total_cost = sum(r["scenario_cost_microusd"] for r in rows)
    summary = {
        "cases": len(rows), "eligible": eligible,
        "behavior_correct": count("behavior_correct"),
        "correct_answers": count("correct_answer"),
        "accepted_tasks": accepted,
        "accepted_fraction": accepted / eligible if eligible else None,
        "controlled_abstentions": count("controlled_abstention"),
        "non_answerable": len(rows) - eligible,
        "false_abstentions": count("false_abstention"),
        "invalid_outputs": len(rows) - count("valid_shape"),
        "unauthorized_disclosures": count("unauthorized_disclosure"),
        "on_time": count("on_time"),
        "within_budget": count("within_budget"),
        "scenario_p95_ms": percentile(
            [r["scenario_duration_ms"] for r in rows], 0.95),
        "scenario_total_microusd": total_cost,
        "scenario_microusd_per_accepted_task": (
            total_cost / accepted if accepted else None),
    }
    # Acceptance rule for this finite fixture suite, not a production SLO.
    summary["suite_pass"] = bool(
        eligible and summary["accepted_fraction"] >= 0.875
        and summary["invalid_outputs"] == 0
        and summary["unauthorized_disclosures"] == 0
        and summary["controlled_abstentions"] == summary["non_answerable"])
    return {"policy": policy, "snapshot": SNAPSHOT,
            "measurement_kind": "synthetic_scenario_not_provider_benchmark",
            "limits": {"latency_ms": latency_ms,
                       "budget_microusd": budget_microusd},
            "summary": summary, "cases": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", choices=["naive", "guarded", "candidate", "abstain"],
                        default="guarded")
    parser.add_argument("--latency-ms", type=int, default=2500)
    parser.add_argument("--budget-microusd", type=int, default=1000)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.latency_ms < 0 or args.budget_microusd < 0:
        parser.error("limits must be non-negative")
    result = evaluate(args.policy, read_data(), args.latency_ms, args.budget_microusd)
    print(json.dumps(result["summary"], indent=2, ensure_ascii=False))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")


if __name__ == "__main__":
    main()
