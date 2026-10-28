"""Definition writer/consumer/route closure, rejection, cold and compiler."""
import copy
import json
import v536_information_output_definitions_fixture as x

f, owner, fn = x.f, x.owner, x.fn


def rpc(action, ok=True, **body):
    return f.invoke('blueprint', {'action': action, **body}, ok)['result'].get('result')


def request():
    f.invoke('schema', {'id': owner})
    s = f.state()['schema']
    method = next(r for r in s['ownFunctions'] if r['id'] == fn)
    preview = rpc('readOwnerEdits', id=owner, hash=s['textHash'], includeFunctionInputs=fn, includeFunctionOutputGraphs=True)
    return {'id': owner, 'rows': [], 'basis': preview['basis'], 'declaration': {'id': owner, 'hash': s['textHash'], 'changes': [{'type': 'function-edit', 'id': fn, 'hash': method['hash'], 'name': method['name'], 'description': method['description'], 'signature': x.new, 'mapping': x.selections(preview)}]}}


try:
    f.start(0)
    f.invoke('select', {'id': owner})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    before = checkpoint.read_bytes()
    faults = ['missing', 'hash', 'public', 'caller'] + (['writer'] if x.removed else []) + (['route', 'source'] if x.added else [])
    for fault in faults:
        bad = request()
        m = bad['declaration']['changes'][0]['mapping']
        selected = next(iter(m['outputGraphs'].values()))
        if fault == 'missing':
            del m['outputGraphs']
        elif fault == 'hash':
            selected['hash'] = '0' * 64
        elif fault == 'public':
            selected['publicOutputs'].append('forged')
        elif fault == 'caller':
            next(iter(m['callers'].values()))['outputs'][x.consumed] = None
        elif fault == 'writer':
            selected['removes'][0]['writers'] = ['wrong']
        elif fault == 'route':
            selected['creates'][0]['next'] = 'other'
        else:
            selected['creates'][-1]['source'] = {'input': 'real'}
        rpc('applySlots', False, **bad)
        assert checkpoint.read_bytes() == before
        assert all((f.project / p).read_bytes() == content for p, content in x.snapshot.items())
    f.checked('출력 전체 writer·소비자·값·경로·공개 metadata의 누락/위조는 부분 적용 없이 원문과 checkpoint를 보존한다')
    if x.mode.endswith('storage'):
        req = request()
        checkpoint.chmod(0o400)
        try:
            rpc('applySlots', False, **req)
            assert checkpoint.read_bytes() == before
        finally:
            checkpoint.chmod(0o600)
        f.checked('출력 정의의 저장 실패는 선언/모든 writer/소비 연결을 전부 미적용으로 유지한다')
    result = rpc('applySlots', **request())
    assert result['atomic'] and result['checkpointSaved']
    ids = x.verify(checkpoint)
    assert all((f.project / p).read_bytes() == content for p, content in x.snapshot.items())
    f.stop()
    f.start(1)
    f.invoke('select', {'id': owner})
    assert x.verify(checkpoint) == ids
    f.checked('출력 추가/삭제·void 전환의 명시 값과 실행 경로·소비자 대응은 한 후보로 저장·재시작한다')
    f.invoke('reviewGroup', {'ids': ids, 'target': 'portable'})
    review = f.state()['review']
    assert review['status'] == 'ready', review
    f.invoke('confirmGroup', {'ids': ids, 'token': review['token']})
    f.stop()
    f.start(2)
    f.invoke('select', {'id': owner})
    f.invoke('schema', {'id': owner})
    assert x.n.canonical(next(r for r in f.state()['schema']['ownFunctions'] if r['id'] == fn)['signature']) == x.new
    assert json.loads((f.project / 'function.node.json').read_text())['source'] == x.record['source']
    for path, content in x.snapshot.items():
        if path not in {'FreeInfo.celem', 'elements/' + fn.split('::')[1] + '.celem', fn.split('::')[1] + 'Body.celem', 'function.graph.json', 'function.node.json', 'CallerBody.celem', 'caller.graph.json'}:
            assert (f.project / path).read_bytes() == content, path
    f.checked('실제 compiler Review/Confirm·cold는 명시 출력 계약만 반영하며 C#·부모·다른 소스를 보존한다')
finally:
    print(json.dumps({'checks': f.checks, 'mode': x.mode, 'evidence': str(f.case), 'actualEngine': True, 'nativeWindows': False}, ensure_ascii=False))
    f.stop()
