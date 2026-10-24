"""Fresh implementation identity after a recoverable information-body archive.

Actual isolated engine, checkpoint/CAS and explicit compiler Confirm. No account,
inference or user project. Also provides the fixture for the renderer regression.
"""
import json
import sys
import v536_field_definitions_ui as d

f = d.f
owner = d.owner
fn = owner + '_Function_' + 'c' * 32
manifest = f.n + 'ProjectManifest'
mode = sys.argv[3] if len(sys.argv) > 3 else 'pending'


def rpc(action, success=True, **args):
    return f.invoke('blueprint', {'action': action, **args}, success)['result'].get('result')


def schema():
    f.invoke('schema', {'id': owner})
    return f.state()['schema']


def create(success=True):
    s = schema()
    method = next(v for v in s['ownFunctions'] if v['id'] == fn)
    basis = rpc('readFeature', id=fn, hash=method['hash'], revision=method['revision'],
                owner=owner, ownerHash=s['textHash'], ownerRevision=s['revision'])
    return rpc('createFeature', success, id=fn, basis=basis['basis'])


def confirm(ids=None):
    schema()
    ids = ids or f.state()['draft']['creationReviewIds']
    f.invoke('reviewGroup', {'ids': ids, 'target': 'portable'})
    review = f.state()['review']
    assert review['status'] == 'ready', review
    assert f.invoke('confirmGroup', {'ids': ids, 'token': review['token']})['result']['result']['sourceConfirmed']


def archive():
    s = schema()
    method = next(v for v in s['ownFunctions'] if v['id'] == fn)
    planned = f.invoke('planBrowserRemoval', {'ids': [fn], 'information': {
        'owner': owner, 'hash': s['textHash'], 'functionHash': method['hash'],
        'mode': 'implementation-only-v1'}})['result']['result']
    token = planned['token']
    result = f.invoke('browserRetirement', {'action': 'apply', 'token': token})['result']['result']
    assert result['retainedFunction'] == fn
    return token


def setup():
    global checkpoint, fnpath, function_original, old_impl, old_graph, initial
    f.start(0)
    f.invoke('select', {'id': owner})
    s = schema()
    basis = rpc('readOwnerEdits', id=owner, hash=s['textHash'])
    rpc('applySlots', id=owner, rows=[], basis=basis['basis'], declaration={
        'id': owner, 'hash': s['textHash'], 'changes': [{
            'type': 'function-add', 'id': fn, 'name': '삭제 뒤 새 구현', 'description': '이전 원문과 새 본문 분리'}]})
    if mode == 'unpublished-body':
        confirm()
    created = create()
    old_impl = created['owner']['implementation']
    old_graph = created['id']
    s = schema()
    body = rpc('read', id=old_graph, owner=owner, ownerHash=s['textHash'], ownerRevision=s['revision'])
    rpc('source', id=old_graph, basis=body['basis'], node='body', text='return; // original archived body 한글')
    f.invoke('saveDraft', {})
    if mode != 'unpublished-body':
        confirm()
    fnpath = f.project / ('elements/' + fn.split('::')[1] + '.celem')
    function_original = fnpath.read_bytes()
    f.original = {str(p.relative_to(f.project)): p.read_bytes() for p in f.project.rglob('*')
                  if p.is_file() and '.confectory' not in p.relative_to(f.project).parts}
    initial = dict(f.original)
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))


def check_old_sources():
    assert fnpath.read_bytes() == function_original
    # Only current owner/manifest can change at explicit Confirm. Old implementation,
    # bodies, unrelated objects, inherited sources and registered packs stay byte-exact.
    assert all((f.project / name).read_bytes() == value for name, value in initial.items()
               if name not in ['FreeInfo.celem', 'project.cproj'])


def restart(i):
    f.stop()
    f.start(i)
    f.invoke('select', {'id': owner})
    schema()


def run():
    assert mode in ['pending', 'confirmed', 'storage', 'conflict', 'unpublished-body'], mode
    try:
        setup()
        token = archive()
        old_archive = next(v for v in json.loads(checkpoint.read_text())['retirements'].values() if v['token'] == token)
        if mode == 'unpublished-body':
            assert old_archive['entries'][old_impl]['baseline'] == 'missing'
            assert not (f.project / old_archive['entries'][old_impl]['path']).exists()
        if mode == 'confirmed':
            confirm([owner, manifest])
            restart(1)
        held = checkpoint.read_bytes()
        if mode == 'storage':
            checkpoint.chmod(0o400)
            try:
                create(False)
                assert checkpoint.read_bytes() == held
                assert not any(v['function'] == fn for v in schema()['providers'])
            finally:
                checkpoint.chmod(0o600)
            f.checked('새 구현 checkpoint 쓰기 거절은 archive·선언·기존 소스·live provider 모두 미적용이다')
        if mode == 'conflict':
            s = schema()
            owner_before = f.state()['draft']['text']
            method = next(v for v in s['ownFunctions'] if v['id'] == fn)
            basis = rpc('readFeature', id=fn, hash=method['hash'], revision=method['revision'],
                        owner=owner, ownerHash=s['textHash'], ownerRevision=s['revision'])
            original = fnpath.read_bytes()
            fnpath.write_bytes(original + b'\n// isolated peer change\n')
            try:
                rpc('createFeature', False, id=fn, basis=basis['basis'])
                assert checkpoint.read_bytes() == held
                # A changed external source legitimately makes the effective
                # projection unavailable. Check the exact live draft instead.
                assert f.state()['draft']['text'] == owner_before
                assert fnpath.read_bytes().endswith(b'// isolated peer change\n')
            finally:
                fnpath.write_bytes(original)
            check_old_sources()
            f.checked('계획 뒤 실제 함수 source 변경은 새 후보 전체를 거절하며 peer 원문과 archive를 보존한다')
            return
        created = create()
        new_impl = created['owner']['implementation']
        assert created['checkpointSaved'] and new_impl != old_impl
        assert created['feature'] == fn and created['id'] == new_impl + '/body:common'
        assert all(new_impl not in v['ids'] for v in f.state()['retirements'])
        receipt = f.state()['retirements'][0]
        assert receipt['token'] == token and new_impl not in receipt['ids']
        assert json.loads(checkpoint.read_text())['retirements'][token]['entries'] == old_archive['entries']
        new_units = {v['id']: v for v in json.loads(checkpoint.read_text())['changes']}
        assert new_units[new_impl]['path'] != 'elements/' + old_impl.split('::')[1] + '.celem'
        assert new_units[new_impl]['baseline'] == 'missing'
        check_old_sources()
        f.checked('삭제 후 새 구현은 독립 ID/경로/본문으로 보관되고 이전 archive·함수 선언·다른 소스는 불변이다')
        saved = checkpoint.read_bytes()
        f.invoke('browserRetirement', {'action': 'recover', 'token': token}, False)
        assert checkpoint.read_bytes() == saved
        assert next(v for v in schema()['providers'] if v['function'] == fn)['implementation'] == new_impl
        f.checked('이전 archive 복구는 새 provider를 덮어쓰지 않고 전체 미적용한다')
        restart(2)
        assert checkpoint.read_bytes() == saved
        assert next(v for v in schema()['providers'] if v['function'] == fn)['implementation'] == new_impl
        # Repeated create has no admission basis while the replacement is attached.
        s = schema()
        method = next(v for v in s['ownFunctions'] if v['id'] == fn)
        rpc('readFeature', False, id=fn, hash=method['hash'], revision=method['revision'],
            owner=owner, ownerHash=s['textHash'], ownerRevision=s['revision'])
        assert checkpoint.read_bytes() == saved
        check_old_sources()
        f.checked('cold 복원과 중복 생성 거절은 새 identity 및 원래 삭제 기록을 유지한다')
        s = schema()
        body = rpc('read', id=created['id'], owner=owner, ownerHash=s['textHash'], ownerRevision=s['revision'])
        rpc('source', id=created['id'], basis=body['basis'], node='body', text='return; // replacement 한글 😀')
        f.invoke('saveDraft', {})
        schema()
        f.invoke('reviewGroup', {'ids': f.state()['draft']['creationReviewIds'], 'target': 'portable'})
        assert f.state()['review']['status'] == 'ready'
        # Review alone is read-only with respect to final sources. Renderer
        # coverage below exercises closing/cancelling the actual review dialog.
        check_old_sources()
        confirm()
        restart(3)
        assert next(v for v in schema()['providers'] if v['function'] == fn)['implementation'] == new_impl
        assert f.state()['retirements'][0]['state'] == 'confirmed'
        check_old_sources()
        assert (f.project / new_units[new_impl]['path']).is_file()
        f.checked('새 본문 편집·검토·명시 Confirm·cold는 새 등록만 반영하고 이전 ' + ('미확정 본문 기록' if mode == 'unpublished-body' else '본문 파일') + '을 보관한다')
    finally:
        print(json.dumps({'checks': f.checks, 'mode': mode, 'evidence': str(f.case),
                          'actualEngine': True, 'nativeWindows': False}, ensure_ascii=False))
        f.stop()


if __name__ == '__main__':
    run()
