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
        f.page.screenshot(path=str(f.case / 'inherited-copy-failure.png'))
        (f.case / 'inherited-copy-failure.json').write_text(json.dumps(
            {'state': f.state(), 'traffic': f.traffic[-70:], 'checks': f.checks},
            ensure_ascii=False, indent=2))
    except Exception:
        pass
    print('EVIDENCE ' + str(f.case), flush=True)
    raise
finally:
    f.stop()
    print(json.dumps({'checks': f.checks, 'mode': mode, 'view': d.is_view,
                      'evidence': str(f.case), 'actualEngineRenderer': True,
                      'actualWindows': False, 'accountOrInference': False}, ensure_ascii=False))
