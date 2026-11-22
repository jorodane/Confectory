"""Resume one authored C# caller from two independently edited type contracts."""
import json
import time

from playwright.sync_api import expect, sync_playwright

import v666_native_type_shared_fixture as fixture


f = fixture.f
d = fixture.c.x.d
shared = fixture.callers[fixture.first]
original = fixture.sources[shared].replace('\r\n', '\n').strip()


def row(function):
    return f.owner().locator(f'[data-inline-method="{function}"]')


def choose_type(function, field):
    row(function).locator('.function-node-heading').press('Enter')
    detail = f.page.locator('.function-detail-popover')
    expect(detail).to_be_visible()
    detail.locator(field).locator('[data-signature-type]').click()
    picker = f.page.get_by_role('dialog', name='속성 타입 선택', exact=True)
    picker.locator('[type=search]').fill('Payload')
    picker.locator('[data-native-type]').filter(has_text=f.n + 'Payload').click()
    detail.locator('button[type=submit]').click()
    expect(detail).to_have_count(0)


def open_source(function, body):
    row(function).locator('[data-function-write-direct],[data-function-edit]').first.click()
    f.page.locator(f'[data-information-body="{body}"]').click()
    dialog = f.page.locator('.bp-script-dialog')
    expect(dialog).to_be_visible()
    return dialog


def replace_source(dialog, before, after):
    field = dialog.locator('[data-code-source]')
    assert before in field.input_value(), field.input_value()
    field.evaluate('''(el, text) => {
        el.focus();
        const from = el.value.indexOf(text);
        el.setSelectionRange(from, from + text.length);
    }''', before)
    f.page.keyboard.insert_text(after)


def close_source(dialog, accept=True):
    dialog.locator('[data-code-save]' if accept else '[data-code-cancel]').click()
    expect(dialog).to_have_count(0)
    f.idle()


def wait_reply(mark, endpoint, action=None):
    stop = time.monotonic() + 90
    while time.monotonic() < stop:
        requests = {
            row['invoke']['requestId']
            for row in f.traffic[mark:]
            if row.get('invoke', {}).get('endpoint') == endpoint
            and (action is None or row['invoke']['input'].get('action') == action)
        }
        replies = [
            row['result'] for row in f.traffic[mark:]
            if row.get('result', {}).get('requestId') in requests
            and row['result'].get('error', {}).get('code') != 'stale_revision'
        ]
        if replies:
            f.idle()
            return replies[-1]
        f.page.wait_for_timeout(25)
    raise AssertionError(f'No {endpoint}/{action} reply: {f.case}')


def owner_save(accepted):
    mark = len(f.traffic)
    f.owner().locator('[data-element-action=save]').click()
    reply = wait_reply(mark, 'blueprint', 'applySlots')
    assert reply['ok'] == accepted, (reply, f.state().get('logs'))


def confirm(review):
    if review.locator('[data-review-advanced]').count():
        review.locator('[data-review-advanced]').click()
        if review.locator('[data-advanced-reviewed]').count():
            review.locator('[data-advanced-reviewed]').check()
    mark = len(f.traffic)
    review.locator('#confirm').click()
    reply = wait_reply(mark, 'confirmGroup')
    assert reply['ok'], reply
    return reply['result']['sourceConfirmed']


def open_editor():
    f.page = f.setup()
    f.page.set_viewport_size({'width': 2300, 'height': 1700})
    d.open_info()


def restart(index):
    f.page.unroute_all(behavior='wait')
    f.page.close()
    f.stop()
    f.start(index)
    open_editor()


def saved_changes(checkpoint):
    # Review can advance session revisions. Source bytes, drafts and receipts
    # still have to match the complete saved group.
    return {
        row['id']: {key: value for key, value in row.items() if key != 'revision'}
        for row in json.loads(checkpoint.read_bytes())['changes']
    }


try:
    f.start(0)
    f.invoke('select', {'id': fixture.owner})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    baseline = checkpoint.read_bytes()
    fixture.execute(70, 'original-shared-caller')
    catalog = fixture.catalogs()[fixture.first]
    payload = next(t['clrType'] for t in catalog['nativeTypes'] if t['id'] == f.n + 'Payload')
    leaf = next(t['clrType'] for t in catalog['nativeTypes'] if t['id'] == f.n + 'Leaf')
    authored = (
        f'int left = calls.Connected.Invoke(new {payload} {{ Value = new {leaf} {{ Count = 30 }} }});\n'
        'var right = calls.SecondSelected.Invoke(40);\n'
        'int result = checked(left * 2 + (int)right.Value.Count);\n'
        'Console.WriteLine(result); return result; // 공동 호출자 원문 😀'
    )
    with sync_playwright() as playwright:
        expect.set_options(timeout=60_000)
        f.browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        open_editor()
        choose_type(fixture.first, '[data-signature-kind=inputs] .feature-io-row')
        first = fixture.bodies[fixture.first]
        dialog = open_source(fixture.first, first)
        replace_source(dialog, fixture.sources[first].strip(), 'return checked((int)amount.Value.Count + 1);')
        close_source(dialog)
        dialog = open_source(fixture.first, shared)
        replace_source(dialog, original, authored)
        close_source(dialog)

        choose_type(fixture.second, '[data-signature-id=return]')
        second = fixture.bodies[fixture.second]
        dialog = open_source(fixture.second, second)
        replace_source(
            dialog, fixture.sources[second].strip(),
            f'return new {payload} {{ Value = new {leaf} {{ Count = amount + 2 }} }};',
        )
        close_source(dialog)
        held = d.pending()
        dialog = open_source(fixture.second, shared)
        observed = dialog.locator('[data-code-source]').input_value()
        assert authored in observed, observed
        replace_source(dialog, 'return result;', 'return result + 1;')
        close_source(dialog, accept=False)
        assert d.pending() == held and checkpoint.read_bytes() == baseline
        fixture.unchanged()

        dialog = open_source(fixture.second, shared)
        assert authored in dialog.locator('[data-code-source]').input_value()
        close_source(dialog)
        agreed = d.pending()
        edits = {edit['id']: edit for _, edit in agreed}
        assert edits[fixture.first]['mapping']['bodies'][shared]['text'] == edits[fixture.second]['mapping']['bodies'][shared]['text']
        dialog = open_source(fixture.second, shared)
        replace_source(dialog, 'return result;', 'return result + 1;')
        close_source(dialog)
        conflicting = d.pending()
        owner_save(False)
        assert d.pending() == conflicting and checkpoint.read_bytes() == baseline
        fixture.unchanged()
        dialog = open_source(fixture.second, shared)
        assert 'return result + 1;' in dialog.locator('[data-code-source]').input_value()
        close_source(dialog, accept=False)
        f.owner().locator('[data-own-functions-toggle]').press('Control+z')
        assert d.pending() == agreed
        f.checked('mixed input/return reuse is explicit; Cancel and inconsistent body Save preserve all inputs and originals')

        restart(1)
        assert d.pending() == agreed
        owner_save(True)
        assert not d.pending()
        fixture.unchanged()
        saved = checkpoint.read_bytes()
        rows = saved_changes(checkpoint)
        group = rows[fixture.owner]['atomicEditGroup']
        assert set(fixture.functions + [first, second, shared]) <= set(group)
        assert group.count(shared) == 1
        receipt = rows[fixture.owner]['slotSaveReceipt']
        plans = receipt['declaration']['changes']
        assert [plan['mapping']['bodies'][shared]['text'] for plan in plans] == [rows[shared]['draft']] * 2
        assert rows[shared]['draft'].replace('\r\n', '\n').strip() == authored
        assert set(fixture.paths.values()) <= receipt['readGuards'].keys()
        restart(2)
        assert checkpoint.read_bytes() == saved and not d.pending()
        review = d.review()
        review.locator('[data-reject]').click()
        expect(review).to_have_count(0)
        assert saved_changes(checkpoint) == rows
        fixture.unchanged()
        review = d.review()
        assert {unit['id'] for unit in f.state()['review']['units']} == set(group)
        caller_path = f.project / fixture.paths[shared]
        original_bytes = caller_path.read_bytes()
        peer_bytes = original_bytes + b'// concurrent caller edit\r\n'
        caller_path.write_bytes(peer_bytes)
        try:
            assert confirm(review) is False
            assert caller_path.read_bytes() == peer_bytes
            assert saved_changes(checkpoint) == rows
            fixture.unchanged({fixture.paths[shared]})
        finally:
            caller_path.write_bytes(original_bytes)
        f.checked('a physical caller edit after Review is preserved and Confirm publishes none of the group')

        if review.is_visible():
            review.locator('[data-reject]').click()
        assert confirm(d.review())
        restart(3)
        fixture.execute(104, 'confirmed-shared-caller')
        changed = {
            'FreeInfo.celem', 'MainBody.celem', *fixture.paths.values(),
            *[f'elements/{fn.split("::")[1]}.celem' for fn in fixture.functions],
            *[f'{fn.split("::")[1]}Body.celem' for fn in fixture.functions],
        }
        fixture.unchanged(changed)
        f.checked('cold before and after Save, immutable originals until Confirm, one shared caller and exact output 104')
        assert not f.errors and not f.external, (f.errors, f.external)
        f.browser.close()
finally:
    (f.case / 'checks.json').write_text(json.dumps(f.checks, ensure_ascii=False, indent=2))
    f.stop()
