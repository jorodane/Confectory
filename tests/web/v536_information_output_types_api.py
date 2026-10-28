"""Typed output Save/rejection/cold/compiler checks through the real engine."""
import copy
import json
import v536_information_output_types_fixture as x

f, owner, fn = x.f, x.owner, x.fn


def rpc(action, ok=True, **body):
    return f.invoke('blueprint', {'action': action, **body}, ok)['result'].get('result')


def schema():
    f.invoke('schema', {'id': owner})
    return f.state()['schema']


def request():
    s = schema()
    method = next(r for r in s['ownFunctions'] if r['id'] == fn)
    preview = rpc('readOwnerEdits', id=owner, hash=s['textHash'], includeFunctionInputs=fn, includeFunctionOutputs=True)
    return {'id': owner, 'rows': [], 'basis': preview['basis'], 'declaration': {'id': owner, 'hash': s['textHash'], 'changes': [{'type': 'function-edit', 'id': fn, 'hash': method['hash'], 'name': method['name'], 'description': method['description'], 'signature': x.new, 'mapping': x.selections(preview)}]}}


try:
    f.start(0)
    f.invoke('select', {'id': owner})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    before = checkpoint.read_bytes()
    for fault in ['missing', 'hash', 'before', 'type', 'source', 'consumer', 'caller-missing', 'unused']:
        bad = request()
        m = bad['declaration']['changes'][0]['mapping']
        selected = next(iter(m['outputs'].values()))
        if fault == 'missing':
            del m['outputs']
        elif fault == 'hash':
            selected['hash'] = '0' * 64
        elif fault == 'before':
            selected['before'] = 'null'
        elif fault == 'type':
            selected['type'] = 'long'
        elif fault == 'source':
            selected['source'] = {'input': 'amount'}
        elif fault == 'caller-missing':
            del next(iter(m['callers'].values()))['outputs']
        elif fault == 'consumer':
            next(iter(m['callers'].values()))['outputs'][x.name] = x.name
        else:
            m['outputs']['unknown'] = copy.deepcopy(selected)
        rpc('applySlots', False, **bad)
        assert checkpoint.read_bytes() == before
        assert all((f.project / p).read_bytes() == content for p, content in x.snapshot.items())
    f.checked('출력 source/hash/원래 binding/타입/소비자 대응 누락·위조는 전체 미적용이며 원문과 checkpoint를 보존한다')
    if x.mode.endswith('storage'):
        req = request()
        checkpoint.chmod(0o400)
        try:
            rpc('applySlots', False, **req)
            assert checkpoint.read_bytes() == before
        finally:
            checkpoint.chmod(0o600)
        f.checked('출력 타입과 caller 대응의 저장 실패는 부분 후보를 남기지 않는다')
    result = rpc('applySlots', **request())
    assert result['atomic'] and result['checkpointSaved']
    ids = x.verify(checkpoint)
    assert all((f.project / p).read_bytes() == content for p, content in x.snapshot.items())
    f.stop()
    f.start(1)
    f.invoke('select', {'id': owner})
    assert x.verify(checkpoint) == ids
    f.checked('명시적 출력 source·호환 caller 출력 대응은 선언/구현/import/본문과 한 후보로 저장·재시작한다')
    f.invoke('reviewGroup', {'ids': ids, 'target': 'portable'})
    review = f.state()['review']
    assert review['status'] == 'ready', review
    f.invoke('confirmGroup', {'ids': ids, 'token': review['token']})
    f.stop()
    f.start(2)
    f.invoke('select', {'id': owner})
    assert x.n.canonical(next(r for r in schema()['ownFunctions'] if r['id'] == fn)['signature']) == x.new
    assert json.loads((f.project / 'function.node.json').read_text())['source'] == x.record['source']
    for path, content in x.snapshot.items():
        if path not in {'FreeInfo.celem', 'elements/' + fn.split('::')[1] + '.celem', fn.split('::')[1] + 'Body.celem', 'function.graph.json', 'function.node.json', 'CallerBody.celem', 'caller.graph.json'}:
            assert (f.project / path).read_bytes() == content, path
    f.checked('실제 compiler Review/Confirm·cold는 새 출력 계약과 명시 소비 연결만 반영하고 C#/타 요소를 보존한다')
finally:
    print(json.dumps({'checks': f.checks, 'evidence': str(f.case), 'mode': x.mode, 'actualEngine': True, 'nativeWindows': False}, ensure_ascii=False))
    f.stop()
