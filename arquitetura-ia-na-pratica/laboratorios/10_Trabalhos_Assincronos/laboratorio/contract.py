"""Strict chapter-8 wire profile. Standard library; not a JSON Schema engine."""
import json
import re

VERSION = '1.0'
MAX_FRAME = 16384
MAX_STREAM = 131072
KINDS = {'accepted', 'progress', 'result', 'error', 'cancelled'}

class ContractError(ValueError):
    pass

def require(condition, code):
    if not condition:
        raise ContractError(code)

def keys(value, expected):
    require(type(value) is dict and set(value) == set(expected), 'fields')

def string(value, low=1, high=400):
    require(type(value) is str and low <= len(value) <= high, 'string')

def identifier(value):
    string(value, 1, 40)
    require(re.fullmatch(r'[A-Za-z0-9_-]+', value) is not None, 'identifier')

def strict_json(raw):
    def pairs(values):
        result = {}
        for key, value in values:
            require(key not in result, 'duplicate_key')
            result[key] = value
        return result
    def constant(value):
        raise ContractError('nonfinite')
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, RecursionError, UnicodeError) as exc:
        raise ContractError('invalid_json') from exc

def validate_request(value):
    keys(value, ('schema_version', 'request_id', 'language', 'queries'))
    require(value['schema_version'] == VERSION, 'version')
    identifier(value['request_id'])
    require(value['language'] in ('pt-BR', 'en-US'), 'language')
    queries = value['queries']
    require(type(queries) is list and 1 <= len(queries) <= 3, 'queries')
    ids = []
    for item in queries:
        keys(item, ('id', 'text'))
        identifier(item['id'])
        string(item['text'])
        require(bool(item['text'].strip()), 'empty_query')
        ids.append(item['id'])
    require(len(ids) == len(set(ids)), 'duplicate_query')
    return value

def outcome(items):
    count = sum(item['status'] == 'answer' for item in items)
    if count == len(items):
        return 'complete'
    return 'partial' if count else 'no_answer'

def validate_result(data):
    keys(data, ('outcome', 'items'))
    items = data['items']
    require(type(items) is list and 1 <= len(items) <= 3, 'items')
    ids = []
    for item in items:
        keys(item, ('id', 'status', 'text', 'citations'))
        identifier(item['id']); ids.append(item['id'])
        require(item['status'] in ('answer', 'clarify', 'abstain'), 'item_status')
        cites = item['citations']
        require(type(cites) is list, 'citations')
        if item['status'] == 'answer':
            string(item['text'], 1, 1000)
            require(len(cites) == 1, 'citation_count')
            cite = cites[0]
            keys(cite, ('document', 'version', 'source', 'quote'))
            string(cite['document'], 1, 100)
            require(type(cite['version']) is int and cite['version'] > 0, 'version_number')
            string(cite['source'], 1, 400); string(cite['quote'], 1, 1000)
            require(cite['quote'] == item['text'], 'quote_mismatch')
        else:
            require(item['text'] is None and cites == [], 'nonanswer_payload')
    require(len(ids) == len(set(ids)), 'duplicate_item')
    require(data['outcome'] == outcome(items), 'outcome')

def validate_event(event):
    keys(event, ('schema_version', 'request_id', 'seq', 'kind', 'data'))
    require(event['schema_version'] == VERSION, 'version')
    identifier(event['request_id'])
    require(type(event['seq']) is int and 1 <= event['seq'] <= 32, 'sequence')
    kind = event['kind']; data = event['data']
    require(type(kind) is str and kind in KINDS, 'kind')
    if kind == 'accepted':
        keys(data, ())
    elif kind == 'progress':
        keys(data, ('stage',))
        require(data['stage'] in ('retrieval', 'validation'), 'stage')
    elif kind == 'result':
        validate_result(data)
    elif kind == 'cancelled':
        keys(data, ('code',))
        require(data['code'] == 'cancelled', 'cancel_code')
    else:
        keys(data, ('code', 'retryable'))
        require(data['code'] == 'processing_failed', 'error_code')
        require(data['retryable'] is False, 'retry_policy')
    return event

def encode_event(event):
    validate_event(event)
    payload = json.dumps(event, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    frame = (f"event: {event['kind']}\nid: {event['request_id']}/{event['seq']}\n"
             f"data: {payload}\n\n").encode('utf-8')
    require(len(frame) <= MAX_FRAME, 'frame_limit')
    return frame
