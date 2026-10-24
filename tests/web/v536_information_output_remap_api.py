"""Whole writer/exit type changes: exact receipts, atomicity and compiler path."""
import copy
import json
import v536_information_output_remap_fixture as x

f, owner, fn = x.f, x.owner, x.fn


def rpc(action, ok=True, **body):
    return f.invoke('blueprint', {'action': action, **body}, ok)['result'].get('result')


def request():
    f.invoke('schema', {'id': owner})
    s = f.state()['schema']
    method = next(r for r in s['ownFunctions'] if r['id'] == fn)
    preview = rpc('readOwnerEdits', id=owner, hash=s['textHash'], includeFunctionInputs=fn, includeFunctionOutputGraphs=True, includeFunctionOutputs=True)
    return {'id': owner, 'rows': [], 'basis': preview['basis'], 'declaration': {'id': owner, 'hash': s['textHash'], 'changes': [{'type': 'function-edit', 'id': fn, 'hash': method['hash'], 'name': method['name'], 'description': method['description'], 'signature': x.new, 'mapping': x.selections(preview)}]}}


try:
    f.start(0)
    f.invoke('select', {'id': owner})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    before = checkpoint.read_bytes()
    for fault in ['missing-writer', 'missing-exit', 'hash', 'before', 'source', 'consumer', 'foreign', 'duplicate', 'operator'] + (['zero'] if x.typ == 'double' else []):
        bad = request()
        m = bad['declaration']['changes'][0]['mapping']
        selected = next(iter(m['outputs'].values()))
        if fault == 'missing-writer':
            del m['outputs'][next(iter(m['outputs']))]
        elif fault == 'missing-exit':
            del m['outputs'][next(key for key, row in m['outputs'].items() if row['node'].startswith('$exit:'))]
        elif fault == 'hash':
            selected['hash'] = '0' * 64
        elif fault == 'before':
            selected['before'] = 'null'
        elif fault == 'source':
            list(m['outputs'].values())[-1]['source'] = {'input': 'amount'}
        elif fault == 'consumer':
            next(iter(m['callers'].values()))['outputs']['count'] = None
        elif fault == 'foreign':
            selected['source'] = {'node': 'other_project'}
        elif fault == 'duplicate':
            m['outputs']['unknown-writer'] = copy.deepcopy(selected)
        else:
            selected['source'] = {'binary': {'operator': '/' if fault == 'zero' else 'UNKNOWN', 'operands': [{'constant': 1.0}, {'constant': 0.0}]}}
        rpc('applySlots', False, **bad)
        assert checkpoint.read_bytes() == before
        assert all((f.project / p).read_bytes() == content for p, content in x.snapshot.items())
    assert x.maps['count'] == ('spare' if x.kind == 'mixed' else 'return')
    f.invoke('schema', {'id': owner})
    assert x.n.canonical(next(row for row in f.state()['schema']['ownFunctions'] if row['id'] == fn)['signature']) == x.old
    f.checked('누락된 writer/exit·오래된 기준·마지막 잘못된 값·미대응 소비자·다른 source는 모든 변경을 미적용으로 유지한다')
    if x.mode.endswith('storage'):
        req = request()
        checkpoint.chmod(0o400)
        try:
            rpc('applySlots', False, **req)
            assert checkpoint.read_bytes() == before
        finally:
            checkpoint.chmod(0o600)
        f.checked('다중 writer 저장 실패는 모든 타입/값/소비 대응 및 기존 checkpoint를 보존한다')
    result = rpc('applySlots', **request())
    assert result['atomic'] and result['checkpointSaved']
    ids = x.verify(checkpoint)
    assert all((f.project / p).read_bytes() == content for p, content in x.snapshot.items())
    f.stop()
    f.start(1)
    f.invoke('select', {'id': owner})
    assert x.verify(checkpoint) == ids
    f.checked('각 writer·exit의 정확한 typed 값과 출력 소비 대응을 단일 후보/CAS로 저장·cold 복원한다')
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
    assert json.loads((f.project / 'provider.node.json').read_text())['source'] == x.provider_record['source']
    for path, content in x.snapshot.items():
        if path not in {'FreeInfo.celem', 'elements/' + fn.split('::')[1] + '.celem', fn.split('::')[1] + 'Body.celem', 'function.graph.json', 'function.node.json', 'provider.node.json', 'CallerBody.celem', 'caller.graph.json'}:
            assert (f.project / path).read_bytes() == content, path
    f.checked('실제 compiler Review/Confirm·cold는 C#·상속 원본·다른 자료를 보존한 새 출력 계약만 반영한다')
finally:
    print(json.dumps({'checks': f.checks, 'mode': x.mode, 'evidence': str(f.case), 'actualEngine': True, 'nativeWindows': False}, ensure_ascii=False))
    f.stop()
