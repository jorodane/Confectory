"""Explicit C# body and contract edits in the original renderer."""
import json
import shutil
import time
from playwright.sync_api import sync_playwright, expect
import v536_information_csharp_fixture as x
x.edited = x.edited.replace("\r\n", "\n")

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
    row = p.locator('[data-signature-id=arg0]')
    row.locator('[data-signature-name]').fill('text')
    row.locator('[data-signature-type]').click()
    f.page.get_by_role('dialog', name='속성 타입 선택', exact=True).locator('[data-type=string]').click()
    p.get_by_role('button', name='저장', exact=True).click()
    if getattr(x, 'native_context', False):
        return None
    modal = f.page.get_by_role('dialog', name='호출 계약 갱신', exact=True)
    expect(modal).to_be_visible()
    return modal


def cpp(body=x.body_id):
    f.owner().locator('[data-inline-method="' + fn + '"] [data-function-edit], [data-inline-method="' + fn + '"] [data-function-write-direct]').click()
    picker = f.page.get_by_role('dialog', name='구현 선택', exact=True)
    if getattr(x, 'native_context', False):
        expect(picker).to_be_visible()
        picker.locator('[data-information-body="' + body + '"]').click()
    dialog = f.page.locator('[role=dialog]:has([data-code-source])')
    expect(dialog).to_be_visible()
    return dialog


def fill_cpp(dialog, source=x.edited):
    field = dialog.locator('[data-code-source]')
    text = field.input_value()
    prefix = text[:text.index('\n{\n') + 3]
    field.evaluate(r'''el=>{el.focus();const a=el.value.indexOf('\n{\n')+3,b=el.value.lastIndexOf('\n}');el.setSelectionRange(a,b);}''')
    f.page.keyboard.insert_text(source)
    expect(field).to_have_value(prefix + source + '\n}\n')
    f.idle()


def choose(modal):
    if modal is not None:
        modal.locator('[data-abi-remap-accept]').click()
        expect(modal.locator('[data-abi-error]')).to_be_visible()
        modal.locator('[data-abi-input=text]').select_option('value')
        modal.locator('[data-abi-value=text]').fill('직접 입력한 호출 인자')
        modal.locator('[data-abi-disconnect=amount]').select_option('disconnect')
        modal.locator('[data-abi-remap-accept]').click()
        expect(modal).to_have_count(0)
    dialog = cpp()
    fill_cpp(dialog)
    assert pending()[0][1]['bodyDrafts'] and not pending()[0][1]['mapping'].get('bodies')
    dialog.locator('[data-code-cancel]').click()
    assert not pending()[0][1].get('bodyDrafts') and not pending()[0][1]['mapping'].get('bodies')
    dialog = cpp()
    fill_cpp(dialog)
    held = restart(8)
    assert f.pending() == held and pending()[0][1]['bodyDrafts']
    dialog = cpp()
    assert x.edited in dialog.locator('[data-code-source]').input_value()
    f.page.screenshot(path=str(f.case / 'manual-body-code.png'))
    dialog.locator('[data-code-save]').click()
    expect(dialog).to_have_count(0)
    value = pending()[0][1]
    assert value['mapping']['bodies'][x.body_id]['text'] == x.edited and not value['bodyDrafts']
    for body, path in getattr(x, 'context_bodies', {}).items():
        if body == x.body_id:
            continue
        dialog = cpp(body)
        fill_cpp(dialog, x.edited_files[path])
        dialog.locator('[data-code-save]').click()
        expect(dialog).to_have_count(0)
        assert pending()[0][1]['mapping']['bodies'][body]['text'] == x.edited_files[path]


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
        if modal is not None:
            modal.locator('[data-abi-remap-cancel]').click()
        assert pending() and checkpoint.read_bytes() == baseline
        f.owner().locator('[data-own-functions-toggle]').press('Control+z')
        assert not pending()
        modal = edit()
        choose(modal)
        value = pending()[0][1]
        assert value['signature'] == x.new and value['mapping']['bodies']
        f.owner().locator('[data-own-functions-toggle]').press('Control+z')
        f.owner().locator('[data-own-functions-toggle]').press('Control+y')
        assert pending()[0][1] == value
        preserved()
        held = restart(1)
        assert f.pending() == held and pending()[0][1] == value
        f.checked('원본 함수·직접 편집한 C#의 취소·Undo/Redo·미저장 cold는 계약·정확한 입력을 보존한다')
        if mode.endswith('projects'):
            alist = f.state()['listingId']
            held = f.pending()
            f.page.close()
            f.stop()
            other = f.case / 'other root' / 'owned project'
            shutil.copytree(f.project, other, ignore=shutil.ignore_patterns('.confectory'))
            f.env['CONFECTORY_WEB_PROJECT'] = str(other / 'project.cproj')
            f.start(2)
            f.invoke('select', {'id': owner})
            f.invoke('saveDraft', {})
            blist = f.state()['listingId']
            other_checkpoint = next(other.glob('.confectory/edit-workspaces/*/draft.json'))
            other_baseline = other_checkpoint.read_bytes()
            f.page = f.setup()
            f.page.set_viewport_size({'width': 2300, 'height': 1700})
            def enter(listing):
                f.page.locator('.brand').click()
                expect(f.page.locator('.home-grid')).to_be_visible()
                f.page.locator('[data-enter="' + listing + '"]').click()
                expect(f.page.locator('.work-body')).to_be_visible()
                f.idle()
            enter(alist)
            assert pending()[0][1] == value
            dialog = cpp()
            dialog.locator('[data-code-save]').evaluate('el=>globalThis.staleManualSave=el')
            dialog.locator('[data-code-cancel]').click()
            enter(blist)
            d.open_info()
            assert not pending()
            f.page.evaluate('()=>staleManualSave.click()')
            assert not pending() and checkpoint.read_bytes() == baseline and other_checkpoint.read_bytes() == other_baseline
            enter(alist)
            assert pending()[0][1] == value
            preserved()
            f.checked('동일 namespace 프로젝트 전환은 C#·계약 입력을 분리하고 닫힌 편집창 저장이 다른 프로젝트를 바꾸지 않는다')
        elif mode.endswith('cancel'):
            f.owner().locator('[data-element-action=discard]').click()
            f.idle()
            assert not pending() and checkpoint.read_bytes() == baseline
            preserved()
            restart(2)
            assert not pending() and checkpoint.read_bytes() == baseline
            f.checked('C#과 계약의 실제 변경 취소·재시작은 모든 선언·본문·호출자를 미적용으로 유지한다')
        elif mode.endswith('conflict'):
            s = f.state()['schema']
            f.invoke('editDescription', {'id': owner, 'hash': s['textHash'], 'revision': s['revision'], 'value': '다른 편집자 입력 보존'})
            f.rejected_save()
            assert pending()[0][1] == value and checkpoint.read_bytes() == baseline
            preserved()
            f.checked('실제 동시 정보 변경은 전체 미적용이며 C# 원문·계약 선택과 타 편집자 입력을 보존한다')
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
                f.checked('C#·계약 저장 및 receipt 응답 유실 뒤 cold는 결과 조회로 복원하며 중복 저장하지 않는다')
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
                    f.checked('실제 화면 저장 실패는 선언·C#·호출자 모두 미적용이며 직접 편집 입력을 보존한다')
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
            for path, source in getattr(x, 'edited_files', {x.body_path: x.edited}).items():
                assert (f.project / path).read_bytes() == source.encode()
            f.checked('직접 편집한 C#·계약·호출자는 화면 저장·재시작·Review 취소/Confirm에서 한 후보로 반영된다')
        assert not f.errors and not f.external, (f.errors, f.external)
        f.page.screenshot(path=str(f.case / 'output-remap-ui.png'))
        f.browser.close()
except Exception:
    try:
        (f.case / 'output-remap-ui-failure.json').write_text(json.dumps({'state': f.state(), 'checks': f.checks, 'traffic': f.traffic[-50:]}, ensure_ascii=False, indent=2))
    except Exception:
        pass
    raise
finally:
    print(json.dumps({'checks': f.checks, 'mode': mode, 'view': d.is_view, 'evidence': str(f.case), 'actualEngineRenderer': True, 'nativeWindows': False}, ensure_ascii=False))
    f.stop()
