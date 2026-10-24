"""Atomic out rename with a real scoped consumer and compiler; fixture only."""
import copy
import json
import v536_information_out_fixture as x

f, owner, fn = x.f, x.owner, x.fn


def rpc(action, ok=True, **body):
    return f.invoke('blueprint', {'action': action, **body}, ok)['result'].get('result')


def schema():
    f.invoke('schema', {'id': owner})
    return f.state()['schema']


def prepare():
    s = schema()
    method = next(row for row in s['ownFunctions'] if row['id'] == fn)
    basis = rpc('readOwnerEdits', id=owner, hash=s['textHash'])
    return {'id': owner, 'rows': [], 'basis': basis['basis'], 'declaration': {'id': owner, 'hash': s['textHash'], 'changes': [x.change(method)]}}


def files_unchanged():
    assert all((f.project / path).read_bytes() == content for path, content in x.snapshot.items())


def verify():
    assert x.n.canonical(next(row for row in schema()['ownFunctions'] if row['id'] == fn)['signature']) == x.signature
    rows = {row['id']: row for row in json.loads(checkpoint.read_text())['changes']}
    x.assert_graphs(rows)
    group = set(rows[owner]['atomicEditGroup'])
    assert {owner, fn, fn + 'Body', fn + 'Body/body:common', x.caller + 'Body/body:common', f.n + 'ProjectManifest'} <= group
    published = f.metadata('blueprintOutputSnapshot', functionText=rows[fn]['draft'])
    assert [row['name'] for row in published['fields']] == ['count2']
    return sorted(group)


try:
    f.start(0)
    f.invoke('select', {'id': owner})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    before = checkpoint.read_bytes()
    request = prepare()
    if x.mode == 'wrapper':
        rpc('applySlots', False, **request)
        assert checkpoint.read_bytes() == before
        assert x.n.canonical(next(row for row in schema()['ownFunctions'] if row['id'] == fn)['signature']) == x.original_signature
        files_unchanged()
        f.checked('기존 공개 출력 이름을 읽는 C# 후처리는 자동 재작성하지 않고 전체 미적용·입력/원문 보존으로 거절한다')
    elif x.mode == 'guards':
        candidates = []
        for edit in ['type', 'remove', 'return', 'role', 'duplicate', 'label']:
            bad = copy.deepcopy(request)
            c = bad['declaration']['changes'][0]
            if edit == 'type':
                c['signature']['args'][1]['type'] = 'string'
            elif edit == 'remove':
                c['signature']['args'].pop()
                c['mapping']['args']['count'] = None
            elif edit == 'return':
                c['signature']['return'] = 'void'
            elif edit == 'role':
                c['signature']['args'][1]['mode'] = 'ref'
            elif edit == 'duplicate':
                c['mapping']['args']['amount'] = 'count2'
            else:
                c['signature']['args'][1]['name'] = '출력 이름'
                c['mapping']['args']['count'] = '출력 이름'
            candidates.append(bad)
        for bad in candidates:
            rpc('applySlots', False, **bad)
            assert checkpoint.read_bytes() == before
            assert x.n.canonical(next(row for row in schema()['ownFunctions'] if row['id'] == fn)['signature']) == x.original_signature
            files_unchanged()
        f.checked('연결/구현이 남은 출력 타입·삭제·반환 삭제·ref 역할·중복 대응·native 식별자 밖의 이름은 거절하고 원래 후보를 보존한다')
    else:
        if x.mode == 'storage':
            checkpoint.chmod(0o400)
            try:
                rpc('applySlots', False, **request)
                assert checkpoint.read_bytes() == before
                assert x.n.canonical(next(row for row in schema()['ownFunctions'] if row['id'] == fn)['signature']) == x.original_signature
                files_unchanged()
            finally:
                checkpoint.chmod(0o600)
            f.checked('out 저장 실패는 선언·내보내기·consumer·공개 metadata와 checkpoint를 전부 유지한다')
        result = rpc('applySlots', **request)
        assert result['atomic'] and result['checkpointSaved']
        ids = verify()
        files_unchanged()
        f.stop()
        f.start(1)
        f.invoke('select', {'id': owner})
        assert verify() == ids
        files_unchanged()
        f.checked('out 이름/선택한 설명·입력 이름은 같은 후보로 저장/cold 복원하며 내부 C#·내보내기 ID·소비 연결을 보존한다')
        f.invoke('reviewGroup', {'ids': ids, 'target': 'portable'})
        review = f.state()['review']
        assert review['status'] == 'ready', review
        f.invoke('confirmGroup', {'ids': ids, 'token': review['token']})
        for path, content in x.snapshot.items():
            if path not in {'FreeInfo.celem', 'elements/' + fn.split('::')[1] + '.celem', fn.split('::')[1] + 'Body.celem', 'function.graph.json', 'function.node.json', 'caller.graph.json'}:
                assert (f.project / path).read_bytes() == content, path
        f.stop()
        f.start(2)
        f.invoke('select', {'id': owner})
        assert x.n.canonical(next(row for row in schema()['ownFunctions'] if row['id'] == fn)['signature']) == x.signature
        assert json.loads((f.project / 'function.node.json').read_text())['source'] == x.record['source']
        f.checked('실제 compiler Review/Confirm·재시작은 새 out 계약만 반영하며 C# 원문·다른 함수·부모를 보존한다')
except Exception:
    try:
        (f.case / 'out-api-failure.json').write_text(json.dumps({'state': f.state(), 'checks': f.checks}, ensure_ascii=False, indent=2))
    except Exception:
        pass
    raise
finally:
    print(json.dumps({'checks': f.checks, 'mode': x.mode, 'evidence': str(f.case), 'actualEngine': True, 'nativeWindows': False, 'accountOrInference': False}, ensure_ascii=False))
    f.stop()
