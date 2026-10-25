"""Actual checkpoint and compiler boundary for explicitly edited C# and ABI."""
import copy
import json
import v536_information_csharp_fixture as x

f, owner, fn = x.f, x.owner, x.fn


def rpc(action, ok=True, **input):
    return f.invoke('blueprint', {'action': action, **input}, ok)['result'].get('result')


def request():
    f.invoke('schema', {'id': owner})
    s = f.state()['schema']
    method = next(r for r in s['ownFunctions'] if r['id'] == fn)
    preview = rpc('readOwnerEdits', id=owner, hash=s['textHash'], includeFunctionInputs=fn, includeFunctionBodies=True)
    return {'id': owner, 'rows': [], 'basis': preview['basis'], 'declaration': {'id': owner, 'hash': s['textHash'], 'changes': [{'type': 'function-edit', 'id': fn, 'hash': method['hash'], 'name': method['name'], 'description': method['description'], 'signature': x.new, 'mapping': x.selections(preview)}]}}


try:
    f.start(0)
    f.invoke('select', {'id': owner})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    baseline = checkpoint.read_bytes()
    for fault in ['missing', 'source-hash', 'old-contract', 'syntax', 'type', 'outside', 'caller']:
        bad = request()
        m = bad['declaration']['changes'][0]['mapping']
        b = m['bodies'][x.body_id]
        if fault == 'missing':
            m.pop('bodies')
        elif fault == 'source-hash':
            b['hash'] = '0' * 64
        elif fault == 'old-contract':
            b['contract'] = x.old
        elif fault == 'syntax':
            b['text'] = 'return ; }'
        elif fault == 'type':
            b['text'] = x.original
        elif fault == 'outside':
            m['bodies']['Other.Project::Body/body:common'] = copy.deepcopy(b)
        else:
            if m['callers']:
                m['callers'].clear()
            else:
                m['bodies'].pop(x.caller + 'Body/body:common')
        rpc('applySlots', False, **bad)
        assert checkpoint.read_bytes() == baseline
        assert all((f.project / p).read_bytes() == v for p, v in x.snapshot.items())
    f.checked('명시 C# 본문·현재 계약·호출자 누락 및 컴파일/경로/기준 오류는 전체 미적용이며 원문/checkpoint를 보존한다')
    result = rpc('applySlots', **request())
    assert result['atomic'] and result['checkpointSaved']
    ids = x.verify(checkpoint)
    f.stop()
    f.start(1)
    f.invoke('select', {'id': owner})
    assert x.verify(checkpoint) == ids
    f.checked('직접 쓴 C# 원문과 함수·구현·호출 인자는 한 후보/CAS로 저장·재시작 복원하며 원본 파일은 유지한다')
    f.invoke('reviewGroup', {'ids': ids, 'target': 'portable'})
    review = f.state()['review']
    assert review['status'] == 'ready', review
    f.invoke('confirmGroup', {'ids': ids, 'token': review['token']})
    f.stop()
    f.start(2)
    f.invoke('select', {'id': owner})
    edited_files = getattr(x, 'edited_files', {x.body_path: x.edited})
    for p, text in edited_files.items():
        assert (f.project / p).read_bytes() == text.encode()
    f.invoke('schema', {'id': owner})
    assert x.n.canonical(next(r for r in f.state()['schema']['ownFunctions'] if r['id'] == fn)['signature']) == x.new
    for p, v in x.snapshot.items():
        if p not in {'FreeInfo.celem', 'elements/' + fn.split('::')[1] + '.celem', fn.split('::')[1] + 'Body.celem', x.body_path, 'CallerBody.celem', 'caller.graph.json'} | set(edited_files):
            assert (f.project / p).read_bytes() == v, p
    f.checked('실제 compiler Review/Confirm·cold에서만 C#와 계약을 함께 반영하고 다른 함수·부모·target을 보존한다')
finally:
    print(json.dumps({'checks': f.checks, 'actualEngine': True, 'evidence': str(f.case), 'nativeWindows': False}, ensure_ascii=False))
    f.stop()
