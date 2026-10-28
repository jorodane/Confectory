"""Mixed targets explicitly coordinate a new output and a void return mapping."""
import copy
import json
import v536_information_mixed_target_fixture as x


def candidate(void=False):
    r = x.request()
    after = copy.deepcopy(x.new)
    after['args'].append({'name': 'result', 'type': 'long' if void else 'string', 'mode': 'out'})
    after['return'] = 'void' if void else 'long'
    r['changes'][0]['signature'] = after
    m = r['changes'][0]['mapping']
    for id, plan in m['bodies'].items():
        plan['contract'] = after
        if id == x.body_id:
            plan['signature'] = after
            plan['text'] = 'result=checked(text.Length+count);return;' if void else 'result=text;return checked(text.Length+count);'
        else:
            plan['text'] = ('calls.' + x.alias + '.Invoke("명시 호출",second,out long result);return result;') if void else ('return calls.' + x.alias + '.Invoke("명시 호출",second,out string result);')
    for plan in m['callers'].values():
        plan['outputs'] = {'return': 'result' if void else 'return'}
    rows = x.f.metadata('informationFunctionOutputGraphs', id=x.owner, function=x.fn, units=r['units'])
    m['outputGraphs'] = {}
    for id, row in rows.items():
        following = next((e['to'] for e in row['edges'] if e['from'] == 'body' and e['port'] == 'next'), '')
        m['outputGraphs'][id] = {'graph': id, 'hash': row['hash'], 'removes': [{'name': 'return', 'writers': row['writers']['return'], 'before': row['exits']['return']}] if void else [], 'creates': [{'node': 'explicit_result', 'name': 'result', 'type': 'long' if void else 'string', 'source': {'input': 'count' if void else 'text'}, 'after': 'body', 'next': '' if void else following}], 'publicOutputs': []}
    return r


for void in [False, True]:
    r = candidate(void)
    result = x.n.prepare(r)
    rows = {row['id']: row for row in result['linkedUpdates']}
    assert rows[x.body_id]['text'] == r['changes'][0]['mapping']['bodies'][x.body_id]['text']
    g = json.loads(rows[x.fn + 'Body/body:common']['text'])
    assert next(row for row in g['nodes'] if row['id'] == 'explicit_result')['output'] == 'result'
    if void:
        consumer = json.loads(rows[x.caller + 'Body/body:common']['text'])
        assert consumer['exits']['return'] == {'node': 'invoke', 'output': 'result'}
    for fault in ['graph', 'code']:
        bad = candidate(void)
        m = bad['changes'][0]['mapping']
        if fault == 'graph':
            next(iter(m['outputGraphs'].values()))['creates'][0]['source'] = {'input': 'missing'}
        else:
            m['bodies'][x.body_id]['text'] = 'return;' if void else 'return 0;'
        x.n.prepare(bad, False)
    assert all((x.f.project / path).read_bytes() == data for path, data in x.snapshot.items())
    print('PASS 혼합 출력 추가' + ('·void 반환 전환' if void else '') + '는 원래 writer/소비자 명시 대응·C# out 할당을 함께 검증하고 오류 시 전체 거절한다', flush=True)
print(json.dumps({'checks': 2, 'evidence': str(x.f.case), 'pureCandidate': True, 'executed': False}, ensure_ascii=False))
