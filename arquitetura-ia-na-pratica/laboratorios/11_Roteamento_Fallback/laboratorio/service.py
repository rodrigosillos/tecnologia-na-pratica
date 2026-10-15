"""In-process API boundary with a finite SSE-shaped response body; no HTTP server."""
import json
from threading import Event
from contract import (ContractError, VERSION, encode_event, outcome,
                      require, validate_event, validate_request, strict_json)
from retrieval import answer, verify_citation

def public_item(query_id, reply):
    cites = []
    if reply['status'] == 'answer':
        for cite in reply['citations']:
            cites.append(dict(document=cite['document'], version=cite['version'],
                              source=cite['source'], quote=cite['text']))
    return dict(id=query_id, status=reply['status'], text=reply['text'], citations=cites)

def events(store, actor, request, cancel=None, before_release=None, engine=answer):
    validate_request(request)
    cancel = cancel if cancel is not None else Event()
    seq = 0
    def event(kind, data):
        nonlocal seq
        value = validate_event(dict(schema_version=VERSION, request_id=request['request_id'],
                                    seq=seq+1, kind=kind, data=data))
        seq += 1
        return value
    yield event('accepted', {})
    if cancel.is_set():
        yield event('cancelled', {'code':'cancelled'}); return
    yield event('progress', {'stage':'retrieval'})
    try:
        replies = []
        for query in request['queries']:
            if cancel.is_set():
                yield event('cancelled', {'code':'cancelled'}); return
            reply = engine(store, actor, query['text'], request['language'])
            replies.append((query['id'], reply))
        yield event('progress', {'stage':'validation'})
        if before_release:
            before_release()
        if cancel.is_set():
            yield event('cancelled', {'code':'cancelled'}); return
        items = []
        for query_id, reply in replies:
            if not verify_citation(store, actor, reply, request['language']):
                reply = dict(status='abstain', text=None, citations=[], reason=None)
            items.append(public_item(query_id, reply))
        final = event('result', dict(outcome=outcome(items), items=items))
    except Exception:
        # This boundary redacts details. A real service also needs protected internal diagnostics.
        final = event('cancelled', {'code':'cancelled'}) if cancel.is_set() else event(
            'error', {'code':'processing_failed', 'retryable':False})
    yield final

def problem(status, title):
    # No raw query, exception text, authorization reason, or internal identifier.
    data = dict(type='about:blank', title=title, status=status)
    return status, {'Content-Type':'application/problem+json', 'Cache-Control':'no-store'}, (
        json.dumps(data, separators=(',', ':')).encode('utf-8'),)

def open_stream(store, actor, body, content_type='application/json', **options):
    if content_type != 'application/json':
        return problem(415, 'Unsupported Media Type')
    if type(body) is not bytes or len(body) > 4096:
        return problem(413, 'Content Too Large')
    try:
        request = validate_request(strict_json(body.decode('utf-8')))
    except (ContractError, UnicodeError, TypeError):
        return problem(400, 'Bad Request')
    stream = (encode_event(e) for e in events(store, actor, request, **options))
    return 200, {'Content-Type':'text/event-stream', 'Cache-Control':'no-store'}, stream
