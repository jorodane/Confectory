"""Saved information binding archive through actual isolated checkpoint/Confirm gates.

Also prepares the real renderer fixture; no real projects, accounts or inference.
"""
import json
import sys
import uuid
import v536_field_definitions_ui as d

f, owner = d.f, d.owner
mode = sys.argv[3] if len(sys.argv) > 3 else 'normal'
function, implementation = f.n + 'Slot', f.n + 'AliasBody'
label = 'Slot'
manifest = f.n + 'ProjectManifest'
info = f.project / 'FreeInfo.celem'
info.write_text(info.read_text().replace('FreeInfo {', 'FreeInfo extends ' + f.n + 'Leaf {provide ' + function + ' with ' + implementation + ';', 1))
parent = f.project / 'Leaf.celem'
parent.write_text(parent.read_text().replace('{', '{module ' + f.n + 'Rules;provide ' + function + ' with ' + f.n + 'SlotBody;', 1))
peer = f.project / 'PeerInfo.celem'
peer.write_text('schema ' + f.n + 'PeerInfo {module ' + f.n + 'Rules;provide ' + function + ' with ' + implementation + ';}')
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet', 'element PeerInfo schema "PeerInfo.celem";registry Confectory.Build.DotNet', 1))
foreign_original = {}
if mode == 'own':
    function, implementation = owner + '_Function_' + 'a' * 32, f.n + 'OwnSharedBody'
    label = '공유 자체 기능'
    local = function.split('::')[1]
    path = f.project / 'elements' / (local + '.celem')
    path.parent.mkdir(exist_ok=True)
    path.write_text('function ' + function + ' (long amount,out long count,out bool ready) -> long {value editorName="' + label + '";}')
    (f.project / 'OwnSharedBody.celem').write_text('implementation ' + implementation + ' for ' + function + ' (long amount,out long count,out bool ready) -> long {body common "OwnShared.csbody";}')
    (f.project / 'OwnShared.csbody').write_text('count=amount+1;ready=true;return amount+2;')
    info.write_text(info.read_text().replace('{', '{contain function ' + function + ';provide ' + function + ' with ' + implementation + ';', 1))
    peer.write_text(peer.read_text().replace('{', '{provide ' + function + ' with ' + implementation + ';', 1))
    f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet', 'element ' + local + ' function "elements/' + local + '.celem";element OwnSharedBody implementation "OwnSharedBody.celem";registry Confectory.Build.DotNet', 1))
if mode == 'registered':
    foreign = f.project / 'registered binding'
    foreign.mkdir()
    function, implementation = 'Source.Binding::Slot', 'Source.Binding::Body'
    (foreign / 'pack.cpack').write_text('pack Source.Binding version "1" {element Slot function "Slot.celem";element Body implementation "Body.celem";element Rules module "Rules.celem";}')
    (foreign / 'Slot.celem').write_text('function ' + function + ' (long amount,out long count,out bool ready) -> long {}')
    (foreign / 'Body.celem').write_text('implementation ' + implementation + ' for ' + function + ' (long amount,out long count,out bool ready) -> long {body common "body.csbody";}')
    (foreign / 'Rules.celem').write_text('module Source.Binding::Rules {require ' + function + ' (long,out long,out bool) -> long;}')
    (foreign / 'body.csbody').write_text('count=amount;ready=true;return amount+1;')
    info.write_text(info.read_text().replace('{', '{module Source.Binding::Rules;provide ' + function + ' with ' + implementation + ';', 1))
    f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet', 'registry Source.Binding "registered binding/pack.cpack";dependency Source.Binding version "1";registry Confectory.Build.DotNet', 1))
    foreign_original = {p: p.read_bytes() for p in foreign.iterdir()}
f.original = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file()}


def rpc(action, ok=True, **args):
    return f.invoke('blueprint', {'action': action, **args}, ok)['result'].get('result')


def schema():
    f.invoke('schema', {'id': owner})
    return f.state()['schema']


def plan(ok=True, surface=None):
    if surface is not None:
        f.invoke('openEditorView', {'view': surface['view'], 'id': owner, 'viewMode': 'properties'})
    s = schema() if surface is None else next(v['schema'] for v in f.state()['editorViews'] if v['view'] == surface['view'])
    selection = {'owner': owner, 'hash': s['textHash'], 'mode': 'information-binding-v1', 'implementation': implementation}
    if mode == 'own':
        method = next(row for row in s['ownFunctions'] if row['id'] == function)
        selection = {'owner': owner, 'hash': s['textHash'], 'mode': 'implementation-only-v1', 'functionHash': method['hash']}
    return f.invoke('planBrowserRemoval', {'ids': [function], 'information': selection, **(surface or {})}, ok)['result'].get('result')


def action(name, token, ok=True, surface=None):
    return f.invoke('browserRetirement', {'action': name, 'token': token, **(surface or {})}, ok)['result'].get('result')


def confirm():
    f.invoke('select', {'id': owner})
    schema()
    ids = f.state()['draft']['creationReviewIds'] or [owner, manifest]
    f.invoke('reviewGroup', {'ids': ids, 'target': 'portable'})
    r = f.state()['review']
    assert r['status'] == 'ready', r
    assert f.invoke('confirmGroup', {'ids': ids, 'token': r['token']})['result']['result']['sourceConfirmed']


def setup():
    global checkpoint, initial, implementation
    f.start(0)
    f.invoke('select', {'id': owner})
    f.invoke('saveDraft', {})
    if mode in ['copy', 'copy-pending']:
        s = schema()
        new_impl = f.n + 'Impl_' + uuid.uuid4().hex
        copy = rpc('readImplementationCopy', id=owner, function=function, source=implementation, target='common', implementation=new_impl, hash=s['textHash'], revision=s['revision'])
        rpc('applySlots', id=owner, rows=[{'function': function, 'implementation': new_impl, 'copySource': implementation, 'copyTarget': 'common', 'fingerprint': copy['fingerprint'], 'basis': copy['basis'], 'edits': []}])
        implementation = new_impl
        if mode == 'copy':
            confirm()
    schema()
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    f.original = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
    initial = dict(f.original)


def retained_sources():
    assert all((f.project / path).read_bytes() == data for path, data in initial.items() if path not in ['FreeInfo.celem', 'project.cproj'])
    assert all(p.read_bytes() == data for p, data in foreign_original.items())
    assert '9223372036854775806' in f.state()['draft']['text']


def check(present):
    s = schema()
    local = next((v for v in s['providers'] if v['function'] == function and v['origin'] == owner), None)
    assert bool(local) == present
    if present:
        assert local['implementation'] == implementation
    elif mode not in ['registered', 'own']:
        fallback = next(v for v in s['providers'] if v['function'] == function)
        assert fallback['origin'] == f.n + 'Leaf' and fallback['implementation'] == f.n + 'SlotBody'
    retained_sources()


def restart(i):
    f.stop()
    f.start(i)
    f.invoke('select', {'id': owner})
    schema()


def run():
    try:
        setup()
        before = checkpoint.read_bytes()
        p = plan()
        token = p['token']
        assert p['mode'] == 'information-binding-v1' and not p['ids'] and checkpoint.read_bytes() == before
        if mode == 'guards':
            f.invoke('select', {'id': f.id})
            f.invoke('openEditorView', {'view': '1', 'id': owner, 'viewMode': 'properties'})
            row = next(v for v in f.state()['editorViews'] if v['view'] == '1')
            surface = {'view': '1', 'id': owner, 'viewBinding': row['authorBinding']}
            s = row['schema']
            request = {'ids': [function], 'information': {'owner': owner, 'hash': s['textHash'], 'mode': 'information-binding-v1', 'implementation': implementation}, **surface}
            for wrong in [{k: v for k, v in request.items() if k != 'viewBinding'}, {**request, 'viewBinding': '0' * 32}, {**request, 'id': f.n + 'PeerInfo'}, {**request, 'information': {**request['information'], 'implementation': f.n + 'WrongBody'}}, {**request, 'information': {**request['information'], 'mode': 'unknown'}}]:
                f.invoke('planBrowserRemoval', wrong, False)
                assert checkpoint.read_bytes() == before
            p = plan(surface=surface)
            action('apply', p['token'], surface=surface)
            saved = checkpoint.read_bytes()
            f.invoke('closeEditorView', {'view': '1', 'id': owner})
            f.invoke('openEditorView', {'view': '1', 'id': owner, 'viewMode': 'properties'})
            action('recover', p['token'], False, surface)
            assert checkpoint.read_bytes() == saved
            row = next(v for v in f.state()['editorViews'] if v['view'] == '1')
            surface['viewBinding'] = row['authorBinding']
            action('recover', p['token'], surface=surface)
            assert f.state()['draft']['id'] == f.id
            f.originals()
            f.checked('독립 연결 archive는 실제 정보/프로젝트/창 nonce와 로컬 provider만 허용하며 위조·닫힌 창·primary 침범을 거절한다')
            return
        if mode == 'conflict':
            s = schema()
            f.invoke('editDescription', {'id': owner, 'revision': s['revision'], 'hash': s['textHash'], 'value': 'peer input stays'})
            peer_text = f.state()['draft']['text']
            action('apply', token, False)
            assert checkpoint.read_bytes() == before and f.state()['draft']['text'] == peer_text
            f.originals()
            f.checked('계획 뒤 live 정보 경합은 연결·구현·checkpoint 전체 미적용과 peer 입력 보존이다')
            return
        if mode == 'storage':
            checkpoint.chmod(0o400)
            try:
                action('apply', token, False)
                assert checkpoint.read_bytes() == before
                check(True)
            finally:
                checkpoint.chmod(0o600)
            assert f.invoke('browserArchiveOutcome', {'action': 'apply', 'token': token})['result']['result']['unapplied']
            f.checked('실제 저장 거절은 연결만 부분 해제하지 않으며 readonly 미적용 조회 뒤 같은 후보로 재시도한다')
        result = action('apply', token)
        assert result['mode'] == 'information-binding-v1' and not result['ids']
        check(False)
        saved = checkpoint.read_bytes()
        restart(1)
        check(False)
        assert checkpoint.read_bytes() == saved
        assert f.invoke('browserArchiveOutcome', {'action': 'apply', 'token': token})['result']['result']['settled']
        action('recover', token)
        check(True)
        assert not f.state()['retirements']
        f.originals()
        f.checked('실제 원자 연결 해제·상위 fallback·cold·완료 조회·pending 복구는 공유/부모/copy와 등록·다른 사용처를 보존한다')
        token = plan()['token']
        action('apply', token)
        if mode == 'copy-pending':
            pending = checkpoint.read_bytes()
            f.invoke('reviewGroup', {'ids': [owner, manifest], 'target': 'portable'}, False)
            assert checkpoint.read_bytes() == pending
            check(False)
            f.checked('미확정 copy를 빼고 연결만 Review하는 요청은 거절하며 원문·전체 creation 그룹과 checkpoint를 보존한다')
        confirm()
        retained_sources()
        f.original = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
        restart(2)
        check(False)
        assert f.state()['retirements'][0]['state'] == 'confirmed'
        action('recover', token)
        check(True)
        action('cancel', token)
        check(False)
        restart(3)
        action('recover', token)
        check(True)
        confirm()
        assert not f.state()['retirements']
        retained_sources()
        restart(4)
        check(True)
        f.checked('실제 Review/Confirm은 정보 연결만 반영하고 확정 복구·복구 취소 후 재복구·cold를 별도 명시적 확정으로 완주한다')
    except Exception:
        try:
            (f.case / 'binding-api-failure.json').write_text(json.dumps({'state': f.state(), 'checks': f.checks}, ensure_ascii=False, indent=2))
        except Exception:
            pass
        raise
    finally:
        print(json.dumps({'checks': f.checks, 'mode': mode, 'evidence': str(f.case), 'actualEngine': True, 'renderer': False, 'nativeWindows': False}, ensure_ascii=False))
        f.stop()


if __name__ == '__main__':
    run()
