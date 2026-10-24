"""Atomic linked contract through the real fixture engine/compiler, no execution."""
import copy
import json
import v536_information_function_contracts_native as n

f, owner, fn = n.f, n.owner, n.fn
mode = n.a.mode
signature = {'args': [{'name': 'amount2', 'type': 'long'}, {'name': 'count', 'type': 'long'}], 'return': 'long'}
original_signature = {'args': [{'name': 'amount', 'type': 'long'}, {'name': 'count', 'type': 'long'}], 'return': 'long'}
target_name = 'amount2'
if mode == 'targets':
    n.add_targets_and_wrapper()
    signature = {'args': [{'name': 'count', 'type': 'long'}, {'name': 'amount', 'type': 'long'}], 'return': 'long'}
    target_name = 'amount'
if mode == 'scoped':
    import re
    function_file = f.project / ('elements/' + fn.split('::')[1] + '.celem')
    function_file.write_text(function_file.read_text().replace('provide ' + fn + ' with ' + fn + 'Body;', ''))
    n.a.info.write_text(n.a.info.read_text().replace('{', '{provide ' + fn + ' with ' + fn + 'Body;', 1))
    caller_file = f.project / 'CallerBody.celem'
    caller_file.write_text(re.sub(r'(import [^;]+)(;)', r'\1 in ' + owner + r'\2', caller_file.read_text()))
snapshot = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}


def rpc(action, ok=True, **body):
    return f.invoke('blueprint', {'action': action, **body}, ok)['result'].get('result')


def schema():
    f.invoke('schema', {'id': owner})
    return f.state()['schema']


def prepare():
    s = schema()
    method = next(row for row in s['ownFunctions'] if row['id'] == fn)
    basis = rpc('readOwnerEdits', id=owner, hash=s['textHash'])
    return {'id': owner, 'rows': [], 'basis': basis['basis'], 'declaration': {'id': owner, 'hash': s['textHash'], 'changes': [{'type': 'function-edit', 'id': fn, 'hash': method['hash'], 'name': method['name'], 'description': method['description'], 'signature': signature, 'mapping': {'before': original_signature, 'args': {'amount': target_name, 'count': 'count'}}}]}}


def files_unchanged():
    assert all((f.project / path).read_bytes() == text for path, text in snapshot.items())


def verify():
    assert n.canonical(next(row for row in schema()['ownFunctions'] if row['id'] == fn)['signature']) == signature
    checkpoint = json.loads(checkpoint_path.read_text())
    rows = {row['id']: row for row in checkpoint['changes']}
    group = set(rows[owner]['atomicEditGroup'])
    assert {owner, fn, fn + 'Body', fn + 'Body/body:common', n.caller + 'Body/body:common', f.n + 'ProjectManifest'} <= group
    graph = json.loads(rows[fn + 'Body/body:common']['draft'])
    call = json.loads(rows[n.caller + 'Body/body:common']['draft'])['nodes'][0]
    assert graph['nodes'][0]['arguments']['amount'] == {'input': target_name}
    assert call['arguments'] == {target_name: {'input': 'first'}, 'count': {'input': 'second'}}
    assert call['signature'] == signature and graph['nodes'][0]['signature'] == original_signature
    assert json.loads(rows[fn + 'Body/body:common/node:body']['draft'])['source'] == n.record['source']
    if mode == 'targets':
        assert {fn + 'Body/body:windows', fn + 'Body/body:windows/node:body'} <= group
        assert json.loads(rows[fn + 'Body/body:windows/node:body']['draft'])['source'] == n.record['source']
        assert call['postCall']['source'] == json.loads(snapshot['caller.graph.json'])['nodes'][0]['postCall']['source']
    return sorted(group)


try:
    f.start(0)
    f.invoke('select', {'id': owner})
    f.invoke('saveDraft', {})
    checkpoint_path = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    before = checkpoint_path.read_bytes()
    request = prepare()
    if mode == 'guards':
        cases = []
        for field, value in [('id', 'Other.Project::Function'), ('hash', '0' * 64), ('allowExecution', True)]:
            bad = copy.deepcopy(request)
            bad['declaration']['changes'][0][field] = value
            cases.append(bad)
        bad = copy.deepcopy(request)
        bad['declaration']['id'] = 'Other.Project::Information'
        cases.append(bad)
        for mapping in [
            {'before': signature, 'args': {'amount': 'amount2', 'count': 'count'}},
            {'before': original_signature, 'args': {'amount': 'amount2', 'count': 'amount2'}},
            {'before': original_signature, 'args': {'amount': None, 'count': 'count'}},
        ]:
            bad = copy.deepcopy(request)
            bad['declaration']['changes'][0]['mapping'] = mapping
            cases.append(bad)
        for bad in cases:
            rpc('applySlots', False, **bad)
            assert checkpoint_path.read_bytes() == before
            assert n.canonical(next(row for row in schema()['ownFunctions'] if row['id'] == fn)['signature']) == original_signature
            files_unchanged()
        f.checked('서버는 다른 프로젝트·위조 hash/권한·stale/중복/연결 유실 pin 대응을 전체 미적용으로 거절한다')
    elif mode == 'source':
        caller_file = f.project / 'caller.graph.json'
        peer = json.loads(caller_file.read_text())
        peer['nodes'][0]['intent'] = '다른 편집자가 변경한 실제 caller 원문'
        caller_file.write_text(json.dumps(peer, ensure_ascii=False))
        peer_bytes = caller_file.read_bytes()
        rpc('applySlots', False, **request)
        assert checkpoint_path.read_bytes() == before and caller_file.read_bytes() == peer_bytes
        assert n.canonical(next(row for row in schema()['ownFunctions'] if row['id'] == fn)['signature']) == original_signature
        assert all((f.project / path).read_bytes() == text for path, text in snapshot.items() if path != 'caller.graph.json')
        f.checked('실제 caller 파일이 바뀌면 원래 source 기준으로 전체 거절하며 peer 원문·기존 checkpoint를 보존한다')
    elif mode == 'conflict':
        s = schema()
        f.invoke('editDescription', {'id': owner, 'hash': s['textHash'], 'revision': s['revision'], 'value': '경합 입력 유지'})
        text = f.state()['draft']['text']
        rpc('applySlots', False, **request)
        assert f.state()['draft']['text'] == text and checkpoint_path.read_bytes() == before
        files_unchanged()
        f.checked('원래 closure 뒤 실제 동시 수정은 선언·구현·호출자 모두 미적용으로 거절한다')
    else:
        if mode == 'storage':
            checkpoint_path.chmod(0o400)
            try:
                rpc('applySlots', False, **request)
                assert checkpoint_path.read_bytes() == before
                assert n.canonical(next(row for row in schema()['ownFunctions'] if row['id'] == fn)['signature']) == original_signature
                files_unchanged()
            finally:
                checkpoint_path.chmod(0o600)
            f.checked('checkpoint 쓰기 실패는 함수·구현·호출 graph·기존 초안을 모두 보존한다')
        result = rpc('applySlots', **request)
        assert result['atomic'] and result['checkpointSaved']
        ids = verify()
        files_unchanged()
        saved = checkpoint_path.read_bytes()
        f.stop()
        f.start(1)
        f.invoke('select', {'id': owner})
        assert verify() == ids and checkpoint_path.read_bytes() == saved
        files_unchanged()
        f.checked('한 후보/CAS 저장과 cold는 명시 핀 대응·callee/consumer 전체 그룹·C# 원문을 보존한다')
        f.invoke('reviewGroup', {'ids': ids, 'target': 'portable'})
        review = f.state()['review']
        assert review['status'] == 'ready', review
        f.invoke('confirmGroup', {'ids': ids, 'token': review['token']})
        for path, text in snapshot.items():
            if path not in {'FreeInfo.celem', 'elements/' + fn.split('::')[1] + '.celem', fn.split('::')[1] + 'Body.celem', 'function.graph.json', 'function.node.json', 'caller.graph.json', 'function-windows.graph.json', 'function-windows.node.json'}:
                assert (f.project / path).read_bytes() == text, path
        f.stop()
        f.start(2)
        f.invoke('select', {'id': owner})
        assert n.canonical(next(row for row in schema()['ownFunctions'] if row['id'] == fn)['signature']) == signature
        assert json.loads((f.project / 'function.node.json').read_text())['source'] == n.record['source']
        f.checked('실제 compiler Review/Confirm·cold는 해당 전체 계약만 반영하고 다른 함수·부모·원문을 유지한다')
except Exception:
    try:
        (f.case / 'contracts-api-failure.json').write_text(json.dumps({'state': f.state(), 'checks': f.checks}, ensure_ascii=False, indent=2))
    except Exception:
        pass
    raise
finally:
    print(json.dumps({'checks': f.checks, 'mode': mode, 'evidence': str(f.case), 'actualEngine': True, 'nativeWindows': False, 'accountOrInference': False}, ensure_ascii=False))
    f.stop()
