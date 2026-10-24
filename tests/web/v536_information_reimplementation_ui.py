"""Original information implementation actions after deletion, real renderer/engine."""
import json
import time
from playwright.sync_api import sync_playwright, expect
import v536_information_reimplementation as a

f, d, owner, fn, mode = a.f, a.d, a.owner, a.fn, a.mode
assert mode in ['pending', 'confirmed', 'loss', 'storage'], mode


def method():
    return f.owner().locator('[data-inline-method="' + fn + '"]')


def current():
    s = f.state()
    return next(v['schema'] for v in s['editorViews'] if v['view'] == '1') if d.is_view else s['schema']


def wait(endpoint, after, action=None, ok=True):
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        ids = {r['invoke']['requestId'] for r in f.traffic[after:] if r.get('invoke', {}).get('endpoint') == endpoint
               and (action is None or r['invoke']['input'].get('action') == action)}
        rows = [r['result'] for r in f.traffic[after:] if r.get('result', {}).get('requestId') in ids
                and r['result'].get('error', {}).get('code') != 'stale_revision']
        if rows:
            assert bool(rows[-1].get('ok')) == ok, rows
            return rows[-1]
        f.page.wait_for_timeout(20)
    raise AssertionError({'endpoint': endpoint, 'action': action, 'evidence': str(f.case)})


def delete(cancel=False):
    after = len(f.traffic)
    method().locator('[data-function-delete-implementation]').click()
    dialog = f.page.get_by_role('dialog', name='구현 삭제', exact=True)
    expect(dialog).to_be_visible()
    wait('planBrowserRemoval', after)
    if cancel:
        dialog.locator('[data-implementation-cancel]').click()
        expect(dialog).to_have_count(0)
        return
    after = len(f.traffic)
    dialog.locator('[data-implementation-confirm]').click()
    wait('browserRetirement', after)
    expect(dialog).to_have_count(0)
    expect(method().locator('[data-function-write-direct]')).to_be_visible()
    a.check_old_sources()


def script(text, accept=True):
    f.author().locator(':scope>.window-title .caption').click(position={'x': 5, 'y': 5})
    f.author().locator('[data-bp-overview-node=body]').click()
    f.author().locator('[data-bp-node=body] [data-internal-code]').click()
    dialog = f.page.locator('.bp-script-dialog')
    value = dialog.locator('[data-code-source]')
    expect(value).to_be_visible()
    before = value.input_value()
    value.evaluate(r'''el=>{el.focus();const a=el.value.indexOf('\n{\n')+3,b=el.value.lastIndexOf('\n}');if(a<3||b<a)throw Error('protected body range');el.setSelectionRange(a,b);}''')
    f.page.keyboard.insert_text(text)
    dialog.locator('[data-code-save]' if accept else '[data-code-cancel]').click()
    expect(dialog).to_have_count(0)
    return before


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


def accept(review):
    if review.locator('[data-review-advanced]').count():
        review.locator('[data-review-advanced]').click()
        if review.locator('[data-advanced-reviewed]').count():
            review.locator('[data-advanced-reviewed]').check()
    after = len(f.traffic)
    review.locator('#confirm').click()
    wait('confirmGroup', after)
    expect(review).to_have_count(0, timeout=120000)
    f.idle()


try:
    a.setup()
    f.invoke('select', {'id': f.id})
    with sync_playwright() as pw:
        expect.set_options(timeout=60000)
        f.browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 2300, 'height': 1500})
        d.open_info()
        # Original drag keeps the information card from occluding the author caption.
        head = f.owner().locator('.object-title-name').bounding_box()
        box = f.owner().bounding_box()
        f.page.mouse.move(head['x'] + 5, head['y'] + 5)
        f.page.mouse.down()
        f.page.mouse.move(1780 + head['x'] - box['x'] + 5, 160 + head['y'] - box['y'] + 5, steps=10)
        f.page.mouse.up()
        assert abs(f.owner().bounding_box()['width'] - 460) < 1
        delete(True)
        before = a.checkpoint.read_bytes()
        delete()
        token = f.state()['retirements'][0]['token']
        f.owner().locator('[data-own-functions-toggle]').focus()
        after = len(f.traffic)
        f.page.keyboard.press('Control+z')
        wait('browserRetirement', after)
        expect(method().locator('[data-function-edit]')).to_be_visible()
        assert not f.state()['retirements']
        f.owner().locator('[data-own-functions-toggle]').focus()
        f.page.keyboard.press('Control+y')
        dialog = f.page.get_by_role('dialog', name='구현 삭제', exact=True)
        expect(dialog).to_be_visible()
        after = len(f.traffic)
        dialog.locator('[data-implementation-confirm]').click()
        wait('browserRetirement', after)
        expect(dialog).to_have_count(0)
        f.idle()
        token = f.state()['retirements'][0]['token']
        expect(method().locator('[data-function-write-direct]')).to_be_visible()
        a.check_old_sources()
        f.checked('460px 원본 삭제 취소·Undo/Redo는 함수 정의/핀/원문과 복구 가능한 이전 구현을 유지한다')
        if mode == 'confirmed':
            accept(d.review())
            restart(1)
        held = a.checkpoint.read_bytes()
        creates, lost = set(), []
        if mode == 'loss':
            def intercept(route):
                body = route.request.post_data_json
                if body.get('op') == 'invoke' and body.get('endpoint') == 'blueprint' and body['input'].get('action') == 'createFeature':
                    creates.add(body['requestId'])
                response = route.fetch()
                payload = response.json()
                for row in payload.get('results', []):
                    if row['requestId'] in creates and row['requestId'] not in lost and row.get('ok'):
                        lost.append(row['requestId'])
                        rid = row['requestId']
                        row.clear()
                        row.update(requestId=rid, ok=False, error={'code': 'transport_lost'})
                route.fulfill(response=response, json=payload)
            f.page.route('**/api/request', intercept)
        if mode == 'storage':
            a.checkpoint.chmod(0o400)
            try:
                after = len(f.traffic)
                method().locator('[data-function-write-direct]').click()
                wait('blueprint', after, 'createFeature', False)
                f.idle()
                assert a.checkpoint.read_bytes() == held and not f.author().is_visible()
                assert not any(v['function'] == fn for v in current()['providers'])
                a.check_old_sources()
            finally:
                a.checkpoint.chmod(0o600)
            f.checked('화면 생성 쓰기 실패는 새 provider/body를 남기지 않으며 명시적 같은 창 재시도를 허용한다')
        f.idle()
        method().locator('[data-function-write-direct]').click()
        expect(f.author().locator('[data-bp-node=body]')).to_be_visible()
        expect(f.author().locator('[data-bp-name]')).to_have_value('삭제 뒤 새 구현')
        f.idle()
        new_impl = next(v for v in current()['providers'] if v['function'] == fn)['implementation']
        assert new_impl != a.old_impl
        assert f.state()['retirements'][0]['token'] == token
        if mode == 'loss':
            assert len(creates) == 1 and len(lost) == 1, {'creates': sorted(creates), 'lost': lost}
        a.check_old_sources()
        f.checked('직접 작성은 새 ID의 실제 편집기를 열고 ' + ('생성 응답 유실에도 조회만으로 복구하여 중복 생성하지 않는다' if mode == 'loss' else '이전 archive와 이름/핀/정확한 값을 보존한다'))
        script('return; // 취소될 입력', False)
        assert not [v for _, v in f.pending()['blueprint'] if v.get('kind') == 'source']
        script('return; // 새 본문 한글 😀')
        held_inputs = f.pending()
        assert held_inputs['blueprint']
        restart(2)
        assert f.pending() == held_inputs
        expect(f.author()).to_be_visible()
        script('return; // 새 본문 한글 😀')
        f.author().locator('[data-bp-save]').click()
        expect(f.author().locator('.bp-status')).to_have_text('저장됨', timeout=60000)
        f.idle()
        a.check_old_sources()
        f.checked('실제 C# 팝오버 취소·본문 입력·cold·저장은 새 구현만 변경하고 이전 원본·다른 target을 보존한다')
        f.close_author()
        r = d.review()
        r.locator('[data-reject]').click()
        a.check_old_sources()
        accept(d.review())
        restart(3)
        assert next(v for v in current()['providers'] if v['function'] == fn)['implementation'] == new_impl
        assert f.state()['retirements'][0]['state'] == 'confirmed'
        a.check_old_sources()
        f.page.screenshot(path=str(f.case / 'reimplementation-ui.png'))
        assert not f.errors and not f.external, (f.errors, f.external)
        f.checked('화면 Review 취소·명시 Confirm·cold는 새 구현 등록과 이전 archive를 별개로 확정한다')
        f.browser.close()
except Exception:
    try:
        (f.case / 'failure.json').write_text(json.dumps({'checks': f.checks, 'state': f.state(), 'traffic': f.traffic[-100:]}, ensure_ascii=False, indent=2))
        f.page.screenshot(path=str(f.case / 'failure.png'))
    except Exception:
        pass
    raise
finally:
    print(json.dumps({'checks': f.checks, 'mode': mode, 'view': d.is_view, 'evidence': str(f.case),
                      'actualEngineRenderer': True, 'nativeWindows': False}, ensure_ascii=False))
    f.stop()
