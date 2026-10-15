"""Chapter 2. Offline, synthetic replay; no model or network calls.

Python 3.10+, standard library. Costs and token counts are fixture data.
The toy tokenizer is NOT used to estimate a provider's context or bill.
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path

from chapter1 import abstain, current, permitted, read_data, valid_shape

ROOT = Path(__file__).resolve().parent
MERGES = {(b"r", b"e"): 0, (b"re", b"f"): 1,
          (b"ref", b"u"): 2, (b"refu", b"n"): 3,
          (b"refun", b"d"): 4}


def toy_tokens(text):
    parts = [bytes([b]) for b in text.encode("utf-8")]
    while len(parts) > 1:
        choices = [(MERGES[pair], i)
                   for i, pair in enumerate(zip(parts, parts[1:]))
                   if pair in MERGES]
        if not choices:
            break
        _, i = min(choices)
        parts[i:i + 2] = [parts[i] + parts[i + 1]]
    return parts


def nonnegative_int(value):
    if type(value) is not int or value < 0:
        raise ValueError("expected a non-negative integer")
    return value


def plan_context(fixed, chunks, limit=4096, output=512, margin=128):
    for value in (fixed, limit, output, margin):
        nonnegative_int(value)
    ids = [c["id"] for c in chunks]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate chunk id")
    for chunk in chunks:
        nonnegative_int(chunk["tokens"])
    available = limit - fixed - output - margin
    if available < 0:
        raise ValueError("fixed input and reserves exceed context")
    selected, omitted = [], []
    for chunk in chunks:
        if chunk["tokens"] <= available:
            selected.append(chunk["id"])
            available -= chunk["tokens"]
        else:
            omitted.append(chunk["id"])
    return {"selected": selected, "omitted": omitted,
            "input_tokens": limit - output - margin - available,
            "reserved_output": output, "margin": margin,
            "slack": available}


def cosine(a, b):
    if not a or len(a) != len(b):
        raise ValueError("nonempty vectors of equal dimension required")
    if not all(math.isfinite(x) for x in (*a, *b)):
        raise ValueError("finite components required")
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if not norm_a or not norm_b:
        raise ValueError("zero vector has no cosine similarity")
    return sum(x * y for x, y in zip(a, b)) / (norm_a * norm_b)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("nonstandard JSON constant: " + value)


def decode_strict(text):
    return json.loads(text, object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def prepare_context(case, documents):
    if case["action"] != "read":
        return [], abstain("action_not_supported")
    docs = [d for d in documents if d["topic"] == case["topic"]
            and permitted(d, case) and current(d)]
    if not docs:
        return [], abstain()
    if len({d["fact_id"] for d in docs}) != 1:
        return [], abstain("conflicting_evidence")
    return docs, None


def supported(response, case, sent_docs):
    if response["status"] != "answer":
        return False
    return any(d["id"] == response["citation"]
               and d["fact_id"] == response["fact_id"]
               and d["topic"] == case["topic"]
               and permitted(d, case) and current(d)
               for d in sent_docs)


def usage_cost(usage):
    if usage is None:
        return None
    incoming = nonnegative_int(usage["input_tokens"])
    outgoing = nonnegative_int(usage["output_tokens"])
    # Fictional integer rates, in micro-USD per token.
    return 2 * incoming + 6 * outgoing


def finalize(event, case, sent_docs, deadline=2500, budget=1000):
    """Return a terminal decision, never a partially streamed answer.

    Event is a trusted replay envelope, not raw provider input.
    No expected_fact/oracle is read when deciding what may be returned.
    """
    state = event["state"]
    if state in {"incomplete", "refused", "unavailable"}:
        return state, None
    if state != "completed":
        return "invalid_envelope", None
    text = "".join(event["chunks"])
    if len(text.encode("utf-8")) > 8192:
        return "oversized", None
    try:
        payload = decode_strict(text)
    except (ValueError, RecursionError):
        return "invalid_json", None
    if not valid_shape(payload):
        return "invalid_schema", None
    if not supported(payload, case, sent_docs):
        return "unsupported", None
    if event["end_ms"] > deadline:
        return "late", None
    cost = usage_cost(event["usage"])
    if cost is None:
        return "unknown_cost", None
    if cost > budget:
        return "over_budget", None
    return "accepted", payload


def run_case(scenario, case, documents):
    docs, abstention = prepare_context(case, documents)
    if abstention is not None:
        return {"id": scenario["id"], "case_id": case["id"],
                "decision": "business_abstention", "attempted": False,
                "sent_document_ids": [], "response": abstention,
                "cost_microusd": 0, "first_ms": None, "end_ms": 0}
    event = scenario["event"]
    decision, response = finalize(event, case, docs)
    return {"id": scenario["id"], "case_id": case["id"],
            "decision": decision, "attempted": True,
            "sent_document_ids": [d["id"] for d in docs],
            "response": response, "cost_microusd": usage_cost(event["usage"]),
            "first_ms": event["first_ms"], "end_ms": event["end_ms"]}


def summarize(rows):
    counts = dict(sorted(Counter(r["decision"] for r in rows).items()))
    unknown = sum(r["cost_microusd"] is None for r in rows)
    known = sum(r["cost_microusd"] for r in rows
                if r["cost_microusd"] is not None)
    total = None if unknown else known
    accepted = counts.get("accepted", 0)
    return {"scenarios": len(rows),
            "attempted": sum(r["attempted"] for r in rows),
            "decisions": counts, "known_cost_microusd": known,
            "unmetered_attempts": unknown, "total_cost_microusd": total,
            "microusd_per_accepted": (total / accepted
                if total is not None and accepted else None)}


def evaluate():
    data = read_data()
    scenarios = json.loads((ROOT / "scenarios.json").read_text(
        encoding="utf-8"))["scenarios"]
    cases = {c["id"]: c for c in data["cases"]}
    rows = [run_case(s, cases[s["case_id"]], data["documents"])
            for s in scenarios]
    # An external oracle checks accepted outputs, not the decision path.
    for row in rows:
        case = cases[row["case_id"]]
        row["oracle_correct_if_accepted"] = (
            row["response"]["fact_id"] == case["expected_fact"]
            if row["decision"] == "accepted" else None)
    return {"measurement_kind": "synthetic_replay_not_model_benchmark",
            "snapshot": "2026-10-14", "summary": summarize(rows),
            "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = evaluate()
    print(json.dumps(report["summary"], indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n",
                            encoding="utf-8")


if __name__ == "__main__":
    main()
