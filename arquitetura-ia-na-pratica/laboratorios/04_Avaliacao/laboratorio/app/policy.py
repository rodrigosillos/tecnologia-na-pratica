"""Evidence and output policies: deterministic, independent of transport."""
import json
from contracts import Document, Principal


def allowed(doc: Document, principal: Principal, topic, snapshot):
    return (doc.tenant == principal.tenant
            and principal.role in doc.roles and doc.topic == topic
            and doc.valid_from <= snapshot
            and (doc.valid_until is None or snapshot < doc.valid_until))


def choose_evidence(candidates, principal, topic, snapshot):
    docs = tuple(d for d in candidates
                 if allowed(d, principal, topic, snapshot))
    if not docs:
        return (), "insufficient_evidence"
    if len({d.fact_id for d in docs}) != 1:
        return (), "conflicting_evidence"
    return docs, None


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("nonstandard constant")


def strict_json(text):
    return json.loads(text, object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def validated_document(completion, docs):
    if completion.state != "completed":
        return None
    if not isinstance(completion.text, str):
        return None
    if len(completion.text.encode("utf-8")) > 8192:
        return None
    try:
        obj = strict_json(completion.text)
    except (ValueError, RecursionError):
        return None
    fields = {"status", "fact_id", "citation", "reason"}
    if not isinstance(obj, dict) or set(obj) != fields:
        return None
    if obj["status"] != "answer" or obj["reason"] is not None:
        return None
    if not all(isinstance(obj[k], str) for k in ("fact_id", "citation")):
        return None
    return next((d for d in docs if d.id == obj["citation"]
                 and d.fact_id == obj["fact_id"]), None)
