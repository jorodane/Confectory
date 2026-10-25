"""Copy UI is not authority to mutate an inherited parent or public ABI."""
import json
import subprocess
import v536_information_inherited_copy_fixture as x

f, owner, fn = x.f, x.owner, x.fn
try:
    f.start(0)
    f.invoke('select', {'id': owner})
    f.invoke('saveDraft', {})
    s = x.schema()
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    original_checkpoint = checkpoint.read_bytes()
    p = x.rpc('readOwnerEdits', id=owner, hash=s['textHash'],
              includeFunctionInputs=fn, includeFunctionBodies=True)
    method = next(r for r in s['ownFunctions'] if r['id'] == fn)
    body_id = x.parent + '/body:common'
    body = p['functionBodies'][body_id]
    signature = x.b.old
    plan = {k: body[k] for k in ['hash', 'path']}
    plan.update(beforeSignature=body['signature'], signature=body['signature'],
                contract=signature, text=body['text'] + '// not a local copy\n')
    change = {'type': 'function-edit', 'id': fn, 'hash': method['hash'],
              'name': method['name'], 'description': method['description'],
              'signature': signature, 'mapping': {'before': signature,
              'args': {'amount': 'amount', 'count': 'count'},
              'bodies': {body_id: plan}}}
    x.rpc('applySlots', False, id=owner, rows=[], basis=p['basis'],
          declaration={'id': owner, 'hash': s['textHash'], 'changes': [change]})
    assert checkpoint.read_bytes() == original_checkpoint
    assert all((f.project / path).read_bytes() == value for path, value in x.snapshot.items())
    f.checked('위조된 본문 계획으로 부모를 수정하려 해도 같은 ABI의 예외를 쓰기 권한으로 사용할 수 없다')
    p = x.rpc('readOwnerEdits', id=owner, hash=s['textHash'],
              includeFunctionInputs=fn, includeFunctionBodies=True)
    changed = json.loads(json.dumps(signature))
    changed['args'][0]['name'] = 'changed'
    change['signature'] = changed
    change['mapping'] = {'before': signature,
                         'args': {'amount': 'changed', 'count': 'count'}}
    x.rpc('applySlots', False, id=owner, rows=[], basis=p['basis'],
          declaration={'id': owner, 'hash': s['textHash'], 'changes': [change]})
    assert checkpoint.read_bytes() == original_checkpoint
    assert all((f.project / path).read_bytes() == value for path, value in x.snapshot.items())
    f.checked('직접 상속 ABI 변경은 전체 명시 후보가 없으면 여전히 거절하며 부모·원문·초안을 보존한다')
    x.rpc('implementationSources', False, id=owner, function=f.n + 'InheritedFunction',
          revision=s['revision'], hash=s['textHash'])
    assert checkpoint.read_bytes() == original_checkpoint
    f.checked('직접 소유하지 않은 상속 함수는 새 copy 진입의 대상으로 승격되지 않는다')
    request = x.n.request(signature, {'amount': 'amount', 'count': 'count'})
    request['units'][x.child]['draft'] = request['units'][x.child]['draft'].replace(
        x.child, f.n + 'WrongIdentity', 1)
    result = subprocess.run([
        f.env['CONFECTORY_DOTNET'],
        str(f.repo / 'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],
        input=json.dumps({'operation': 'informationFunctionInputUses', **request,
                          'function': fn}), text=True, capture_output=True, check=True)
    error = json.loads(result.stdout)
    assert not error['ok'] and 'Owned implementation identity required' in error['message']
    f.checked('읽기 선택기에서도 상속 선언의 위조된 ID/locator는 건너뛰지 않고 거절한다')
finally:
    f.stop()
    print(json.dumps({'checks': f.checks, 'evidence': str(f.case),
                      'actualEngine': True, 'actualWindows': False}, ensure_ascii=False))
