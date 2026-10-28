"""Actual UI-authored copy closure lifetime; isolated source/compiler only."""
import copy
import hashlib
import json
import sys
import subprocess
import uuid
import v536_information_binding_api as a

f, owner, manifest = a.f, a.owner, a.manifest
scenario = sys.argv[3] if len(sys.argv) > 3 else 'normal'
binding_setup = a.setup


def setup():
    previous = a.mode
    a.mode = scenario if scenario in ['own', 'registered'] else 'copy-pending' if scenario == 'pending' else 'copy'
    try:
        binding_setup()
        if scenario == 'own':
            # The existing copy selector belongs to required module slots.
            # The original own-function row has no copy/import action. Keep this
            # guard rather than expanding the creation API for a test fixture.
            s = a.schema()
            before = a.checkpoint.read_bytes()
            a.rpc('readImplementationCopy', False, id=owner, function=a.function, source=a.implementation, target='common', implementation=f.n + 'Impl_' + uuid.uuid4().hex, hash=s['textHash'], revision=s['revision'])
            assert a.checkpoint.read_bytes() == before
            f.originals()
            f.checked('모듈 요구가 없는 자체 함수에는 기존 copy 선택 API를 확장하지 않고 원문/선언/입력을 보존하여 거절한다')
        elif scenario == 'registered':
            s = a.schema()
            implementation = f.n + 'Impl_' + uuid.uuid4().hex
            selected = a.rpc('readImplementationCopy', id=owner, function=a.function, source=a.implementation, target='common', implementation=implementation, hash=s['textHash'], revision=s['revision'])
            a.rpc('applySlots', id=owner, rows=[{'function': a.function, 'implementation': implementation, 'copySource': a.implementation, 'copyTarget': 'common', 'fingerprint': selected['fingerprint'], 'basis': selected['basis'], 'edits': []}])
            a.implementation = implementation
            a.confirm()
            a.initial = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
            f.original = dict(a.initial)
    finally:
        a.mode = previous


def closure():
    saved = json.loads(a.checkpoint.read_text())
    rows = saved['retirements']
    assert len(rows) == 1
    receipt = next(iter(rows.values()))
    assert receipt['mode'] == 'information-copy-v1'
    ids = set(receipt['ids'])
    assert a.implementation in ids and len(ids) >= 3
    assert set(receipt['entries']) == ids
    assert all(i == a.implementation or i.startswith(a.implementation + '/body:') for i in ids)
    assert a.function not in ids and owner not in ids
    return receipt


def check(present):
    previous = a.mode
    a.mode = scenario if scenario in ['own', 'registered'] else a.mode
    try:
        a.check(present)
    finally:
        a.mode = previous
    manifest_text = next((f.project / 'project.cproj').read_text() for _ in [0])
    # Disk registration changes only on explicit compiler Confirm.
    assert all((f.project / p).read_bytes() == text for p, text in a.initial.items() if p not in ['FreeInfo.celem', 'project.cproj'])
    return manifest_text


def native_checks():
    description = f.metadata('describe', project=str(f.manifest))
    units = {}
    for row in description['units']:
        text = (f.project / row['path']).read_text()
        units[row['id']] = {**row, 'original': text, 'draft': text, 'baseline': hashlib.sha256(text.encode()).hexdigest(), 'revision': 1}
    request = dict(project=str(f.manifest), namespace='Owned.Elements', scope={'participant': 'fixture', 'context': 'editor'}, units=units, retirements={})
    selection = dict(owner=owner, function=a.function, implementation=a.implementation, mode='information-binding-v1', ownerHash=units[owner]['baseline'], checkpointHash='d' * 64)
    def meta(action, ok=True, **args):
        payload = {'operation': 'informationFunctionRetirement', 'action': action, **request, **args}
        result = subprocess.run([f.env['CONFECTORY_DOTNET'], str(f.repo / 'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')], input=json.dumps(payload), text=True, capture_output=True, check=True, env=f.env)
        value = json.loads(result.stdout)
        assert bool(value['ok']) == ok, value
        return value.get('result')
    p = meta('plan', **selection)
    assert p['mode'] == 'information-copy-v1' and len(p['ids']) >= 3
    applied = meta('apply', evidence=p)
    receipt = applied['retirements'][p['token']]
    meta('validate', units=applied['units'], receipt=receipt)
    restored = meta('recover', units=applied['units'], retirements=applied['retirements'], evidence=receipt)
    assert not restored['retirements'] and all(restored['units'][id]['draft'] == units[id]['draft'] for id in p['ids'])
    f.checked('실제 생성 copy의 Native 후보는 로컬 등록·출처·전체 본문을 증명하고 연결/closure만 원자 보관·복구한다')
    peer = copy.deepcopy(units)
    peer[f.n + 'PeerInfo']['draft'] = peer[f.n + 'PeerInfo']['draft'].replace('with ' + f.n + 'AliasBody', 'with ' + a.implementation)
    shared = meta('plan', units=peer, **selection)
    assert shared['mode'] == 'information-binding-v1' and not shared['ids']
    alias = copy.deepcopy(units)
    alias[f.n + 'AliasBody']['draft'] = alias[f.n + 'AliasBody']['draft'].replace('extends ' + f.n + 'SlotBody', 'extends ' + a.implementation)
    shared = meta('plan', units=alias, **selection)
    assert shared['mode'] == 'information-binding-v1' and not shared['ids']
    f.checked('다른 정보의 provide나 상속 구현에서 사용하는 copy는 closure를 보관하지 않고 기존 연결 수명만 선택한다')
    for field in ['ownerAfter', 'afterManifest', 'implementation', 'mode']:
        forged = copy.deepcopy(receipt)
        forged[field] = 'unknown' if field in ['implementation', 'mode'] else forged[field] + '\n// forged'
        meta('validate', False, units=applied['units'], receipt=forged)
    forged = copy.deepcopy(receipt)
    body = next(id for id in forged['ids'] if '/body:' in id)
    forged['entries'][body]['draft'] += ' '
    meta('validate', False, units=applied['units'], receipt=forged)
    forged = copy.deepcopy(receipt)
    del forged['bindingProof']['binding']['retained'][body]
    meta('validate', False, units=applied['units'], receipt=forged)
    bad = copy.deepcopy(units)
    graph_id = next(id for id in p['ids'] if bad[id]['kind'] == 'blueprint')
    graph = json.loads(bad[graph_id]['draft'])
    graph['copySource']['implementation'] = a.implementation
    bad[graph_id]['draft'] = json.dumps(graph)
    meta('plan', False, units=bad, **selection)
    f.checked('위조된 수명·대상·등록·본문·자기 출처는 채택하지 않으며 기존 파일/입력은 그대로다')
    late = copy.deepcopy(units)
    late[owner]['draft'] += '\n// late input'
    meta('apply', False, units=late, evidence=p)
    changed = copy.deepcopy(applied['units'])
    changed[a.function]['draft'] = changed[a.function]['draft'].replace('long amount', 'double amount')
    meta('validate', units=changed, receipt=receipt)
    meta('recover', False, units=changed, retirements=applied['retirements'], evidence=receipt)
    assert changed[a.function]['draft'].find('double amount') >= 0
    f.originals()
    f.checked('계획 뒤 새 입력은 전체 미적용이며 오래된 archive는 읽되 바뀐 함수 계약을 복구로 덮어쓰지 않는다')


def run():
    try:
        setup()
        if scenario == 'own':
            return
        if scenario == 'native':
            native_checks()
            return
        # Cold first proves ownership comes from registration/body provenance,
        # rather than only transient creationOwner/copySource cache metadata.
        if scenario != 'pending':
            a.restart(1)
        before = a.checkpoint.read_bytes()
        p = a.plan()
        assert p['mode'] == 'information-copy-v1' and len(p['ids']) >= 3 and a.checkpoint.read_bytes() == before
        if scenario == 'guards':
            f.invoke('select', {'id': f.id})
            f.invoke('openEditorView', {'view': '1', 'id': owner, 'viewMode': 'properties'})
            row = next(v for v in f.state()['editorViews'] if v['view'] == '1')
            surface = {'view': '1', 'id': owner, 'viewBinding': row['authorBinding']}
            selection = {'ids': [a.function], 'information': {'owner': owner, 'hash': row['schema']['textHash'], 'mode': 'information-binding-v1', 'implementation': a.implementation}, **surface}
            for wrong in [{k: v for k, v in selection.items() if k != 'viewBinding'}, {**selection, 'viewBinding': '0' * 32}, {**selection, 'id': f.n + 'PeerInfo'}, {**selection, 'information': {**selection['information'], 'implementation': f.n + 'SlotBody'}}, {**selection, 'information': {**selection['information'], 'mode': 'unknown'}}]:
                f.invoke('planBrowserRemoval', wrong, False)
                assert a.checkpoint.read_bytes() == before
            p = a.plan(surface=surface)
            assert p['mode'] == 'information-copy-v1'
            a.action('apply', p['token'], surface=surface)
            held = a.checkpoint.read_bytes()
            f.invoke('closeEditorView', {'view': '1', 'id': owner})
            f.invoke('openEditorView', {'view': '1', 'id': owner, 'viewMode': 'properties'})
            a.action('recover', p['token'], False, surface)
            assert a.checkpoint.read_bytes() == held
            row = next(v for v in f.state()['editorViews'] if v['view'] == '1')
            surface['viewBinding'] = row['authorBinding']
            a.action('recover', p['token'], surface=surface)
            assert f.state()['draft']['id'] == f.id
            f.originals()
            f.checked('copy archive도 실제 bound 정보/프로젝트/nonce만 허용하며 위조·닫힌 창을 거절하고 primary 입력을 보존한다')
            return
        if scenario == 'conflict':
            s = a.schema()
            f.invoke('editDescription', {'id': owner, 'revision': s['revision'], 'hash': s['textHash'], 'value': '다른 입력 보존'})
            text = f.state()['draft']['text']
            a.action('apply', p['token'], False)
            assert a.checkpoint.read_bytes() == before and f.state()['draft']['text'] == text
            f.checked('copy 계획 뒤 live 경합은 등록·본문·연결·checkpoint 전체 미적용과 새 입력 보존이다')
            return
        if scenario == 'storage':
            a.checkpoint.chmod(0o400)
            try:
                a.action('apply', p['token'], False)
                assert a.checkpoint.read_bytes() == before
                check(True)
            finally:
                a.checkpoint.chmod(0o600)
            assert f.invoke('browserArchiveOutcome', {'action': 'apply', 'token': p['token']})['result']['result']['unapplied']
            f.checked('copy 쓰기 실패는 전체 미적용이며 readonly 확인 뒤 같은 후보로 명시적 재시도한다')
        result = a.action('apply', p['token'])
        assert result['mode'] == 'information-copy-v1' and set(result['ids']) == set(p['ids'])
        receipt = closure()
        assert a.implementation not in f.state()['draft']['creationReviewIds']
        check(False)
        saved = a.checkpoint.read_bytes()
        a.restart(2)
        assert a.checkpoint.read_bytes() == saved
        closure()
        assert f.invoke('browserArchiveOutcome', {'action': 'apply', 'token': p['token']})['result']['result']['settled']
        a.action('recover', p['token'])
        check(True)
        assert not f.state()['retirements']
        f.checked('실제 생성·cold copy의 등록과 모든 본문만 보관하며 pending 복구·cold·결과 조회에서 원본/부모/참조·exact64를 보존한다')
        p = a.plan()
        a.action('apply', p['token'])
        a.confirm()
        check(False)
        assert ('element ' + a.implementation.split('::')[1] + ' implementation') not in (f.project / 'project.cproj').read_text()
        a.restart(3)
        check(False)
        assert f.state()['retirements'][0]['state'] == 'confirmed'
        a.action('recover', p['token'])
        check(True)
        a.action('cancel', p['token'])
        check(False)
        a.restart(4)
        a.action('recover', p['token'])
        check(True)
        a.confirm()
        assert not f.state()['retirements'] and ('element ' + a.implementation.split('::')[1] + ' implementation') in (f.project / 'project.cproj').read_text()
        a.restart(5)
        check(True)
        f.checked('copy 확정은 등록만 해제하고 파일을 보관하며 확정 복구·복구 취소·재복구·Confirm·cold에서 선언/핀/원문을 보존한다')
    except Exception:
        try:
            (f.case / 'copy-retirement-failure.json').write_text(json.dumps({'state': f.state(), 'checks': f.checks}, ensure_ascii=False, indent=2))
        except Exception:
            pass
        raise
    finally:
        print(json.dumps({'checks': f.checks, 'scenario': scenario, 'evidence': str(f.case), 'actualEngine': True, 'nativeWindows': False}, ensure_ascii=False))
        f.stop()


if __name__ == '__main__':
    run()
