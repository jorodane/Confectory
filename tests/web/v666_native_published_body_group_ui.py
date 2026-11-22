"""Re-edit both published C# bodies of a connected nominal input/return pair."""
import json
import time

from playwright.sync_api import expect, sync_playwright

import v666_native_io_mixed_fixture as fixture


fixture.io_case = 'value'
f, d = fixture.f, fixture.c.x.d


def wait_reply(mark, endpoint, action=None):
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        requests = {
            entry['invoke']['requestId']: entry['invoke']['input']
            for entry in f.traffic[mark:]
            if entry.get('invoke', {}).get('endpoint') == endpoint
            and (action is None or entry['invoke']['input'].get('action') == action)
        }
        for entry in f.traffic[mark:]:
            reply = entry.get('result', {})
            if reply.get('requestId') in requests and reply.get('error', {}).get('code') != 'stale_revision':
                f.idle()
                return requests[reply['requestId']], reply
        f.page.wait_for_timeout(25)
    raise AssertionError(f'No {endpoint}/{action} reply in {f.case}')


def save(accepted):
    mark = len(f.traffic)
    f.owner().locator('[data-element-action=save]').click()
    call, reply = wait_reply(mark, 'blueprint', 'applySlots')
    assert reply['ok'] == accepted, (reply, f.state().get('logs'))
    return call['declaration']


def confirm(review):
    if review.locator('[data-review-advanced]').count():
        review.locator('[data-review-advanced]').click()
        if review.locator('[data-advanced-reviewed]').count():
            review.locator('[data-advanced-reviewed]').check()
    mark = len(f.traffic)
    review.locator('#confirm').click()
    _, reply = wait_reply(mark, 'confirmGroup')
    assert reply['ok'], reply
    return reply['result']['sourceConfirmed']


def edit(function, body, before, after, accept=True):
    row = f.owner().locator(f'[data-inline-method="{function}"]')
    row.locator('[data-function-write-direct],[data-function-edit]').first.click()
    f.page.locator(f'[data-information-body="{body}"]').click()
    dialog = f.page.locator('.bp-script-dialog')
    source = dialog.locator('[data-code-source]')
    assert before in source.input_value(), source.input_value()
    source.evaluate('''(el, text) => {
        const from = el.value.indexOf(text);
        el.focus();
        el.setSelectionRange(from, from + text.length);
    }''', before)
    f.page.keyboard.insert_text(after)
    dialog.locator('[data-code-save]' if accept else '[data-code-cancel]').click()
    expect(dialog).to_have_count(0)
    f.idle()


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


def saved_rows(checkpoint):
    return {
        row['id']: {key: value for key, value in row.items() if key != 'revision'}
        for row in json.loads(checkpoint.read_bytes())['changes']
    }


def seed_published_contracts():
    f.start(0)
    f.invoke('select', {'id': fixture.owner})
    f.invoke('saveDraft', {})
    cp = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    f.invoke('blueprint', fixture.apply_request())
    ids = fixture.verify(cp)
    f.invoke('reviewGroup', {'ids': ids, 'target': 'portable'})
    review = f.state()['review']
    assert review['status'] == 'ready', review
    assert f.invoke('confirmGroup', {'ids': ids, 'token': review['token']})['result']['result']['sourceConfirmed']
    fixture.execute(73, 'published-nominal-contracts')
    f.stop()


try:
    seed_published_contracts()
    sources = {path: (f.project / path).read_bytes() for path in fixture.snapshot}

    def originals(except_paths=()):
        for path, original in sources.items():
            if path not in except_paths:
                assert (f.project / path).read_bytes() == original, path

    f.start(1)
    f.invoke('select', {'id': fixture.owner})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    baseline = checkpoint.read_bytes()
    first, second = fixture.functions
    first_body, second_body = fixture.bodies[first], fixture.bodies[second]
    with sync_playwright() as playwright:
        expect.set_options(timeout=60_000)
        f.browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        open_editor()
        edit(first, first_body, 'Count=result;', 'Count=result+99;', accept=False)
        assert not d.pending() and checkpoint.read_bytes() == baseline
        edit(first, first_body, 'Count=result;', 'Count=result+4;')
        edit(second, second_body, 'Count+2);', 'Count+5);')
        wanted = d.pending()
        edits = [value for _, value in wanted]
        scopes = [value['nativeTypes']['$function:' + value['id']]['sources'] for value in edits]
        assert len(scopes) == 2 and scopes[0] == scopes[1]

        # The first implementation is also visible from the callee's editor.
        # Two different texts for it are not two disjoint body-only edits.
        edit(second, first_body, 'Count=result;', 'Count=result+99;')
        conflicting = d.pending()
        rejected = save(False)
        assert all('nativeTypes' in row for row in rejected['changes'])
        assert d.pending() == conflicting and checkpoint.read_bytes() == baseline
        originals()
        f.owner().locator('[data-own-functions-toggle]').press('Control+z')
        assert d.pending() == wanted
        f.checked('Cancel and conflicting source plans retain the entire staged input and original checkpoint')

        restart(2)
        assert d.pending() == wanted
        request = save(True)
        assert not d.pending()
        originals()
        rows = saved_rows(checkpoint)
        group = rows[fixture.owner]['atomicEditGroup']
        receipt = rows[fixture.owner]['slotSaveReceipt']
        assert set([first, second, first_body, second_body]) <= set(group)
        assert 'Count=result+4;' in rows[first_body]['draft'] and 'Count+5);' in rows[second_body]['draft']
        assert receipt['version'] == 3 and 'nativeBodyContexts' not in receipt
        assert receipt['declaration'] == request
        assert sum('nativeTypes' in row for row in request['changes']) == 1
        proof = next(row['nativeTypes'] for row in request['changes'] if 'nativeTypes' in row)
        assert receipt['nativeTypeProofs'] == proof
        assert proof['$function:' + request['changes'][0]['id']]['sources'] == scopes[0]
        expected_reads = {source['path']: source['source'] for item in proof.values() for source in item['sources'].values()}
        assert {read['path']: read['hash'] for read in receipt['nativeTypeReads']} == expected_reads
        assert set(fixture.paths.values()) | {'Leaf.celem', 'Payload.celem'} <= receipt['readGuards'].keys()
        f.checked('one existing v3 receipt retains both body changes and the complete original owned and registered type read scopes')

        restart(3)
        assert saved_rows(checkpoint) == rows and not d.pending()
        review = d.review()
        review.locator('[data-reject]').click()
        expect(review).to_have_count(0)
        assert saved_rows(checkpoint) == rows
        review = d.review()
        path = fixture.paths[fixture.callers[first]]
        peer = sources[path] + b'// concurrent caller change\r\n'
        (f.project / path).write_bytes(peer)
        try:
            assert confirm(review) is False
            assert (f.project / path).read_bytes() == peer and saved_rows(checkpoint) == rows
            originals({path})
        finally:
            (f.project / path).write_bytes(sources[path])
        f.checked('Review cancellation and a changed caller at Confirm leave every saved body and dependency intact')

        if review.is_visible():
            review.locator('[data-reject]').click()
        assert confirm(d.review())
        restart(4)
        fixture.execute(80, 'revised-connected-bodies')
        originals({fixture.paths[first_body], fixture.paths[second_body]})
        f.checked('both published signatures and the calling chain stay byte-identical; the reopened build runs 80')
        assert not f.errors and not f.external, (f.errors, f.external)
        f.browser.close()
finally:
    (f.case / 'checks.json').write_text(json.dumps(f.checks, ensure_ascii=False, indent=2))
    f.stop()
