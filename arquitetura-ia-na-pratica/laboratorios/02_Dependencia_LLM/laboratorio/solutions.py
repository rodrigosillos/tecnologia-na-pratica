"""Executable solutions to exercises 3 and 4. No external dependencies."""
import json
from boundary import plan_context, finalize, prepare_context
from chapter1 import read_data


def exercise3():
    chunks = [{'id':'A','tokens':1200}, {'id':'B','tokens':1000},
              {'id':'C','tokens':900}]
    plan = plan_context(900, chunks)
    larger_output = plan_context(900, chunks, output=1024)
    assert plan['selected'] == ['A', 'B']
    assert plan['input_tokens'] + 512 + 128 == 3740
    assert plan['slack'] == 356
    assert larger_output['selected'] == ['A']
    return {'output_512':plan, 'output_1024':larger_output,
            'overflow_if_all_included':544}


def exercise4():
    data = read_data()
    case = data['cases'][0]
    docs, _ = prepare_context(case, data['documents'])
    good = {'status':'answer', 'fact_id':'return_30d',
            'citation':'acme-returns-v2', 'reason':None}
    event = {'state':'incomplete', 'chunks':[json.dumps(good)],
             'usage':{'input_tokens':180,'output_tokens':50},
             'first_ms':80, 'end_ms':240}
    first = finalize(event, case, docs)
    assert first == ('incomplete', None)
    event['state'] = 'completed'
    bad = dict(good, fact_id='return_999d')
    event['chunks'] = [json.dumps(bad)]
    second = finalize(event, case, docs)
    assert second == ('unsupported', None)
    raw = json.dumps(dict(reversed(list(good.items()))), indent=2)
    event['chunks'] = [raw[:30], raw[30:]]
    third = finalize(event, case, docs)
    assert third == ('accepted', good)
    return {'complete_json_incomplete_event':first,
            'valid_shape_unsupported_fact':second,
            'changed_serialization_same_fact':third}


if __name__=='__main__':
    print(json.dumps({'exercise3':exercise3(), 'exercise4':exercise4()},
                     indent=2))
