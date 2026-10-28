"""Retain the earlier input-only rename/type path when no outputs change."""
import copy
import json
import v536_information_shared_types_fixture as x

r = x.request()
for row in r['changes']:
    row['signature']['args'][1]['name'] = 'retained'
    row['mapping']['args']['count'] = 'retained'
    for caller in row['mapping']['callers'].values():
        caller['inputs']['retained'] = caller['inputs'].pop('count')
    for use in row['mapping']['implementations'].values():
        use['value'] = {'input': 'retained'}
for row in r['changes']:
    single = copy.deepcopy(r); single['changes'] = [row]; x.n.prepare(single)
x.unchanged()
if x.mode == 'reject':
    x.n.prepare(r, False); x.f.checked('넓은 새 가드는 원래 유효한 출력 없는 입력 전용 이름/타입 결합을 과도하게 거절한다')
else:
    result = x.n.prepare(r); updates = result['updates']+result['linkedUpdates']
    caller = json.loads(next(row['text'] for row in updates if row['id'] == x.n.caller+'Body/body:common'))
    for node in caller['nodes']:
        assert node['arguments'] == {'amount': {'constant': '새 한글 값'}, 'retained': {'input': 'second'}}
    for fn in x.functions:
        leaf = json.loads(next(row['text'] for row in updates if row['id'] == fn+'Body/body:common'))
        code = next(row for row in leaf['nodes'] if row['id'] == 'body')
        assert code['signature'] == x.old and code['arguments'] == {'amount': {'input': 'retained'}, 'count': {'input': 'retained'}}
        assert json.loads(next(row['text'] for row in updates if row['id'] == fn+'Body/body:common/node:body'))['source'] == json.loads(x.snapshot['function.node.json' if fn == x.functions[0] else 'second.node.json'])['source']
    reverse = copy.deepcopy(r); reverse['changes'].reverse(); other = x.n.prepare(reverse)
    assert {row['id']: row['text'] for row in updates} == {row['id']: row['text'] for row in other['updates']+other['linkedUpdates']}
    x.unchanged(); x.f.checked('출력 없는 기존 입력 전용 이름/타입 결합은 원래 값·C#·원문과 역순 후보를 보존한다')
print(json.dumps({'checks': x.f.checks, 'evidence': str(x.f.case), 'actualWindows': False}, ensure_ascii=False))
