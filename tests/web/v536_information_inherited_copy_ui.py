"""Existing v536 copy picker/editor for an owned inherited information function."""
import json
import time
from playwright.sync_api import sync_playwright, expect
import v536_information_inherited_copy_fixture as x

f, d, owner, fn, mode = x.f, x.d, x.owner, x.fn, x.mode

def choices():
    return [v['copy'] for _, v in f.pending()['blueprint']
            if v.get('kind') == 'copy-selection' and v['copy']['owner'] == owner]

def same_user_inputs(before, require_journal=True):
    after = f.pending()
    # Save keeps a separate retry/receipt journal. Its addition must not be
    # mistaken for changed user text, and it must not be erased by the test.
    def user(value):
        return {**value, 'blueprint': [(k, v) for k, v in value['blueprint']
                                      if v.get('kind') != 'copy-attempt']}
    (f.case / 'inherited-copy-boundary-inputs.json').write_text(json.dumps(
        {'before': before, 'after': after}, ensure_ascii=False, indent=2))
    assert user(before) == user(after)
    journal = [v for _, v in after['blueprint'] if v.get('kind') == 'copy-attempt']
    assert len(journal) == 1 if require_journal else len(journal) <= 1
    if journal:
        assert journal[0]['owner'] == owner
        assert journal[0]['rows'][0]['copy']['implementation'] == choices()[0]['implementation']

def picker():
    f.owner().locator('[data-inline-method="' + fn + '"] [data-function-edit]').click()
    popup = f.page.get_by_role('dialog', name='구현 선택', exact=True)
    expect(popup).to_be_visible()
    expect(popup).to_contain_text('원본·상위 객체의 구현은 유지됩니다')
    expect(popup.locator('[data-copy-source="' + x.child + '"][data-copy-target=common]')).to_have_count(1)
    assert not f.page.locator('[data-code-source]').count(), 'do not edit the parent in place'
    return popup

def edit_source():
    button = f.author().locator('[data-bp-node=body] [data-internal-code]')
    f.author().locator(':scope > .window-title .caption').click(position={'x': 5, 'y': 8})
    f.author().locator('[data-bp-overview-node=body]').click()
    button.click()
    dialog = f.page.locator('.bp-script-dialog')
    value = dialog.locator('[data-code-source]')
    expect(value).to_be_visible()
    assert '원래 별칭' in value.input_value()
    value.evaluate("el=>{el.focus();const i=el.value.indexOf('원래 별칭');el.setSelectionRange(i,i+'원래 별칭'.length);}")
    f.page.keyboard.insert_text('상속 복사 UI 😀')
    f.page.keyboard.press('Control+z')
    assert '원래 별칭' in value.input_value()
    f.page.keyboard.press('Control+y')
    assert '상속 복사 UI 😀' in value.input_value()
    f.page.screenshot(path=str(f.case / 'inherited-copy-script.png'))
    dialog.locator('[data-code-save]').click()
    expect(dialog).to_be_hidden()
    f.close_author()

def restart(i, expect_same=True):
    held = f.pending()
    f.page.unroute_all(behavior='wait')
    f.page.close()
    f.stop()
    f.start(i)
    f.page = f.setup()
    f.page.set_viewport_size({'width': 2300, 'height': 1700})
    if d.is_view:
        f.owner = lambda: f.page.locator('.window[data-key=editor-1]')
    expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo')
    f.idle()
    restored = f.pending()
    (f.case / ('inherited-copy-restart-' + str(i) + '.json')).write_text(
        json.dumps({'before': held, 'after': restored}, ensure_ascii=False, indent=2))
    if expect_same:
        assert restored == held

def reedit_pending(copied, checkpoint):
    """The existing own-function body dialog after Save, before Confirm."""
    key = copied + '/body:common/node:body'
    def pending():
        return [v for _, v in d.pending() if v.get('kind') == 'function-edit']
    def editor():
        f.owner().locator('[data-inline-method="' + fn + '"] [data-function-edit]').click()
        popup = f.page.get_by_role('dialog', name='구현 선택', exact=True)
        expect(popup).to_be_visible()
        expect(popup.locator('[data-information-body="' + key + '"]')).to_contain_text('소유 복사본')
        popup.locator('[data-information-body="' + key + '"]').click()
        dialog = f.page.locator('[role=dialog]:has([data-code-source])')
        expect(dialog).to_be_visible()
        return dialog
    def fill(dialog, value):
        code = dialog.locator('[data-code-source]')
        code.evaluate(r"el=>{el.focus();el.setSelectionRange(el.value.indexOf('\n{\n')+3,el.value.lastIndexOf('\n}'));}")
        # Use the real editor's editable body region; its native header/footer
        # are protected. A whole-text replacement is correctly rejected.
        suffix = value[value.rfind('\n}') + 2:]
        body = value[value.index('\n{\n') + 3:value.rfind('\n}')]
        if suffix: body += suffix
        f.page.keyboard.insert_text(body)
        f.idle()
    def wait(start, ok=True, action='applySlots'):
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            ids = {r['invoke']['requestId'] for r in f.traffic[start:]
                   if r.get('invoke', {}).get('endpoint') == 'blueprint'
                   and r['invoke']['input'].get('action') == action}
            rows = [r['result'] for r in f.traffic[start:]
                    if r.get('result', {}).get('requestId') in ids
                    and r['result'].get('error', {}).get('code') != 'stale_revision']
            if rows:
                assert bool(rows[-1]['ok']) == ok, rows[-1]
                f.idle()
                return
            f.page.wait_for_timeout(20)
        raise AssertionError({'waiting': action, 'evidence': str(f.case)})
    def save(ok=True):
        mark = len(f.traffic)
        f.owner().locator('[data-element-action=save]').click()
        wait(mark, ok)
    before = checkpoint.read_bytes()
    dialog = editor()
    original = dialog.locator('[data-code-source]').input_value()
    assert '상속 복사 UI 😀' in original and not pending()
    edited = original.replace('상속 복사 UI 😀', '미확정 복사 재편집 😀')
    fill(dialog, edited)
    dialog.locator('[data-code-cancel]').click()
    assert not pending() and checkpoint.read_bytes() == before
    dialog = editor()
    fill(dialog, edited + '\n// unfinished local input')
    held = f.pending()
    restart(10)
    assert f.pending() == held
    dialog = editor()
    assert 'unfinished local input' in dialog.locator('[data-code-source]').input_value()
    fill(dialog, edited)
    dialog.locator('[data-code-save]').click()
    mapping = f.page.locator('[role=dialog]:has([data-abi-remap-accept])')
    expect(mapping).to_be_visible()
    mapping.locator('[data-abi-remap-accept]').click()
    f.idle()
    assert len(pending()) == 1
    value = pending()[0]
    assert value['mapping']['copies'][copied + '/body:common']['pending']['functionSignature'] == x.b.old
    f.owner().locator('[data-own-functions-toggle]').press('Control+z')
    f.owner().locator('[data-own-functions-toggle]').press('Control+y')
    assert pending()[0] == value
    held = f.pending()
    restart(11)
    assert f.pending() == held and pending()[0] == value
    preserved()
    f.checked('미확정 복사본 재편집·팝업 취소·불완전 입력 cold·Undo/Redo는 계약/복사 ID/출처/정확한 값과 입력을 보존한다')
    if mode == 'reedit-cancel':
        f.owner().locator('[data-element-action=discard]').click()
        f.idle()
        assert not pending()
        rows = json.loads(checkpoint.read_text())['changes']
        assert any(r['id'] == copied for r in rows)
        assert '미확정 복사 재편집' not in checkpoint.read_text()
        restart(12)
        assert not pending()
        preserved()
        f.checked('재편집 취소는 기존 미확정 생성·배정을 유지하고 추가 입력만 취소한다')
        return False
    if mode == 'reedit-conflict':
        state = f.state()['schema']
        f.invoke('editDescription', {'id': owner, 'hash': state['textHash'],
                                   'revision': state['revision'], 'value': '다른 창의 새 입력'})
        # Persist the peer's independent change. A backend-only unsaved edit
        # is not a durable other-window input and may disappear on restart.
        f.invoke('saveDraft', {})
        peer_checkpoint = checkpoint.read_bytes()
        assert peer_checkpoint != before
        mark = len(f.traffic)
        f.rejected_save()
        failed = {r['result']['requestId'] for r in f.traffic[mark:]
                  if r.get('result', {}).get('ok') is False}
        assert any(r.get('invoke', {}).get('requestId') in failed
                   and r['invoke'].get('input', {}).get('action') == 'readOwnerEdits'
                   for r in f.traffic[mark:])
        assert pending()[0] == value and checkpoint.read_bytes() == peer_checkpoint
        restart(12)
        f.rejected_save()
        assert pending()[0] == value and checkpoint.read_bytes() == peer_checkpoint
        preserved()
        f.checked('다른 창 경합은 cold 뒤에도 원자 거절하며 기존 복사 초안과 새 입력을 보존한다')
        return False
    if mode == 'reedit-projects':
        import shutil
        listing = f.state()['listingId']
        f.page.close(); f.stop()
        other = f.case / 'other root' / 'owned project'
        shutil.copytree(f.project, other, ignore=shutil.ignore_patterns('.confectory'))
        f.env['CONFECTORY_WEB_PROJECT'] = str(other / 'project.cproj')
        f.start(12); f.invoke('select', {'id': owner}); f.invoke('saveDraft', {})
        second = f.state()['listingId']
        other_checkpoint = next(other.glob('.confectory/edit-workspaces/*/draft.json'))
        other_before = other_checkpoint.read_bytes()
        f.page = f.setup(); f.page.set_viewport_size({'width': 2300, 'height': 1700})
        def enter(id):
            f.page.locator('.brand').click()
            expect(f.page.locator('.home-grid')).to_be_visible()
            f.page.locator('[data-enter="' + id + '"]').click()
            expect(f.page.locator('.work-body')).to_be_visible(); f.idle()
        enter(listing)
        assert pending()[0] == value
        dialog = editor()
        dialog.locator('[data-code-save]').evaluate('el=>globalThis.stalePendingCopySave=el')
        dialog.locator('[data-code-cancel]').click()
        enter(second); d.open_info()
        assert not pending()
        f.page.evaluate('()=>stalePendingCopySave.click()')
        assert not pending() and other_checkpoint.read_bytes() == other_before
        assert checkpoint.read_bytes() == before
        enter(listing)
        assert pending()[0] == value
        preserved()
        # The second project was only a startup fixture for discovery. Restore
        # the requested first project before the following cold-start check.
        f.env['CONFECTORY_WEB_PROJECT'] = str(f.manifest)
        f.checked('프로젝트 전환/독립 창의 미확정 copy 입력과 닫힌 저장 동작은 원래 소유 문맥을 보존한다')
    if mode == 'reedit-storage':
        checkpoint.chmod(0o400)
        try:
            save(False)
            assert pending()[0] == value and checkpoint.read_bytes() == before
            preserved()
        finally:
            checkpoint.chmod(0o600)
        f.checked('재편집 저장 실패는 기존 미확정 생성/배정과 입력을 부분 적용 없이 보존한다')
    if mode == 'reedit-loss':
        applies, queries, lost = set(), set(), set()
        def intercept(route):
            request = route.request.post_data_json
            if request.get('op') == 'invoke' and request.get('endpoint') == 'blueprint':
                action = request.get('input', {}).get('action')
                if action == 'applySlots': applies.add(request['requestId'])
                elif applies and action == 'settledSlots': queries.add(request['requestId'])
            response = route.fetch()
            payload = response.json()
            for row in payload.get('results', []):
                if row['requestId'] in applies | queries:
                    rid = row['requestId']; lost.add(rid); row.clear()
                    row.update(requestId=rid, ok=False, error={'code': 'transport_lost'})
            route.fulfill(response=response, json=payload)
        f.page.route('**/api/request', intercept)
        f.owner().locator('[data-element-action=save]').click()
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline and not queries & lost: f.page.wait_for_timeout(20)
        assert len(applies) == 1 and queries & lost and pending()
        mark = len(f.traffic)
        restart(12, expect_same=False)
        if pending():
            f.owner().locator('[data-element-action=save]').click()
            wait(mark, action='settledSlots')
        assert not any(r.get('invoke', {}).get('input', {}).get('action') == 'applySlots' for r in f.traffic[mark:])
        f.checked('재편집 응답 유실/cold는 결과 조회 후 확정하며 같은 복사본을 중복 적용하지 않는다')
    else:
        save()
    deadline = time.monotonic() + 60
    while pending() and time.monotonic() < deadline: f.page.wait_for_timeout(20)
    assert not pending()
    rows = json.loads(checkpoint.read_text())['changes']
    assert len([r for r in rows if r['id'] == copied]) == 1
    record = next(r for r in rows if r['id'] == key)
    assert json.loads(record['draft'])['source'] in edited
    assert '미확정 복사 재편집 😀' in json.loads(record['draft'])['source']
    assert all(r.get('baseline') == 'missing' for r in rows if r['id'].startswith(copied))
    by_id = {r['id']: r for r in rows}
    group = by_id[owner]['atomicEditGroup']
    assert {r['id'] for r in rows if r['id'].startswith(copied)} <= set(group)
    assert all(by_id[id]['atomicEditGroup'] == group for id in group)
    restart(13)
    preserved()
    f.checked('미확정 복사본의 같은 계약 본문 저장은 생성/배정과 한 그룹으로 남고 재시작 후 부모/호출자 원문을 보존한다')
    return True

def saved():
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        if not choices():
            f.idle()
            return
        f.page.wait_for_timeout(30)
    raise AssertionError({'pending': f.pending(), 'evidence': str(f.case)})

def preserved():
    x.original_sources()
    expect(f.owner().get_by_label('Power 기본값', exact=True)).to_have_value('9223372036854775806')
    assert not f.page.locator('#app').evaluate('el=>el.inert')

try:
    f.start(0)
    f.invoke('select', {'id': owner})
    f.invoke('saveDraft', {})
    if d.is_view:
        f.invoke('select', {'id': f.n + 'RefTarget'})
    with sync_playwright() as pw:
        expect.set_options(timeout=60000)
        f.browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 2300, 'height': 1700})
        d.open_info()
        assert abs(f.owner().bounding_box()['width'] - 460) < 1
        if d.is_view:
            # Floating information windows remain above document windows in the
            # original layout. Move it aside using its normal draggable title.
            head = f.owner().locator('.object-title-name').bounding_box()
            box = f.owner().bounding_box()
            f.page.mouse.move(head['x'] + 5, head['y'] + 5)
            f.page.mouse.down()
            f.page.mouse.move(1780 + head['x'] - box['x'] + 5,
                              80 + head['y'] - box['y'] + 5, steps=10)
            f.page.mouse.up()
        popup = picker()
        f.page.screenshot(path=str(f.case / 'inherited-copy-picker.png'))
        f.page.keyboard.press('Escape')
        expect(popup).to_have_count(0)
        assert not choices()
        popup = picker()
        popup.locator('[data-copy-source="' + x.child + '"][data-copy-target=common]').click()
        expect(f.author().locator('[data-bp-node=body]')).to_be_visible()
        edit_source()
        assert len(choices()) == 1
        copied = choices()[0]['implementation']
        held = f.pending()
        checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
        before = checkpoint.read_bytes()
        preserved()
        restart(1)
        assert f.pending() == held and choices()[0]['implementation'] == copied
        preserved()
        f.checked(('독립' if d.is_view else '기본') + ' 정보 창의 기존 상속 복사 선택·취소·C# Undo/Redo·cold는 원본/정확한 값/새 복사 ID를 보존한다')
        if mode == 'storage':
            checkpoint.chmod(0o400)
            try:
                f.rejected_save()
                same_user_inputs(held)
                assert checkpoint.read_bytes() == before
                preserved()
            finally:
                checkpoint.chmod(0o600)
            f.checked('실제 화면 저장 실패는 복사본·owner·등록을 부분 적용하지 않고 입력과 부모를 보존한다')
        elif mode == 'conflict':
            parent = f.project / x.parent_path
            peer = parent.read_bytes() + b'\n// owned peer changed inherited header\n'
            parent.write_bytes(peer)
            x.snapshot[x.parent_path] = peer
            f.original[x.parent_path] = peer
            f.rejected_save()
            same_user_inputs(held, require_journal=False)
            assert checkpoint.read_bytes() == before
            restart(2)
            f.rejected_save()
            same_user_inputs(held, require_journal=False)
            assert checkpoint.read_bytes() == before
            preserved()
            f.checked('실제 부모 header 경합은 cold 뒤에도 원자 거절하며 peer 원문·원래 private snapshot·입력을 덮어쓰지 않는다')
        elif mode == 'cancel':
            f.owner().locator('[data-element-action=discard]').click()
            f.idle()
            assert not choices()
            preserved()
            f.checked('전체 취소는 private 복사 입력만 해제하며 부모/원래 provider와 다른 입력을 보존한다')
        elif mode == 'loss':
            applies, queries, lost = set(), set(), set()
            def intercept(route):
                request = route.request.post_data_json
                if request.get('op') == 'invoke' and request.get('endpoint') == 'blueprint':
                    action = request.get('input', {}).get('action')
                    if action == 'applySlots':
                        applies.add(request['requestId'])
                    elif applies and action == 'settledSlots':
                        queries.add(request['requestId'])
                response = route.fetch()
                payload = response.json()
                for result in payload.get('results', []):
                    if result['requestId'] in applies | queries:
                        rid = result['requestId']
                        lost.add(rid)
                        result.clear()
                        result.update(requestId=rid, ok=False, error={'code': 'transport_lost'})
                route.fulfill(response=response, json=payload)
            f.page.route('**/api/request', intercept)
            f.owner().locator('[data-element-action=save]').click()
            deadline = time.monotonic() + 90
            while time.monotonic() < deadline and not queries & lost:
                f.page.wait_for_timeout(30)
            assert len(applies) == 1 and queries & lost and choices()
            after = len(f.traffic)
            restart(2, expect_same=False)
            if choices():
                f.owner().locator('[data-element-action=save]').click()
                saved()
            query_ids = {r['invoke']['requestId'] for r in f.traffic[after:]
                         if r.get('invoke', {}).get('endpoint') == 'blueprint'
                         and r['invoke'].get('input', {}).get('action') == 'settledSlots'}
            assert any(r.get('result', {}).get('requestId') in query_ids
                       and r['result'].get('ok')
                       and r['result'].get('result', {}).get('settled') is True
                       for r in f.traffic[after:])
            assert not any(r.get('invoke', {}).get('input', {}).get('action') == 'applySlots'
                           for r in f.traffic[after:])
            staged = json.loads(checkpoint.read_text())['changes']
            assert len([r for r in staged if r['id'] == copied]) == 1
            body = next(r for r in staged if r['kind'] == 'blueprint-node'
                        and r['id'].startswith(copied + '/body:common/node:'))
            assert '상속 복사 UI 😀' in json.loads(body['draft'])['source']
            assert '9223372036854775806' in json.loads(body['draft'])['source']
            preserved()
            f.checked('적용/조회 응답 유실과 cold 뒤 재시도는 receipt만 조회하여 같은 복사 ID를 중복 생성하지 않는다')
        if mode not in ['conflict', 'cancel']:
            if choices():
                f.owner().locator('.object-title-name').click(position={'x': 4, 'y': 4})
                f.owner().locator('[data-element-action=save]').click()
                saved()
            preserved()
            restart(3 if mode == 'loss' else 2)
            if __import__('os').environ.get('CONFECTORY_PENDING_COPY') == '1':
                if not reedit_pending(copied, checkpoint):
                    assert not f.errors and not f.external, (f.errors, f.external)
                    f.browser.close()
                    raise SystemExit(0)
            review = d.review()
            review.locator('[data-reject]').click()
            preserved()
            review = d.review()
            if review.locator('[data-review-advanced]').count():
                review.locator('[data-review-advanced]').click()
                if review.locator('[data-advanced-reviewed]').count():
                    review.locator('[data-advanced-reviewed]').check()
            review.locator('#confirm').click()
            expect(review).to_have_count(0, timeout=120000)
            f.idle()
            x.original_sources()
            assert copied in x.b.info.read_text()
            assert (f.project / x.parent_path).read_bytes() == x.snapshot[x.parent_path]
            f.page.screenshot(path=str(f.case / 'inherited-copy-confirmed.png'))
            f.checked('실제 Save·재시작·Review 취소/재검토·명시 Confirm은 새 소유 복사본만 반영하며 함수/부모/호출자를 보존한다')
            if 'serial-extra' in __import__('sys').argv[4:]:
                records = [json.loads(p.read_text()) for p in
                           (f.project / 'blueprints/nodes').glob(copied.split('::')[1] + '.*.node.json')]
                assert len(records) == 2
                assert next(r for r in records if r['node'] == 'extra')['source'] == 'return value + 1; // 원본 추가 동작'
                assert '상속 복사 UI 😀' in next(r for r in records if r['node'] == 'body')['source']
                f.checked('추가 직렬 동작과 반환 writer를 포함한 부모 그래프는 선택한 본문만 편집하고 다른 노드 원문을 보존한다')
        assert not f.errors and not f.external, (f.errors, f.external)
        f.page.unroute_all(behavior='wait')
        f.browser.close()
except Exception:
    try:
        (f.case / 'inherited-copy-failure.json').write_text(json.dumps(
            {'traffic': f.traffic[-100:], 'checks': f.checks},
            ensure_ascii=False, indent=2))
    except Exception:
        pass
    try:
        f.page.screenshot(path=str(f.case / 'inherited-copy-failure.png'), timeout=10000)
    except Exception:
        pass
    print('EVIDENCE ' + str(f.case), flush=True)
    raise
finally:
    f.stop()
    print(json.dumps({'checks': f.checks, 'mode': mode, 'view': d.is_view,
                      'evidence': str(f.case), 'actualEngineRenderer': True,
                      'actualWindows': False, 'accountOrInference': False}, ensure_ascii=False))
