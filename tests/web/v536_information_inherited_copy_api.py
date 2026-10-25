"""Contained information function uses the existing atomic private-copy path."""
import copy
import json
import v536_information_inherited_copy_fixture as x

f, owner, fn = x.f, x.owner, x.fn
try:
    f.start(0)
    f.invoke('select', {'id': owner})
    f.invoke('saveDraft', {})
    s = x.schema()
    assert next(p for p in s['providers'] if p['function'] == fn)['contract']['parent'] == x.parent
    assert not any(r['function'] == fn for r in s['requirements']), 'do not invent a module card'
    catalog = x.rpc('implementationSources', id=owner, function=fn,
                    revision=s['revision'], hash=s['textHash'])
    assert catalog['rows'][0]['id'] == x.child
    assert catalog['rows'][0]['bodyOrigin'] == x.parent
    prepared = x.prepare()
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    held = checkpoint.read_bytes()
    seed = json.loads(held)['privateCopies'][x.copy_id]['snapshot']
    assert seed['bodyOrigin'] == x.parent
    assert seed['records'][0]['record']['source'] == x.original
    observed = {r['path'] for r in seed['observations']}
    assert {str(f.project / x.parent_path), str(x.b.implementation_file),
            *(str(f.project / p) for p in x.body_observations)}.issubset(observed)
    assert all((f.project / p).read_bytes() == v for p, v in x.snapshot.items())
    f.checked('자체 정보 함수의 기존 선택/비공개 초안 경로는 부모 header/body와 원래 snapshot을 보관하며 모듈 UI를 추가하지 않는다')
    row = x.copy_row(prepared)
    bad = copy.deepcopy(row)
    bad['edits'][0]['node'] = 'not-the-selected-node'
    x.rpc('applySlots', False, id=owner, rows=[bad])
    assert checkpoint.read_bytes() == held
    assert not x.rpc('list', feature=fn, query=x.copy_id + '/body:')['rows']
    result = x.rpc('applySlots', id=owner, rows=[row])
    assert result['atomic'] and result['checkpointSaved']
    s = x.schema()
    assert next(p for p in s['providers'] if p['function'] == fn)['implementation'] == x.copy_id
    view = x.rpc('read', id=x.copy_id + '/body:common', owner=owner,
                 ownerRevision=s['revision'], ownerHash=s['textHash'])
    assert view['nodes'][0]['source'] == x.edited
    ids = view['reviewIds']
    assert {owner, x.copy_id, x.copy_id + '/body:common'}.issubset(ids), ids
    x.original_sources()
    f.stop()
    f.start(1)
    f.invoke('select', {'id': owner})
    assert next(p for p in x.schema()['providers'] if p['function'] == fn)['implementation'] == x.copy_id
    x.original_sources()
    f.checked('오류는 전체 미적용이고 명시 재시도/원자 저장/cold는 새 복사본만 연결하며 부모·함수·호출자를 보존한다')
    f.invoke('reviewGroup', {'ids': ids, 'target': 'portable'})
    review = f.state()['review']
    assert review['status'] == 'ready', review
    confirmed = f.invoke('confirmGroup', {'ids': ids, 'token': review['token']})
    assert confirmed['result']['result']['sourceConfirmed'], f.state().get('review')
    f.stop()
    f.start(2)
    f.invoke('select', {'id': owner})
    x.original_sources()
    s = x.schema()
    preview = x.rpc('readOwnerEdits', id=owner, hash=s['textHash'],
                    includeFunctionInputs=fn, includeFunctionBodies=True)
    body_id, body = next((k, v) for k, v in preview['functionBodies'].items()
                         if v.get('copyOwner') == owner and k.startswith(x.copy_id + '/body:'))
    signature = x.b.old
    source = x.edited.replace('소유한 상속 복사본', '저장한 복사본 재편집')
    plan = {k: body[k] for k in ['hash', 'path', 'whole']}
    plan.update(beforeSignature=body['signature'], signature=body['signature'],
                contract=signature, text=source)
    if body['sourceKind'] != 'whole-csharp':
        plan['outputs'] = {'return': 'return', 'nativeTotal': 'nativeTotal'}
    method = next(m for m in s['ownFunctions'] if m['id'] == fn)
    declaration = {'id': owner, 'hash': s['textHash'], 'changes': [{
        'type': 'function-edit', 'id': fn, 'hash': method['hash'],
        'name': method['name'], 'description': method['description'],
        'signature': signature, 'mapping': {'before': signature,
        'args': {'amount': 'amount', 'count': 'count'},
        'copies': preview['functionCopies'], 'bodies': {body_id: plan}}}]}
    result = x.rpc('applySlots', id=owner, rows=[], basis=preview['basis'], declaration=declaration)
    assert result['atomic'] and result['checkpointSaved']
    rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
    assert json.loads(rows[body_id]['draft'])['source'] == source
    assert x.parent not in rows and x.child not in rows
    x.original_sources()
    f.checked('복사 후 본문 재편집은 미사용 상속 선언을 바꾸지 않고 같은 ABI/전체 후보 검증으로 보관한다')
finally:
    f.stop()
    print(json.dumps({'checks': f.checks, 'actualEngine': True,
                      'evidence': str(f.case), 'projectRun': False,
                      'actualWindows': False}, ensure_ascii=False))
