"""One CAS for overlapping input/output edits; real engine and fixture compiler."""
import copy
import json
import v536_information_io_fixture as x

f, owner, fn = x.f, x.owner, x.fn


def rpc(action, ok=True, **body):
    return f.invoke('blueprint', {'action': action, **body}, ok)['result'].get('result')


def request():
    f.invoke('schema', {'id': owner})
    s = f.state()['schema']
    method = next(r for r in s['ownFunctions'] if r['id'] == fn)
    preview = rpc('readOwnerEdits', id=owner, hash=s['textHash'], includeFunctionInputs=fn, includeFunctionOutputGraphs=True, includeFunctionOutputs=True)
    return {'id': owner, 'rows': [], 'basis': preview['basis'], 'declaration': {'id': owner, 'hash': s['textHash'], 'changes': [{'type': 'function-edit', 'id': fn, 'hash': method['hash'], 'name': method['name'], 'description': method['description'], 'signature': x.new, 'mapping': x.selections(preview)}]}}, preview


try:
    f.start(0)
    f.invoke('select', {'id': owner})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    before = checkpoint.read_bytes()
    req, preview = request()
    m = req['declaration']['changes'][0]['mapping']
    faults = ['caller'] + (['missing-output', 'output-before', 'duplicate-slot', 'source'] if m.get('outputs') else []) + (['missing-input', 'input-before', 'alias-type'] if m['implementations'] else []) + (['structure', 'created-source'] if m.get('outputGraphs') else [])
    for fault in faults:
        bad, preview = request()
        m = bad['declaration']['changes'][0]['mapping']
        if fault == 'caller':
            del m['callers'][next(iter(m['callers']))]
        elif fault == 'missing-output':
            del m['outputs'][next(iter(m['outputs']))]
        elif fault == 'output-before':
            next(iter(m['outputs'].values()))['before'] = 'null'
        elif fault == 'source':
            next(iter(m['outputs'].values()))['source'] = {'input': 'missing'}
        elif fault == 'duplicate-slot':
            output = next(iter(m['outputs'].values()))
            key = output['graph'] + '#' + output['node'] + '#value'
            use = preview['functionInputUses'][key]
            m['implementations'][key] = {k: use[k] for k in ['graph', 'node', 'argument', 'hash', 'before']} | {'value': {'valueJson': '7'}}
        elif fault == 'missing-input':
            del m['implementations'][next(iter(m['implementations']))]
        elif fault == 'input-before':
            next(iter(m['implementations'].values()))['before'] = 'null'
        elif fault == 'alias-type':
            next(v for k, v in m['implementations'].items() if '#$alias:' in k)['value'] = {'input': 'words'}
        elif fault == 'structure':
            next(iter(m['outputGraphs'].values()))['hash'] = '0' * 64
        else:
            next(iter(m['outputGraphs'].values()))['creates'][-1]['source'] = {'input': 'missing'}
        rpc('applySlots', False, **bad)
        assert checkpoint.read_bytes() == before
        assert all((f.project / p).read_bytes() == b for p, b in x.snapshot.items())
    f.checked('중첩된 입력/출력 선택의 누락·중복 대체·타입/원래 기준 오류·마지막 새 출력 오류는 후보 전체 미적용이다')
    req, _ = request()
    result = rpc('applySlots', **req)
    assert result['atomic'] and result['checkpointSaved']
    ids = x.verify(checkpoint)
    f.stop()
    f.start(1)
    f.invoke('select', {'id': owner})
    assert x.verify(checkpoint) == ids
    assert all((f.project / p).read_bytes() == b for p, b in x.snapshot.items())
    f.checked('현재 입력·출력 writer/exit·별칭·호출자 선택은 한 CAS로 저장·재시작하며 C#와 정확한 원문을 보존한다')
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
        if path not in {'FreeInfo.celem', 'elements/' + fn.split('::')[1] + '.celem', fn.split('::')[1] + 'Body.celem', 'function.graph.json', 'function.node.json', 'provider.node.json', 'CallerBody.celem', 'caller.graph.json'}:
            assert (f.project / path).read_bytes() == content, path
    f.checked('결합된 계약은 실제 compiler Review/Confirm·cold를 통과하고 다른 소스·부모·target은 보존된다')
finally:
    print(json.dumps({'checks': f.checks, 'kind': x.kind, 'evidence': str(f.case), 'actualEngine': True, 'actualWindows': False}, ensure_ascii=False))
    f.stop()
