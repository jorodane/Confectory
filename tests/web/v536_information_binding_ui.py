"""Existing v536 delete/recovery interactions over a real fixture engine/renderer."""
import json
import shutil
import time
from playwright.sync_api import sync_playwright, expect
import v536_information_binding_api as a

f, d, owner, function, mode = a.f, a.d, a.owner, a.function, a.mode
assert mode in ['normal', 'own', 'copy', 'copy-pending', 'registered', 'storage', 'loss', 'loss-cold', 'conflict', 'projects', 'cancel'], mode


def slot():
    return f.owner().locator(('[data-inline-method="' if mode == 'own' else '[data-module-method="') + a.function + '"]')


def current():
    s = f.state()
    return next(row['schema'] for row in s['editorViews'] if row['view'] == '1') if d.is_view else s['schema']


def live_source():
    s = f.state()
    return next(row['draft']['text'] for row in s['editorViews'] if row['view'] == '1') if d.is_view else s['draft']['text']


def wait(endpoint, after, action=None, ok=True):
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        ids = {r['invoke']['requestId'] for r in f.traffic[after:] if r.get('invoke', {}).get('endpoint') == endpoint
               and (action is None or r['invoke']['input'].get('action') == action)}
        rows = [r['result'] for r in f.traffic[after:] if r.get('result', {}).get('requestId') in ids and r['result'].get('error', {}).get('code') != 'stale_revision']
        if rows:
            assert bool(rows[-1].get('ok')) == ok, rows
            f.idle()
            return rows[-1]
        f.page.wait_for_timeout(20)
    raise AssertionError({'endpoint': endpoint, 'action': action, 'evidence': str(f.case)})


def unchanged():
    assert all((f.project / p).read_bytes() == value for p, value in a.initial.items() if p not in ['FreeInfo.celem', 'project.cproj'])
    assert all(p.read_bytes() == value for p, value in a.foreign_original.items())
    expect(f.owner().get_by_label('Power 기본값', exact=True)).to_have_value('9223372036854775806')
    # The underlying app is intentionally inert while the existing modal is
    # open; closing its last dialog must release that state.
    assert f.page.locator('#app').evaluate('el=>el.inert') == bool(f.page.get_by_role('dialog').count())
    if mode == 'cancel' and d.is_view:
        d.verify_peer()


def check(present):
    expect(slot()).to_be_visible()
    if present:
        expect(slot().locator('[data-function-delete-implementation]')).to_be_enabled()
        data = current()
        if data is None:
            # A rejected command exposes its live source even when its cached
            # projection is absent. Verify that source without refreshing or
            # repairing the UI before exercising the original retry button.
            parsed = f.metadata('inspect', text=live_source())
            assert any(edge.get('role') == 'provide' and edge.get('function') == a.function and edge.get('target') == a.implementation for edge in parsed['relations']['edges'])
        else:
            assert next(p for p in data['providers'] if p['function'] == a.function and p['origin'] == owner)['implementation'] == a.implementation
    elif mode not in ['registered', 'own']:
        expect(slot().locator('[data-function-delete-implementation]')).to_be_disabled()
        assert next(p for p in current()['providers'] if p['function'] == a.function)['origin'] == f.n + 'Leaf'
    else:
        expect(slot().locator('[data-function-write-direct]')).to_be_visible()
    if getattr(a, 'archive_copy', False) and not present:
        receipt = next(row for row in f.state()['retirements'] if row['owner'] == owner)
        assert receipt['mode'] == 'information-copy-v1'
        assert a.implementation in receipt['ids'] and len(receipt['ids']) >= 3
    unchanged()


def dialog():
    f.idle()
    after = len(f.traffic)
    slot().locator('[data-function-delete-implementation]').click()
    popup = f.page.get_by_role('dialog', name='구현 삭제', exact=True)
    expect(popup).to_be_visible()
    wait('planBrowserRemoval', after)
    expect(popup).to_contain_text('원본과 편집 초안은 복구할 수 있게 보관' if getattr(a, 'archive_copy', False) else '이 정보의 연결만 해제')
    f.page.screenshot(path=str(f.case / 'binding-delete-modal.png'))
    return popup


def delete(cancel=False):
    popup = dialog()
    if cancel:
        popup.locator('[data-implementation-cancel]').click()
        expect(popup).to_have_count(0)
        check(True)
        return
    after = len(f.traffic)
    popup.locator('[data-implementation-confirm]').click()
    wait('browserRetirement', after, 'apply')
    expect(popup).to_have_count(0)
    check(False)


def recover():
    f.idle()
    f.page.locator('#workspace').click(button='right', position={'x': 80, 'y': 100})
    f.page.get_by_role('button', name='프로젝트 브라우저', exact=True).click()
    browser = f.page.locator('.window[data-key^="browser:project:"]')
    browser.locator('[data-browser-control="browser-actions"]').click()
    f.page.locator('.context-menu').get_by_role('button', name='삭제 항목 복구', exact=True).click()
    after = len(f.traffic)
    f.page.locator('.context-menu').get_by_role('button', name=a.label, exact=True).click()
    wait('browserRetirement', after, 'recover')
    browser.locator('[data-close]').first.click()
    f.idle()
    check(True)


def restart(i):
    f.pending()
    f.page.unroute_all(behavior='wait')
    f.page.close()
    f.stop()
    f.start(i)
    f.page = f.setup()
    f.page.set_viewport_size({'width': 2300, 'height': 1500})
    if d.is_view:
        f.owner = lambda: f.page.locator('.window[data-key=editor-1]')
    expect(f.owner().locator('.object-title-name')).to_have_text('FreeInfo')
    f.idle()


def accept():
    review = d.review()
    review.locator('[data-reject]').click()
    unchanged()
    review = d.review()
    if review.locator('[data-review-advanced]').count():
        review.locator('[data-review-advanced]').click()
        if review.locator('[data-advanced-reviewed]').count():
            review.locator('[data-advanced-reviewed]').check()
    after = len(f.traffic)
    review.locator('#confirm').click()
    wait('confirmGroup', after)
    expect(review).to_have_count(0, timeout=120000)
    f.idle()


def setup_page():
    f.page = f.setup()
    f.page.set_viewport_size({'width': 2300, 'height': 1500})
    d.open_info()
    head = f.owner().locator('.object-title-name').bounding_box()
    box = f.owner().bounding_box()
    f.page.mouse.move(head['x'] + 5, head['y'] + 5)
    f.page.mouse.down()
    f.page.mouse.move(1780 + head['x'] - box['x'] + 5, 160 + head['y'] - box['y'] + 5, steps=10)
    f.page.mouse.up()
    assert abs(f.owner().bounding_box()['width'] - 460) < 1
    check(True)


try:
    a.setup()
    f.invoke('select', {'id': f.id})
    with sync_playwright() as pw:
        expect.set_options(timeout=60000)
        f.browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        setup_page()
        if mode == 'cancel' and d.is_view:
            d.open_peer()
            peer = f.page.locator('.window[data-key=editor-2]')
            head = peer.locator('.object-title-name').bounding_box()
            box = peer.bounding_box()
            f.page.mouse.move(head['x'] + 5, head['y'] + 5)
            f.page.mouse.down()
            f.page.mouse.move(30 + head['x'] - box['x'] + 5, 850 + head['y'] - box['y'] + 5, steps=10)
            f.page.mouse.up()
            d.verify_peer()
        before = a.checkpoint.read_bytes()
        if mode in ['loss', 'loss-cold']:
            mutations, queries, lost = {}, set(), set()
            def intercept(route):
                body = route.request.post_data_json
                if body.get('op') == 'invoke':
                    if body.get('endpoint') == 'browserRetirement':
                        mutations[body['requestId']] = body['input']['action']
                    elif body.get('endpoint') == 'browserArchiveOutcome':
                        queries.add(body['requestId'])
                if body.get('op') == 'update':
                    response = route.fetch()
                    payload = response.json()
                    for row in payload.get('results', []):
                        rid = row['requestId']
                        if row.get('ok') and (rid in mutations and rid not in lost or mode == 'loss-cold' and rid in queries):
                            lost.add(rid)
                            row.clear()
                            row.update(requestId=rid, ok=False, error={'code': 'transport_lost'})
                    route.fulfill(response=response, json=payload)
                    return
                route.fallback()
            f.page.route('**/api/request', intercept)
            popup = dialog()
            after = len(f.traffic)
            popup.locator('[data-implementation-confirm]').click()
            if mode == 'loss':
                wait('browserArchiveOutcome', after)
                expect(popup).to_have_count(0)
                check(False)
            else:
                expect(f.page.locator('#status')).to_contain_text('[archive-outcome]', timeout=60000)
                f.idle()
                assert queries & lost
                held = f.pending()
                assert any(v.get('kind') == 'information-retirement' for _, v in held['blueprint'])
                popup.locator('[data-implementation-cancel]').click()
                restart(1)
                check(False)
                assert f.pending() == held
                recover()
                assert not any(v.get('kind') == 'information-retirement' for _, v in f.pending()['blueprint'])
            assert list(mutations.values()).count('apply') == 1
            f.checked('성공 응답' + ('/조회 유실과 cold' if mode == 'loss-cold' else ' 유실') + '은 binding receipt를 조회하며 공유 원문/입력을 지키고 apply를 중복하지 않는다')
        elif mode == 'conflict':
            popup = dialog()
            s = current()
            f.invoke('editViewDescription' if d.is_view else 'editDescription', {'id': owner, 'hash': s['textHash'], 'revision': s['revision'], 'value': '계획 뒤 새 정보 입력', **({'view': '1'} if d.is_view else {})})
            after = len(f.traffic)
            popup.locator('[data-implementation-confirm]').click()
            wait('browserRetirement', after, 'apply', False)
            assert a.checkpoint.read_bytes() == before
            popup.locator('[data-implementation-cancel]').click()
            check(True)
            parsed = f.metadata('inspect', text=live_source())
            assert parsed['description'] == '계획 뒤 새 정보 입력'
            f.checked('화면 계획 뒤 동시 입력은 연결·checkpoint 미적용이며 새 정보 원문과 공유/부모 source를 보존한다')
        elif mode == 'projects':
            alist = f.state()['listingId']
            f.page.evaluate('(id)=>{globalThis.staleBindingButton=document.querySelector(`[data-module-method="${id}"] [data-function-delete-implementation]`)}', a.function)
            # Store the old DOM event target, not a replacement callback.
            f.pending()
            f.page.close()
            f.stop()
            bproject = f.case / 'other root' / 'owned project'
            shutil.copytree(f.project, bproject, ignore=shutil.ignore_patterns('.confectory'))
            f.env['CONFECTORY_WEB_PROJECT'] = str(bproject / 'project.cproj')
            f.start(1)
            f.invoke('select', {'id': owner})
            f.invoke('saveDraft', {})
            blist = f.state()['listingId']
            bcheckpoint = next(bproject.glob('.confectory/edit-workspaces/*/draft.json'))
            bsaved = bcheckpoint.read_bytes()
            f.page = f.setup()
            f.page.set_viewport_size({'width': 2300, 'height': 1500})
            def enter(listing):
                f.page.locator('.brand').click()
                expect(f.page.locator('.home-grid')).to_be_visible()
                f.page.locator('[data-enter="' + listing + '"]').click()
                expect(f.page.locator('.work-body')).to_be_visible()
                f.idle()
            enter(alist)
            check(True)
            f.page.evaluate('(id)=>{globalThis.staleBindingButton=document.querySelector(`[data-module-method="${id}"] [data-function-delete-implementation]`)}', a.function)
            enter(blist)
            d.open_info()
            after = len(f.traffic)
            f.page.evaluate('()=>staleBindingButton.click()')
            f.idle()
            assert not f.page.get_by_role('dialog', name='구현 삭제', exact=True).count()
            assert a.checkpoint.read_bytes() == before and bcheckpoint.read_bytes() == bsaved
            assert not any(r.get('invoke', {}).get('endpoint') == 'planBrowserRemoval' for r in f.traffic[after:])
            delete()
            assert a.checkpoint.read_bytes() == before
            enter(alist)
            check(True)
            enter(blist)
            check(False)
            f.checked('동일 namespace A/B 전환은 닫힌 A row의 삭제 이벤트를 거절하고 B의 명시 연결 삭제만 B checkpoint에 반영한다')
        else:
            delete(True)
            assert a.checkpoint.read_bytes() == before
            if mode == 'storage':
                popup = dialog()
                a.checkpoint.chmod(0o400)
                try:
                    after = len(f.traffic)
                    popup.locator('[data-implementation-confirm]').click()
                    wait('browserRetirement', after, 'apply', False)
                    expect(f.page.locator('#status')).to_contain_text('[archive-unapplied]')
                    assert a.checkpoint.read_bytes() == before
                    check(True)
                finally:
                    a.checkpoint.chmod(0o600)
                after = len(f.traffic)
                popup.locator('[data-implementation-confirm]').click()
                wait('browserRetirement', after, 'apply')
                expect(popup).to_have_count(0)
                check(False)
                f.checked('화면의 실제 쓰기 실패는 공유 연결을 부분 해제하지 않으며 readonly 미적용 조회 뒤 명시 재시도한다')
            else:
                delete()
            f.owner().locator('[data-own-functions-toggle]').focus()
            after = len(f.traffic)
            f.page.keyboard.press('Control+z')
            wait('browserRetirement', after, 'recover')
            check(True)
            f.owner().locator('[data-own-functions-toggle]').focus()
            after = len(f.traffic)
            f.page.keyboard.press('Control+y')
            popup = f.page.get_by_role('dialog', name='구현 삭제', exact=True)
            expect(popup).to_be_visible()
            wait('planBrowserRemoval', after)
            popup.locator('[data-implementation-confirm]').click()
            wait('browserRetirement', after, 'apply')
            expect(popup).to_have_count(0)
            check(False)
            assert f.state()['retirements'][0]['mode'] == ('information-copy-v1' if getattr(a, 'archive_copy', False) else 'information-binding-v1')
            f.checked('460px 원본 삭제/취소/Undo/Redo는 소유 copy closure만 보관하고 부모/공유 원문과 fallback을 유지한다' if getattr(a, 'archive_copy', False) else '460px 원본 모듈 삭제/취소/Undo/Redo는 정보 연결만 보관하고 상위 fallback과 부모/공유/copy 본문을 유지한다')
            restart(1)
            check(False)
            recover()
            restart(2)
            check(True)
            f.checked('기존 Browser 복구 메뉴와 cold는 원래 소유 binding을 되살리고 새 copy나 함수/핀을 만들지 않는다')
            delete()
            if mode == 'cancel':
                f.owner().locator('[data-element-action=discard]').click()
                f.idle()
                check(True)
                assert not f.state()['retirements']
                restart(3)
                check(True)
                f.checked('기존 변경 취소/cold는 binding archive와 검토 그룹만 되돌리고 원문/기존 copy/다른 입력을 보존한다')
            else:
                accept()
                unchanged()
                restart(3)
                check(False)
                recover()
                f.owner().locator('[data-element-action=discard]').click()
                f.idle()
                check(False)
                recover()
                accept()
                restart(4)
                check(True)
                assert not f.state()['retirements']
                f.checked('실제 Review 취소/Confirm·cold·확정 복구 취소/재복구·Confirm은 연결 수명만 반영하고 원문·참조·다른 실행 대상을 보존한다')
        f.page.screenshot(path=str(f.case / 'binding-ui.png'))
        assert not f.errors and not f.external, (f.errors, f.external)
        f.browser.close()
except Exception:
    try:
        (f.case / 'binding-ui-failure.json').write_text(json.dumps({'checks': f.checks, 'state': f.state(), 'traffic': f.traffic[-100:], 'errors': f.errors}, ensure_ascii=False, indent=2))
        f.page.screenshot(path=str(f.case / 'binding-ui-failure.png'))
    except Exception:
        pass
    raise
finally:
    print(json.dumps({'checks': f.checks, 'mode': mode, 'view': d.is_view, 'evidence': str(f.case), 'actualEngineRenderer': True, 'nativeWindows': False}, ensure_ascii=False))
    f.stop()
