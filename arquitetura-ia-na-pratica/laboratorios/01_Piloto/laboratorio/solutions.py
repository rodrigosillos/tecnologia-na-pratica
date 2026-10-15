"""Executable solutions and relaxed-limit experiment. Entirely offline."""
from copy import deepcopy
import json
from pathlib import Path
from copilot import read_data, lookup, evaluate


def exercise_one():
    result = {
        "behavior_correct_fraction": (9 + 7) / 20,
        "accepted_fraction": (9 - 2) / 12,
        "controlled_abstention_fraction": 7 / 8,
        "microusd_per_accepted_task": 40000 / 7,
        "suite_pass": False,
        "overlapping_resource_failures_accepted": 8,
    }
    assert round(result["accepted_fraction"] * 100, 2) == 58.33
    return result


def exercise_two():
    data = read_data()
    case = data["cases"][-1]
    docs = deepcopy(data["documents"])
    before = lookup(case, docs)
    first = next(d for d in docs if d["id"] == "acme-conflict-a")
    second = next(d for d in docs if d["id"] == "acme-conflict-b")
    second["fact_id"] = first["fact_id"]
    second["text"] = deepcopy(first["text"])
    after = lookup(case, docs)
    reversed_result = lookup(case, list(reversed(docs)))
    assert before["status"] == "abstain"
    assert after["fact_id"] == reversed_result["fact_id"] == "call_111"
    assert data["documents"][-1]["fact_id"] == "call_222"
    return {"before": before, "after": after,
            "after_reversing_documents": reversed_result}


def main():
    root = Path(__file__).resolve().parent / "results"
    root.mkdir(exist_ok=True)
    relaxed = evaluate("candidate", read_data(), 5000, 2000)
    results = {"exercise_1": exercise_one(), "exercise_2": exercise_two()}
    for name, value in [("solutions", results), ("relaxed", relaxed)]:
        (root / (name + ".json")).write_text(
            json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print("Relaxed accepted tasks:", relaxed["summary"]["accepted_tasks"])
    print("Relaxed suite pass:", relaxed["summary"]["suite_pass"])


if __name__ == "__main__":
    main()
