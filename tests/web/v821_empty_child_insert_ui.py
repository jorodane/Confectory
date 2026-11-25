"""First action in an executable empty void child, through the actual editor."""
import ast
import copy
import json
from pathlib import Path
import sys
import uuid

from playwright.sync_api import expect, sync_playwright

# Reuse the owned nested frame fixture, not its order test body.
fixture = Path(__file__).with_name('v821_frame_structure_ui.py')
setup = ast.parse(fixture.read_text()).body
exec(compile(ast.Module(body=setup[:next(i for i, n in enumerate(setup) if isinstance(n, ast.Try))],
                        type_ignores=[]), str(fixture), 'exec'), globals())
helper = Path(__file__).with_name('v821_child_insert_ui.py')
edit = next(n for n in ast.parse(helper.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'edit_body')
exec(compile(ast.Module(body=[edit], type_ignores=[]), str(helper), 'exec'), globals())

frame_path = 'other/nest'
frame = t.graph + '/graph:other/graph:nest'
sibling = t.graph + '/graph:body/graph:nest'
empty = base['nodes'][1]['graph']['nodes'][0]['graph']
empty.update(entry='exit:return', nodes=[], edges=[], exits={'return': None})
graph_path = f.project / t.graph_file
graph_path.write_text(json.dumps(base, ensure_ascii=False))
# Only these synthetic files belonged to the fixture before making the existing
# void invocation empty. No new storage or executable meaning is introduced.
for name in ('Pair.peer.inner.node.json', 'Pair.peer.tail.node.json'):
    (f.project / name).unlink()
x.physical = {p: p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts}
original_output = 'body\ninside\nparent-tail\nafter\n10'
changed_output = 'body\ninside\nparent-tail\nfirst-child\nafter\n10'


def show_empty_path():
    if panel().locator('.bp-breadcrumbs button').count():
        root_view()
    for name in ('other', 'nest'):
        doc().locator(f'[data-document-internal="{name}"]').click()
        f.idle()
    expect(doc().locator('[data-document-cell="$entry"]')).to_be_visible()


def reopen(index):
    restart(index)
    show_empty_path()


def proposal(data, to='exit:return'):
    node = 'empty_probe'
    return dict(action='authorBatch', id=frame, attempt=uuid.uuid4().hex,
                documentFrame=copy.deepcopy(data['documentFrameOrderBinding']),
                sourceProof=x.proof(data), checkpointHash=data['checkpointHash'],
                edits=[dict(action='createNode', node=node, definition=dict(kind='code', control='next', intent='첫 동작', signature=signature())),
                       dict(action='rename', node=node, text='첫 동작'),
                       dict(action='intent', node=node, text='첫 동작'),
                       dict(action='source', node=node, text='return;'),
                       dict(action='entry', node='$entry', to=node),
                       dict(action='route', node=node, port='next', to=to)])


def guard_original():
    x.original()
    assert not [p for p in f.project.rglob('*.node.json') if p not in x.physical and '.confectory' not in p.parts]


try:
    x.build('empty-original', 10, original_output)
    f.start(0)
    f.invoke('select', dict(id=t.feature))
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    before = checkpoint.read_bytes()
    with sync_playwright() as pw:
        expect.set_options(timeout=45000)
        f.browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size(dict(width=1800, height=1400))
        open_document()
        show_empty_path()
        original = read(frame)
        assert original['entry'] == 'exit:return' and not original['nodes']
        assert original['documentFrameOrderBinding']['path'] == frame_path
        sibling_before = read(sibling)['nodes']
        add = doc().locator('[data-document-add="$entry"]')
        expect(add).to_be_enabled()
        f.invoke('blueprint', proposal(original, 'exit:wrong'), False)
        assert checkpoint.read_bytes() == before
        guard_original()
        add.click()
        f.idle()
        created, = [name for name in order() if name.startswith('cell_')]
        assert len(pending()) == 6
        doc().locator('.fd-document-title').click()
        doc().press('Control+z')
        assert created not in order() and not pending()
        doc().press('Control+y')
        assert created in order() and len(pending()) == 6
        edit_body(created, 'global::System.Console.WriteLine("first-child");\nreturn;')
        held = pending()
        guard_original()
        assert checkpoint.read_bytes() == before
        reopen(1)
        assert pending() == held and created in order()
        guard_original()
        f.checked('Existing empty child executes its original return; actual first insertion and local Undo/Redo survive cold local input restoration')

        leaf = f.project / 'Pair.body.inner.node.json'
        raw = leaf.read_bytes()
        leaf.write_bytes(raw + b' ')
        try:
            save()
            assert retained(held) and checkpoint.read_bytes() == before
            assert leaf.read_bytes() == raw + b' '
        finally:
            leaf.write_bytes(raw)
        guard_original()
        save()
        assert not pending()
        current = read(frame)
        assert current['entry'] == created and len(current['nodes']) == 1
        assert current['edges'] == [edge(created, 'exit:return')]
        assert read(sibling)['nodes'] == sibling_before
        made = current['nodes'][0]
        assert made['sourceId'] == frame.replace('/graph:', '/node:') + '/node:' + created
        saved = checkpoint.read_bytes()
        units = {row['id']: row for row in json.loads(saved)['changes']}
        assert set(units[t.graph]['propertyObservations']['sources']) == {*original['documentFrameOrderBinding']['sources'], made['sourceId']}
        assert not (f.project / units[made['sourceId']]['path']).exists()
        guard_original()
        history = f.invoke('draftHistory', dict(action='inspect'))['result']['result']
        assert history['boundary'] == 'OWNERSHIP_CHANGED' and not history['undo']['available'] and not history['redo']['available']
        reopen(2)
        assert created in order() and read(frame)['entry'] == created
        guard_original()
        f.checked('Sibling CAS protects Save; cold saved first child retains exact owner and return, original source and ownership history boundary')

        window = review()
        window.locator('[data-reject]').click()
        guard_original()
        window = review()
        saved = checkpoint.read_bytes()
        leaf.write_bytes(raw + b' ')
        try:
            window.locator('#confirm').click()
            f.idle()
            assert leaf.read_bytes() == raw + b' ' and checkpoint.read_bytes() == saved
            assert graph_path.read_bytes() == x.physical[graph_path]
            assert not (f.project / units[made['sourceId']]['path']).exists()
        finally:
            leaf.write_bytes(raw)
        if window.is_visible():
            window.locator('[data-reject]').click()
        window = review()
        window.locator('#confirm').click()
        expect(window).to_be_hidden(timeout=120000)
        f.idle()
        written = json.loads(graph_path.read_text())
        selected = written['nodes'][1]['graph']['nodes'][0]['graph']
        assert selected['entry'] == created and len(selected['nodes']) == 1 and selected['edges'] == [edge(created, 'exit:return')]
        selected.update(entry='exit:return', nodes=[], edges=[])
        assert written == base
        assert all(p.read_bytes() == raw for p, raw in x.physical.items() if p != graph_path)
        new_files = [p for p in f.project.rglob('*.node.json') if p not in x.physical and '.confectory' not in p.parts]
        assert len(new_files) == 1 and json.loads(new_files[0].read_text())['node'] == created
        x.build('empty-confirmed-first-child', 10, changed_output)
        reopen(3)
        assert created in order() and len(read(frame)['nodes']) == 1
        assert read(sibling)['nodes'] == sibling_before
        f.checked('Review cancel and stale sibling cannot publish; explicit Confirm creates exactly one source and executes it before the original return; cold reopen retains it')
        f.page.screenshot(path=str(f.case / 'empty-child-insert.png'))
        assert not f.errors and not f.external, (f.errors, f.external)
        f.browser.close()
finally:
    (f.case / 'empty-child-traffic.json').write_text(json.dumps(f.traffic, ensure_ascii=False))
    f.stop()
    print('V821_EMPTY_CHILD_INSERT', f.case, flush=True)
