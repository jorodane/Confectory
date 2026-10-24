"""Actual own-function order fixture; no user projects, accounts or execution."""
import copy
import json
import sys
import v536_field_definitions_ui as d

f, owner = d.f, d.owner
mode = sys.argv[3] if len(sys.argv) > 3 else 'normal'
functions = [owner + '_Function_' + digit * 32 for digit in ['a', 'b', 'c']]
locked = [f.n + 'LockedOne', f.n + 'LockedTwo']
original_order = [functions[0], locked[0], functions[1], locked[1], functions[2]]
desired = [functions[2], functions[0], locked[0], functions[1], locked[1]]
manifest_id = f.n + 'ProjectManifest'
info = f.project / 'FreeInfo.celem'
inherited = f.n + 'InheritedFunction'
for local, kind, source in [
    ('FunctionParent', 'schema', 'schema ' + f.n + 'FunctionParent {contain function ' + inherited + ';}'),
    ('InheritedFunction', 'function', 'function ' + inherited + ' () -> void {provide ' + inherited + ' with ' + inherited + 'Body;}'),
    ('InheritedFunctionBody', 'implementation', 'implementation ' + inherited + 'Body for ' + inherited + ' () -> void {body common "InheritedFunction.csbody";}'),
]:
    (f.project / (local + '.celem')).write_text(source)
    f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet', 'element ' + local + ' ' + kind + ' "' + local + '.celem";registry Confectory.Build.DotNet', 1))
(f.project / 'InheritedFunction.csbody').write_text('return; // 부모 원문 보존')
info.write_text(info.read_text().replace('FreeInfo {', 'FreeInfo extends ' + f.n + 'FunctionParent {', 1))
info.write_text(info.read_text().replace('{', '{\n// 정보 원문 · 9223372036854775806\n' + ''.join('contain function ' + id + ';\n' for id in original_order), 1))
for i, id in enumerate(functions + locked):
    local = id.split('::')[1]
    path = ('elements/' if id in functions else '') + local + '.celem'
    file = f.project / path
    file.parent.mkdir(exist_ok=True)
    file.write_text('function ' + id + ' (long amount,ref long count) -> long {description "보존할 핀과 원문";value editorName="' + ['첫째', '둘째', '셋째', '읽기 전용 1', '읽기 전용 2'][i] + '";provide ' + id + ' with ' + id + 'Body;}')
    (f.project / (local + 'Body.celem')).write_text('implementation ' + id + 'Body for ' + id + ' (long amount,ref long count) -> long {body common "' + local + '.csbody";}')
    (f.project / (local + '.csbody')).write_text('count=checked(count+1);return amount; // 한글 본문 그대로')
    f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet', 'element ' + local + ' function "' + path + '";element ' + local + 'Body implementation "' + local + 'Body.celem";registry Confectory.Build.DotNet', 1))
f.original = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*') if p.is_file()}


def schema():
    f.invoke('schema', {'id': owner})
    return f.state()['schema']


def order(s=None):
    return [row['id'] for row in (s or schema())['ownFunctions'] if row['origin'] == owner]


def preserve():
    assert all((f.project / p).read_bytes() == b for p, b in f.original.items() if p != 'FreeInfo.celem')
    assert '9223372036854775806' in f.state()['draft']['text']
    assert {row['id']: row['hash'] for row in schema()['ownFunctions']} == source_hashes


def prepare(ids, extra=None):
    s = schema()
    reply = f.invoke('blueprint', {'action': 'readOwnerEdits', 'id': owner, 'hash': s['textHash']})['result']['result']
    return {'action': 'applySlots', 'id': owner, 'rows': [], 'basis': reply['basis'], 'declaration': {'id': owner, 'hash': s['textHash'], 'changes': [{'type': 'function-order', 'ids': ids}, *(extra or [])]}}


def apply(request, ok=True):
    return f.invoke('blueprint', request, ok)['result'].get('result')


def restart(i):
    f.stop()
    f.start(i)
    f.invoke('select', {'id': owner})
    return schema()


def confirm():
    ids = f.state()['draft']['creationReviewIds'] or [owner, manifest_id]
    f.invoke('reviewGroup', {'ids': ids, 'target': 'portable'})
    r = f.state()['review']
    assert r['status'] == 'ready', r
    f.invoke('confirmGroup', {'ids': ids, 'token': r['token']})


def setup():
    global checkpoint, source_hashes
    f.start(0)
    f.invoke('select', {'id': owner})
    s = schema()
    assert order(s) == original_order
    source_hashes = {row['id']: row['hash'] for row in s['ownFunctions']}
    assert all(row['writable'] == (row['id'] in functions) for row in s['ownFunctions'])
    assert next(row for row in s['ownFunctions'] if row['id'] == inherited)['origin'] == f.n + 'FunctionParent'
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))


def run():
    try:
        setup()
        before = checkpoint.read_bytes()
        request = prepare(desired)
        if mode == 'guards':
            for ids in [desired[:-1], desired + [desired[0]], [functions[0], locked[1], functions[1], locked[0], functions[2]], [*desired[:-1], 'Other.Project::Function'], [*desired[:-1], inherited]]:
                apply(prepare(ids), False)
                assert checkpoint.read_bytes() == before and order() == original_order
            f.checked('함수 누락·중복·다른 프로젝트·읽기 전용 상대 순서 변경을 모두 미적용으로 거절한다')
            return
        if mode == 'conflict':
            s = schema()
            f.invoke('editDescription', {'id': owner, 'revision': s['revision'], 'hash': s['textHash'], 'value': '경합 입력 보존'})
            text = f.state()['draft']['text']
            apply(request, False)
            assert checkpoint.read_bytes() == before and f.state()['draft']['text'] == text
            f.checked('순서 후보 뒤 원문 경합은 새 설명·기존 순서·checkpoint를 보존하며 전체 미적용이다')
            return
        if mode == 'storage':
            checkpoint.chmod(0o400)
            try:
                apply(request, False)
                assert checkpoint.read_bytes() == before and order() == original_order
            finally:
                checkpoint.chmod(0o600)
            f.checked('순서 저장 실패는 원문과 checkpoint 전체를 유지한다')
        apply(request)
        assert order() == desired
        preserve()
        held = checkpoint.read_bytes()
        restart(1)
        assert order() == desired and checkpoint.read_bytes() == held
        preserve()
        f.checked('순서만 저장/cold 복원하며 함수 ID·핀·본문·읽기 전용 참조·정확한 기본값은 유지한다')
        confirm()
        assert order() == desired
        preserve()
        restart(2)
        assert order() == desired
        apply(prepare(original_order))
        assert order() == original_order
        confirm()
        restart(3)
        assert order() == original_order
        preserve()
        f.checked('명시적 Review/Confirm과 확정 뒤 같은 창 재편집/cold는 contain 순서만 반영한다')
    except Exception:
        try:
            (f.case / 'function-order-failure.json').write_text(json.dumps({'state': f.state(), 'checks': f.checks}, ensure_ascii=False, indent=2))
        except Exception:
            pass
        raise
    finally:
        print(json.dumps({'checks': f.checks, 'mode': mode, 'evidence': str(f.case), 'actualEngine': True, 'nativeWindows': False}, ensure_ascii=False))
        f.stop()


if __name__ == '__main__':
    run()
