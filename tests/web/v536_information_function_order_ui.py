"""Original v536 heading drag/Alt-arrow order over a real isolated engine."""
import json
import shutil
import time
from playwright.sync_api import sync_playwright, expect
import v536_information_function_order_api as a

f, d, owner = a.f, a.d, a.owner
mode = a.mode


def schema():
    s = f.state()
    return next(row['schema'] for row in s['editorViews'] if row['view'] == '1') if d.is_view else s['schema']


def visible_order():
    return f.owner().locator('.own-function-list > [data-method-id],.own-function-list > [data-inline-method]').evaluate_all("rows=>rows.map(row=>row.dataset.inlineMethod||row.dataset.methodId)")


def heading(id):
    return f.owner().locator('[data-inline-method="' + id + '"] > .function-node-heading')


def pending():
    return [(key, value) for key, value in d.pending() if value['kind'] == 'function-order']


def preserve():
    assert all((f.project / path).read_bytes() == text for path, text in f.original.items() if path != 'FreeInfo.celem')
    s = schema()
    if s is not None:
        assert {row['id']: row['hash'] for row in s['ownFunctions']} == a.source_hashes
    else:
        state = f.state()
        draft = next(row['draft'] for row in state['editorViews'] if row['view'] == '1') if d.is_view else state['draft']
        parsed = f.metadata('inspect', text=draft['text'])
        assert {row['target'] for row in parsed['relations']['edges'] if row['role'] == 'contain' and row['kind'] == 'function'} == set(a.original_order)
    expect(f.owner().get_by_label('Power 기본값', exact=True)).to_have_value('9223372036854775806')
    assert not f.page.locator('#app').evaluate('el=>el.inert')
    if mode == 'cancel' and d.is_view:
        d.verify_peer()


def wait(endpoint, start, ok=True, action=None):
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        ids = {r['invoke']['requestId'] for r in f.traffic[start:] if r.get('invoke', {}).get('endpoint') == endpoint and (action is None or r['invoke']['input'].get('action') == action)}
        rows = [r['result'] for r in f.traffic[start:] if r.get('result', {}).get('requestId') in ids and r['result'].get('error', {}).get('code') != 'stale_revision']
        if rows:
            assert bool(rows[-1].get('ok')) == ok, rows[-1]
            f.idle()
            return rows[-1]
        f.page.wait_for_timeout(20)
    raise AssertionError({'endpoint': endpoint, 'action': action, 'evidence': str(f.case)})


def save(ok=True):
    f.idle()
    start = len(f.traffic)
    f.owner().locator('[data-element-action=save]').click()
    wait('blueprint', start, ok, 'applySlots')
    if ok:
        deadline = time.monotonic() + 60
        while pending() and time.monotonic() < deadline:
            f.page.wait_for_timeout(20)
        assert not pending(), (f.pending(), f.owner().locator('[data-element-error]').all_text_contents())


def restart(i):
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
    return held


def confirm():
    review = d.review()
    review.locator('[data-reject]').click()
    preserve()
    review = d.review()
    if review.locator('[data-review-advanced]').count():
        review.locator('[data-review-advanced]').click()
        if review.locator('[data-advanced-reviewed]').count():
            review.locator('[data-advanced-reviewed]').check()
    start = len(f.traffic)
    review.locator('#confirm').click()
    wait('confirmGroup', start)
    expect(review).to_have_count(0, timeout=120000)
    f.idle()


try:
    a.setup()
    f.invoke('select', {'id': f.id})
    with sync_playwright() as pw:
        expect.set_options(timeout=60000)
        f.browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 2300, 'height': 1700})
        d.open_info()
        assert visible_order() == a.original_order
        heading(a.functions[2]).press('Alt+ArrowUp')
        assert visible_order() == [a.functions[0], a.locked[0], a.functions[2], a.functions[1], a.locked[1]]
        heading(a.functions[2]).press('Alt+ArrowUp')
        assert visible_order() == a.desired and pending()[0][1]['ids'] == a.desired
        heading(a.functions[2]).press('Control+z')
        assert visible_order() != a.desired
        f.owner().locator('[data-own-functions-toggle]').press('Control+z')
        assert visible_order() == a.original_order and not pending()
        f.owner().locator('[data-own-functions-toggle]').press('Control+y')
        f.owner().locator('[data-own-functions-toggle]').press('Control+y')
        assert visible_order() == a.desired
        preserve()
        f.checked('원본 Alt+↑/↓와 영역 Undo/Redo는 자체 기능만 이동하고 읽기 전용 참조·핀·본문·64비트 값을 보존한다')
        held = restart(1)
        assert f.pending() == held and visible_order() == a.desired
        if mode == 'conflict':
            before = a.checkpoint.read_bytes()
            s = schema()
            f.invoke('editViewDescription' if d.is_view else 'editDescription', {'id': owner, 'hash': s['textHash'], 'revision': s['revision'], 'value': '경합 설명 유지', **({'view': '1'} if d.is_view else {})})
            f.rejected_save()
            assert pending() and pending()[0][1]['ids'] == a.desired and a.checkpoint.read_bytes() == before
            state = f.state()
            draft = next(row['draft'] for row in state['editorViews'] if row['view'] == '1') if d.is_view else state['draft']
            assert f.metadata('inspect', text=draft['text'])['description'] == '경합 설명 유지'
            preserve()
            f.checked('화면의 실제 원문 경합은 순서 입력·동료 설명·checkpoint를 덮지 않고 거절한다')
            raise SystemExit(0)
        if mode == 'loss':
            applies, queries, missing = set(), set(), set()
            def intercept(route):
                body = route.request.post_data_json
                if body.get('op') == 'invoke' and body.get('endpoint') == 'blueprint':
                    action = body.get('input', {}).get('action')
                    if action == 'applySlots':
                        applies.add(body['requestId'])
                    elif applies and action == 'settledSlots':
                        queries.add(body['requestId'])
                response = route.fetch()
                payload = response.json()
                for row in payload.get('results', []):
                    if row['requestId'] in applies | queries:
                        rid = row['requestId']
                        missing.add(rid)
                        row.clear()
                        row.update(requestId=rid, ok=False, error={'code': 'transport_lost'})
                route.fulfill(response=response, json=payload)
            f.page.route('**/api/request', intercept)
            f.owner().locator('[data-element-action=save]').click()
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline and not queries & missing:
                f.page.wait_for_timeout(20)
            assert len(applies) == 1 and queries & missing and pending()
            held = f.pending()
            mark = len(f.traffic)
            restart(2)
            assert f.pending() == held
            f.owner().locator('[data-element-action=save]').click()
            wait('blueprint', mark, True, 'settledSlots')
            deadline = time.monotonic() + 60
            while pending() and time.monotonic() < deadline:
                f.page.wait_for_timeout(20)
            assert not pending() and a.order(schema()) == a.desired
            assert not any(row.get('invoke', {}).get('input', {}).get('action') == 'applySlots' for row in f.traffic[mark:])
            preserve()
            f.checked('순서 저장 성공/조회 응답 유실은 cold 후 receipt 조회로 확인하고 apply를 중복하지 않는다')
            raise SystemExit(0)
        if mode == 'projects':
            alist, before = f.state()['listingId'], a.checkpoint.read_bytes()
            f.pending()
            f.page.close()
            f.stop()
            bproject = f.case / 'other root' / 'owned project'
            shutil.copytree(f.project, bproject, ignore=shutil.ignore_patterns('.confectory'))
            f.env['CONFECTORY_WEB_PROJECT'] = str(bproject / 'project.cproj')
            f.start(2)
            f.invoke('select', {'id': owner})
            f.invoke('saveDraft', {})
            blist = f.state()['listingId']
            bcheckpoint = next(bproject.glob('.confectory/edit-workspaces/*/draft.json'))
            bsaved = bcheckpoint.read_bytes()
            f.page = f.setup()
            f.page.set_viewport_size({'width': 2300, 'height': 1700})
            def enter(listing):
                f.page.locator('.brand').click()
                expect(f.page.locator('.home-grid')).to_be_visible()
                f.page.locator('[data-enter="' + listing + '"]').click()
                expect(f.page.locator('.work-body')).to_be_visible()
                f.idle()
            enter(alist)
            assert visible_order() == a.desired
            heading(a.functions[0]).evaluate('el=>globalThis.staleOrderHeading=el')
            enter(blist)
            d.open_info()
            assert visible_order() == a.original_order
            f.page.evaluate("()=>staleOrderHeading.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowDown',altKey:true,bubbles:true}))")
            f.idle()
            assert not pending() and visible_order() == a.original_order
            assert a.checkpoint.read_bytes() == before and bcheckpoint.read_bytes() == bsaved
            heading(a.functions[1]).press('Alt+ArrowUp')
            b_order = [a.functions[1], a.functions[0], a.locked[0], a.locked[1], a.functions[2]]
            assert visible_order() == b_order
            save()
            assert a.checkpoint.read_bytes() == before
            assert all((bproject / path).read_bytes() == text for path, text in f.original.items() if path != 'FreeInfo.celem')
            enter(alist)
            assert visible_order() == a.desired
            enter(blist)
            assert visible_order() == b_order
            f.checked('동일 namespace 프로젝트 전환은 A 입력과 B 저장을 분리하며 닫힌 A heading 이벤트를 거절한다')
            raise SystemExit(0)
        if mode == 'storage':
            before = a.checkpoint.read_bytes()
            a.checkpoint.chmod(0o400)
            try:
                save(False)
                assert a.checkpoint.read_bytes() == before and pending() and visible_order() == a.desired
                preserve()
            finally:
                a.checkpoint.chmod(0o600)
            f.checked('화면 쓰기 실패는 순서 입력과 원문/checkpoint 전체를 보존한다')
        if mode == 'cancel' and d.is_view:
            d.open_peer()
            peer = f.page.locator('.window[data-key=editor-2]')
            title = peer.locator('.object-title-name').bounding_box()
            box = peer.bounding_box()
            f.page.mouse.move(title['x'] + 5, title['y'] + 5)
            f.page.mouse.down()
            f.page.mouse.move(30 + title['x'] - box['x'] + 5, 850 + title['y'] - box['y'] + 5, steps=10)
            f.page.mouse.up()
            d.verify_peer()
        save()
        assert a.order(schema()) == a.desired
        preserve()
        restart(2)
        assert visible_order() == a.desired and not pending()
        f.checked('미저장 입력과 저장된 순서의 cold 복원은 창별 문맥·원래 함수 식별성을 유지한다')
        if mode == 'cancel':
            saved_checkpoint = a.checkpoint.read_bytes()
            # Discard restores the last explicit draft Save, not pre-Save source.
            expect(f.owner().locator('[data-element-action=discard]')).to_be_disabled()
            heading(a.functions[2]).press('Alt+ArrowDown')
            assert visible_order() != a.desired and pending()
            f.owner().locator('[data-element-action=discard]').click()
            f.idle()
            assert visible_order() == a.desired and not pending()
            assert a.checkpoint.read_bytes() == saved_checkpoint
            preserve()
            restart(3)
            assert visible_order() == a.desired and not pending()
            assert a.checkpoint.read_bytes() == saved_checkpoint
            f.checked('변경 취소는 새 순서 입력만 마지막 저장본으로 돌리고 cold·다른 창 입력·checkpoint를 보존한다')
        else:
            confirm()
            preserve()
            restart(3)
            assert visible_order() == a.desired
            # Native mouse drag uses the original HTML5 heading and row target.
            source, target = heading(a.functions[2]), f.owner().locator('[data-inline-method="' + a.functions[1] + '"]')
            source.drag_to(target, source_position={'x': 120, 'y': 2}, target_position={'x': 120, 'y': target.bounding_box()['height'] - 3})
            dragged = [a.functions[0], a.locked[0], a.functions[1], a.functions[2], a.locked[1]]
            assert visible_order() == dragged and pending()[0][1]['ids'] == dragged
            save()
            confirm()
            restart(4)
            assert visible_order() == dragged
            preserve()
            f.checked('원본 제목 드래그/drop·검토 취소/명시적 Confirm·확정 뒤 재편집/cold도 contain 순서만 변경한다')
        f.page.screenshot(path=str(f.case / 'function-order-ui.png'))
        assert not f.errors and not f.external, (f.errors, f.external)
        f.browser.close()
except Exception:
    try:
        (f.case / 'function-order-ui-failure.json').write_text(json.dumps({'state': f.state(), 'checks': f.checks, 'traffic': f.traffic[-60:]}, ensure_ascii=False, indent=2))
    except Exception:
        pass
    raise
finally:
    print(json.dumps({'checks': f.checks, 'mode': mode, 'view': d.is_view, 'evidence': str(f.case), 'actualEngineRenderer': True, 'nativeWindows': False}, ensure_ascii=False))
    f.stop()
