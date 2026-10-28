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
    pending_copy = __import__('os').environ.get('CONFECTORY_PENDING_COPY') == '1'
    if not pending_copy:
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
    if preview.get('functionDependencies'):
        declaration['changes'][0]['mapping']['dependencies'] = preview['functionDependencies']
    if pending_copy:
        proof = preview['functionCopies'][x.copy_id + '/body:common']
        assert proof['pending'] == {'functionSignature': signature,
                                    'implementationSignature': body['signature']}
        unchanged_checkpoint = checkpoint.read_bytes()
        faults = ['missing-proof', 'changed-proof', 'changed-contract', 'invalid-body']
        if x.imported_copy: faults += ['missing-dependencies', 'invalid-alias']
        for fault in faults:
            bad = copy.deepcopy(declaration)
            change = bad['changes'][0]
            if fault == 'missing-proof': change['mapping'].pop('copies')
            elif fault == 'changed-proof': change['mapping']['copies'][x.copy_id + '/body:common']['pending']['functionSignature']['return'] = 'double'
            elif fault == 'changed-contract':
                change['signature'] = copy.deepcopy(signature)
                change['signature']['args'][0]['name'] = 'renamed'
                change['mapping']['args']['amount'] = 'renamed'
                change['mapping']['bodies'][body_id]['contract'] = change['signature']
            elif fault == 'missing-dependencies': change['mapping'].pop('dependencies')
            elif fault == 'invalid-alias': change['mapping']['bodies'][body_id]['text'] = source.replace('calls.ForeignEcho', 'calls.MissingAlias')
            else: change['mapping']['bodies'][body_id]['text'] = 'not C#'
            x.rpc('applySlots', False, id=owner, rows=[], basis=preview['basis'], declaration=bad)
            assert checkpoint.read_bytes() == unchanged_checkpoint
            x.original_sources()
        f.checked('미확정 receipt 누락/변조·계약 변경·잘못된 본문은 기존 생성/배정까지 전체 미적용으로 보존한다')
        parent_file = f.project / x.parent_path
        original_parent = parent_file.read_bytes()
        try:
            parent_file.write_bytes(original_parent + b'\n// real peer source change\n')
            x.rpc('applySlots', False, id=owner, rows=[], basis=preview['basis'], declaration=declaration)
            assert checkpoint.read_bytes() == unchanged_checkpoint
        finally:
            parent_file.write_bytes(original_parent)
        x.original_sources()
        f.checked('미확정 copy의 실제 부모 원문 경합도 원자 거절하고 원래 생성 기록을 보존한다')
        if x.imported_copy:
            if 'blueprint-parent' in __import__('sys').argv[4:]:
                # Root metadata requests cannot inject the internal observed
                # function map, even when they claim the current declaration.
                import subprocess
                original_units = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
                original_graph = json.loads(original_units[x.copy_id + '/body:common']['draft'])
                original_graph.pop('copySource')
                original_body = json.loads(original_units[body_id]['draft'])['source']
                root_request = {'operation': 'blueprintRootContract',
                    'functionText': x.b.function_file.read_text(),
                    'text': original_units[x.copy_id]['draft'], 'bodyTarget': 'common',
                    'graph': original_graph, 'plan': {'args': signature['args'],
                    'returnType': signature['return'], 'remap': {'amount': 'amount', 'count': 'count'},
                    'rootBody': {'node': 'body', 'source': original_body}}}
                for field in [None, 'featureContracts', 'stableImports']:
                    direct = copy.deepcopy(root_request)
                    if field: direct[field] = {x.foreign: (f.project / 'registered/Echo.celem').read_text()}
                    process = subprocess.run([f.env['CONFECTORY_DOTNET'],
                        str(f.repo / 'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],
                        input=json.dumps(direct), text=True, capture_output=True, check=True, env=f.env)
                    refused = json.loads(process.stdout)
                    assert not refused['ok'] and 'complete unchanged source contracts' in refused['message'], refused
                assert checkpoint.read_bytes() == unchanged_checkpoint
            foreign_file = f.project / 'registered/Echo.celem'
            original_foreign = foreign_file.read_bytes()
            try:
                foreign_file.write_bytes(original_foreign.replace(b'long foreignInput', b'double foreignInput'))
                x.rpc('applySlots', False, id=owner, rows=[], basis=preview['basis'], declaration=declaration)
                assert checkpoint.read_bytes() == unchanged_checkpoint
            finally:
                foreign_file.write_bytes(original_foreign)
            x.original_sources()
            f.checked('외부 import receipt 누락·잘못된 별칭·실제 외부 계약 변경은 전체 거절하며 외부 원본과 기존 copy를 보존한다')
    result = x.rpc('applySlots', id=owner, rows=[], basis=preview['basis'], declaration=declaration)
    assert result['atomic'] and result['checkpointSaved']
    rows = {r['id']: r for r in json.loads(checkpoint.read_text())['changes']}
    assert json.loads(rows[body_id]['draft'])['source'] == source
    assert x.parent not in rows and x.child not in rows
    x.imported_copy_contract(rows, x.copy_id)
    x.original_sources()
    f.checked('복사 후 본문 재편집은 미사용 상속 선언을 바꾸지 않고 같은 ABI/전체 후보 검증으로 보관한다')
    if pending_copy or x.imported_copy:
        group = rows[owner]['atomicEditGroup']
        assert {r for r in rows if r.startswith(x.copy_id)} <= set(group)
        assert all(rows[id]['atomicEditGroup'] == group for id in group)
        f.invoke('reviewGroup', {'ids': group, 'target': 'portable'})
        review = f.state()['review']
        assert review['status'] == 'ready', review
        f.invoke('confirmGroup', {'ids': group, 'token': review['token']})
        x.original_sources()
        assert x.copy_id in x.b.info.read_text()
        f.checked('미확정 생성 header·모든 record·배정·본문의 완전한 한 Review/Confirm은 compiler를 통과하고 부모를 보존한다' if pending_copy else '확정 copy 재편집도 기존 header/import를 보존하여 다시 Review/Confirm한다')
finally:
    f.stop()
    print(json.dumps({'checks': f.checks, 'actualEngine': True,
                      'evidence': str(f.case), 'projectRun': False,
                      'actualWindows': False}, ensure_ascii=False))
