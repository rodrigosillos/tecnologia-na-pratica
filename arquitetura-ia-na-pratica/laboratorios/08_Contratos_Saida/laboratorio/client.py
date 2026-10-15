"""Strict finite-stream reader for this lab's LF/one-data-line SSE profile."""
from contract import (ContractError, MAX_FRAME, MAX_STREAM, require,
                      strict_json, validate_event)

class Client:
    def __init__(self, request_id, query_ids):
        self.request_id = request_id
        self.query_ids = list(query_ids)
        self.state = 'waiting'
        self.seq = 0
        self.progress = []
        self.result = None
        self.error = None
        self.buffer = b''
        self.bytes_seen = 0

    def accept(self, event):
        validate_event(event)
        require(self.state in ('waiting', 'running'), 'after_terminal')
        require(event['request_id'] == self.request_id, 'request_mismatch')
        require(event['seq'] == self.seq + 1, 'sequence_gap_or_replay')
        kind = event['kind']
        if self.state == 'waiting':
            require(kind == 'accepted', 'missing_accepted')
            self.state = 'running'
        else:
            require(kind != 'accepted', 'duplicate_accepted')
            if kind == 'progress':
                self.progress.append(event['data']['stage'])
            elif kind == 'result':
                require([i['id'] for i in event['data']['items']] == self.query_ids,
                        'query_mismatch')
                self.result = event['data']
                self.state = 'completed'
            elif kind == 'error':
                self.error = event['data']; self.state = 'failed'
            elif kind == 'cancelled':
                self.state = 'cancelled'
        self.seq = event['seq']

    def feed(self, chunk):
        require(type(chunk) is bytes, 'byte_input')
        self.bytes_seen += len(chunk)
        require(self.bytes_seen <= MAX_STREAM, 'stream_limit')
        self.buffer += chunk
        while b'\n\n' in self.buffer:
            raw, self.buffer = self.buffer.split(b'\n\n', 1)
            require(len(raw)+2 <= MAX_FRAME, 'frame_limit')
            try:
                lines = raw.decode('utf-8', errors='strict').split('\n')
            except UnicodeError as exc:
                raise ContractError('utf8') from exc
            require(len(lines) == 3, 'frame_fields')
            require(lines[0].startswith('event: ') and lines[1].startswith('id: ')
                    and lines[2].startswith('data: '), 'frame_profile')
            event = validate_event(strict_json(lines[2][6:]))
            require(lines[0][7:] == event['kind'], 'event_mismatch')
            require(lines[1][4:] == f"{event['request_id']}/{event['seq']}", 'id_mismatch')
            self.accept(event)
        require(len(self.buffer) <= MAX_FRAME, 'frame_limit')

    def finish(self):
        require(not self.buffer, 'unfinished_frame')
        require(self.state in ('completed', 'failed', 'cancelled'), 'incomplete_stream')

def consume(chunks, request_id, query_ids):
    client = Client(request_id, query_ids)
    try:
        for chunk in chunks:
            client.feed(chunk)
        client.finish()
    except ContractError:
        client.result = None
        client.state = 'protocol_error'
        raise
    return client

def fragments(data, size=7):
    require(type(size) is int and size > 0, 'fragment_size')
    for start in range(0, len(data), size):
        yield data[start:start+size]
