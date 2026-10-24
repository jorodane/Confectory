"""Existing v536 output picker and atomic Save through the actual renderer."""
import json
import time
from playwright.sync_api import sync_playwright, expect
import v536_information_output_types_fixture as x

f, d, owner, fn, mode = x.f, x.d, x.owner, x.fn, x.mode


def pending():
    return [(key, value) for key, value in d.pending() if value['kind'] == 'function-edit']


def popup():
    f.owner().locator('[data-inline-method="' + fn + '"] > .function-node-heading').dblclick(position={'x': 190, 'y': 3})
    p = f.page.locator('.function-detail-popover')
    expect(p).to_be_visible()
    return p


def preserved():
    expect(f.owner().get_by_label('Power 기본값', exact=True)).to_have_value('9223372036854775806')
    assert not f.page.locator('#app').evaluate('el=>el.inert')
    assert all((f.project / p).read_bytes() == b for p, b in x.snapshot.items())


def restart(i):
    held = f.pending()
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


def wait(endpoint, start, ok=True, action=None):
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        ids = {r['invoke']['requestId'] for r in f.traffic[start:] if r.get('invoke', {}).get('endpoint') == endpoint and (action is None or r['invoke']['input'].get('action') == action)}
        rows = [r['result'] for r in f.traffic[start:] if r.get('result', {}).get('requestId') in ids and r['result'].get('error', {}).get('code') != 'stale_revision']
        if rows:
            assert bool(rows[-1]['ok']) == ok, rows[-1]
            f.idle()
            return
        f.page.wait_for_timeout(20)
    raise AssertionError({'endpoint': endpoint, 'action': action, 'evidence': str(f.case)})


def edit():
    p = popup()
    dimensions = p.locator('.feature-io-card,.feature-io-heading,.feature-io-row').evaluate_all('(xs)=>xs.map(x=>{const r=x.getBoundingClientRect();return [r.width,r.height]})')
    f.page.screenshot(path=str(f.case / 'output-contract-popover.png'))
    field = 'return' if x.name == 'return' else 'arg2'
    p.locator('[data-signature-id=' + field + '] [data-signature-type]').click()
    f.page.get_by_role('dialog', name='속성 타입 선택', exact=True).locator('[data-type=double]').click()
    assert p.locator('.feature-io-card,.feature-io-heading,.feature-io-row').evaluate_all('(xs)=>xs.map(x=>{const r=x.getBoundingClientRect();return [r.width,r.height]})') == dimensions
    p.get_by_role('button', name='저장', exact=True).click()
    modal = f.page.get_by_role('dialog', name='호출 계약 갱신', exact=True)
    expect(modal).to_be_visible()
    f.page.screenshot(path=str(f.case / 'output-contract-mapping.png'))
    return modal


def choose(modal):
    modal.locator('[data-abi-target^="output:"] [data-abi-input=value]').select_option('pin:real')
    modal.locator('[data-abi-output=' + x.name + ']').select_option('count' if x.name == 'return' else 'return')
    modal.locator('[data-abi-remap-accept]').click()
    expect(modal).to_have_count(0)


try:
    f.start(0)
    f.invoke('select', {'id': owner})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    baseline = checkpoint.read_bytes()
    with sync_playwright() as pw:
        expect.set_options(timeout=60000)
        f.browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 2300, 'height': 1700})
        d.open_info()
        p = popup()
        p.locator('[data-detail-description]').fill('취소할 새 입력')
        p.locator('[data-detail-cancel]').click()
        assert not pending()
        modal = edit()
        modal.locator('[data-abi-remap-cancel]').click()
        assert pending() and checkpoint.read_bytes() == baseline
        f.owner().locator('[data-own-functions-toggle]').press('Control+z')
        assert not pending()
        modal = edit()
        choose(modal)
        value = pending()[0][1]
        assert value['signature'] == x.new and value['mapping']['outputs']
        f.owner().locator('[data-own-functions-toggle]').press('Control+z')
        f.owner().locator('[data-own-functions-toggle]').press('Control+y')
        assert pending()[0][1] == value
        preserved()
        held = restart(1)
        assert f.pending() == held and pending()[0][1] == value
        f.checked('원본 상세창과 기존 출력 대응 선택·취소·Undo/Redo·cold는 source/호환 연결과 정확한 입력을 보존한다')
        if mode.endswith('cancel'):
            f.owner().locator('[data-element-action=discard]').click()
            f.idle()
            assert not pending() and checkpoint.read_bytes() == baseline
            preserved()
            restart(2)
            assert not pending() and checkpoint.read_bytes() == baseline
            f.checked('출력 계약의 실제 변경 취소·재시작은 모든 선언·생산자·소비자를 미적용으로 유지한다')
        elif mode.endswith('conflict'):
            s = f.state()['schema']
            f.invoke('editDescription', {'id': owner, 'hash': s['textHash'], 'revision': s['revision'], 'value': '다른 편집자 입력 보존'})
            f.rejected_save()
            assert pending()[0][1] == value and checkpoint.read_bytes() == baseline
            preserved()
            f.checked('실제 동시 정보 변경은 전체 미적용이며 출력 source/연결 선택과 타 편집자 입력을 보존한다')
        else:
            if mode.endswith('loss'):
                applies, queries, masked = set(), set(), set()
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
                            masked.add(rid)
                            row.clear()
                            row.update(requestId=rid, ok=False, error={'code': 'transport_lost'})
                    route.fulfill(response=response, json=payload)
                f.page.route('**/api/request', intercept)
                f.owner().locator('[data-element-action=save]').click()
                deadline = time.monotonic() + 90
                while time.monotonic() < deadline and not queries & masked:
                    f.page.wait_for_timeout(20)
                assert len(applies) == 1 and queries & masked and pending()
                f.page.unroute_all(behavior='wait')
                held = restart(2)
                assert f.pending() == held
                mark = len(f.traffic)
                f.owner().locator('[data-element-action=save]').click()
                wait('blueprint', mark, True, 'settledSlots')
                assert not any(r.get('invoke', {}).get('input', {}).get('action') == 'applySlots' for r in f.traffic[mark:])
                f.checked('출력 저장 및 receipt 응답 유실 뒤 cold는 결과 조회로 복원하며 중복 저장하지 않는다')
            else:
                if mode.endswith('storage'):
                    checkpoint.chmod(0o400)
                    try:
                        mark = len(f.traffic)
                        f.owner().locator('[data-element-action=save]').click()
                        wait('blueprint', mark, False, 'applySlots')
                        assert pending()[0][1] == value and checkpoint.read_bytes() == baseline
                        preserved()
                    finally:
                        checkpoint.chmod(0o600)
                    f.checked('실제 화면 저장 실패는 생산자/소비자 모두 미적용이며 출력 선택 입력을 보존한다')
                mark = len(f.traffic)
                f.owner().locator('[data-element-action=save]').click()
                wait('blueprint', mark, True, 'applySlots')
            deadline = time.monotonic() + 60
            while pending() and time.monotonic() < deadline:
                f.page.wait_for_timeout(20)
            assert not pending()
            x.verify(checkpoint)
            preserved()
            restart(3)
            review = d.review()
            review.locator('[data-reject]').click()
            preserved()
            review = d.review()
            if review.locator('[data-review-advanced]').count():
                review.locator('[data-review-advanced]').click()
                if review.locator('[data-advanced-reviewed]').count():
                    review.locator('[data-advanced-reviewed]').check()
            mark = len(f.traffic)
            review.locator('#confirm').click()
            wait('confirmGroup', mark)
            expect(review).to_have_count(0)
            restart(4)
            assert json.loads((f.project / 'function.node.json').read_text())['source'] == x.record['source']
            f.checked('출력/반환 타입·명시 source·호환 caller 대응은 화면 저장·재시작·Review 취소/Confirm에서 한 후보로 반영된다')
        assert not f.errors and not f.external, (f.errors, f.external)
        f.page.screenshot(path=str(f.case / 'output-type-ui.png'))
        f.browser.close()
except Exception:
    try:
        (f.case / 'output-type-ui-failure.json').write_text(json.dumps({'state': f.state(), 'checks': f.checks, 'traffic': f.traffic[-50:]}, ensure_ascii=False, indent=2))
    except Exception:
        pass
    raise
finally:
    print(json.dumps({'checks': f.checks, 'mode': mode, 'view': d.is_view, 'evidence': str(f.case), 'actualEngineRenderer': True, 'nativeWindows': False}, ensure_ascii=False))
    f.stop()
