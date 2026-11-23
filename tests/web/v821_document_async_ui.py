"""Exercise explicit Logic Code Task and completion routing in a real editor."""
import ast
import copy
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

import v666_root_execution_fixture as t

f = t.f
assert t.out_mode and not t.data_mode
sources = {
    'work': ('Work.node.json', 'System.Console.WriteLine("task:sync");workResult=checked((int)amount*10);return Result.None;'),
    'completed': ('Completed.node.json', 'System.Console.WriteLine("completed:"+value);'),
    'decision': ('Decision.node.json', 'System.Console.WriteLine("decision:"+value);'),
}
task = ('System.Console.WriteLine("task:start");\n'
        'await global::System.Threading.Tasks.Task.Yield();\n'
        'workResult=checked((int)amount*10);System.Console.WriteLine("task:done");return Result.None;')

for file, names in [
    ('v821_function_document_ui.py', {'panel', 'doc', 'pending', 'open_document', 'restart', 'review'}),
    ('v821_document_call_first_branch_ui.py', {'edit_body'}),
]:
    helper = Path(__file__).with_name(file)
    functions = [node for node in ast.parse(helper.read_text()).body
                 if isinstance(node, ast.FunctionDef) and node.name in names]
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(helper), 'exec'), globals())


def seed():
    root = copy.deepcopy(t.root)
    root['entry'] = 'work'
    publish = next(edge for edge in root['edges'] if edge['port'] == 'case:positive')
    old_success = publish['to']
    publish['to'] = 'decision'
    root['edges'] += [t.edge('work', 'choose'), t.edge('completed', 'return:work'),
                      t.edge('decision', old_success)]
    for id_, args, values, owner in [
        ('work', [{'name': 'amount', 'type': 'long'}, {'name': 'workResult', 'type': 'int', 'mode': 'out'}],
         {'amount': {'input': 'amount'}}, None),
        ('completed', [{'name': 'value', 'type': 'int'}],
         {'value': {'node': 'work', 'output': 'workResult'}}, 'work'),
        ('decision', [{'name': 'value', 'type': 'int'}],
         {'value': {'node': 'choose', 'output': 'result'}}, 'choose'),
    ]:
        root['nodes'].append({'id': id_, 'kind': 'code', 'control': 'next', 'intent': id_,
                              'signature': {'args': args, 'return': 'void'}, 'arguments': values,
                              'implementation': sources[id_][0], **({'branchOwner': owner} if owner else {})})
    work = next(row for row in root['nodes'] if row['id'] == 'work')
    work['control'] = 'switch'
    work['executionEnum'] = {'primary': 'next', 'members': [{'id': 'next', 'name': 'None', 'value': 0}]}
    defs = f.metadata('featureBlueprintNodes', featureSource=t.function, graph=root)
    assert defs['state'] == 'node-definitions', defs
    for id_, (file, source) in sources.items():
        definition = next(row for row in defs['nodes'] if row['id'] == id_)
        (f.project/file).write_text(json.dumps(dict(schema=1, node=id_, definitionHash=definition['definitionHash'],
                                                  source=source)))
    (f.project/'Flow.graph.json').write_text(json.dumps(root))
    t.physical = {path: path.read_bytes() for path in f.project.iterdir() if path.is_file()}
    return root


def mode(id_):
    return doc().locator(f'[data-document-async-mode="{id_}"]')


def toggle(id_, cancel=False):
    mode(id_).click()
    dialog = f.page.get_by_role('dialog', name='기능 실행 방식', exact=True)
    dialog.locator('[data-document-async-cancel]' if cancel else '[data-document-async-apply]').click()
    expect(dialog).to_be_hidden()


def choose_completion(cancel=False):
    doc().locator('[data-document-branch="completion"][data-document-owner="work"]').click()
    doc().locator('[data-document-branch-target="completion"][data-document-owner="work"]').click()
    dialog = f.page.get_by_role('dialog', name='완료 시 실행 대상 선택', exact=True)
    expect(dialog.locator('[data-document-route-choice] option')).to_have_count(2)
    expect(dialog.locator('[data-route-apply]')).to_be_disabled()
    dialog.locator('[data-document-route-choice]').select_option('completed')
    dialog.locator('[data-route-cancel]' if cancel else '[data-route-apply]').click()
    expect(dialog).to_be_hidden()


def save():
    panel().locator('[data-bp-save]').click()
    expect(panel().locator('.bp-status')).to_have_text('저장됨', timeout=90000)
    assert not pending()
    f.idle()


try:
    root = seed()
    t.build('logic-async-before', 10, 'task:sync\ncallee:1\ndecision:10\nafter:10')
    f.start(0)
    f.invoke('select', {'id': t.feature})
    f.invoke('saveDraft', {})
    checkpoint = next(f.project.glob('.confectory/edit-workspaces/*/draft.json'))
    before = checkpoint.read_bytes()
    with sync_playwright() as pw:
        expect.set_options(timeout=30000)
        f.browser = pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 1800, 'height': 1400})
        open_document()
        expect(mode('$entry')).to_have_text('실행 방식 · 동기')
        toggle('$entry', cancel=True)
        expect(mode('$entry')).to_be_focused()
        assert not pending() and checkpoint.read_bytes() == before
        toggle('work')  # Cannot promote a child while the function is synchronous.
        expect(mode('work')).to_have_text('실행 방식 · 동기')
        assert not pending() and checkpoint.read_bytes() == before
        toggle('$entry')
        expect(mode('$entry')).to_have_text('실행 방식 · 비동기')
        toggle('work')
        expect(mode('work')).to_have_text('실행 방식 · 비동기')
        toggle('work')
        expect(mode('work')).to_have_text('실행 방식 · 동기')
        doc().press('Control+z')
        expect(mode('work')).to_have_text('실행 방식 · 비동기')
        doc().press('Control+y')
        expect(mode('work')).to_have_text('실행 방식 · 동기')
        toggle('work')
        save()
        t.original()
        assert 'GRAPH_ASYNC_CALLER_REQUIRED' in json.dumps(t.read(t.caller)['diagnostics'])
        f.checked('Root and Task require explicit changes. Cancel/Undo/Redo preserve originals, and the synchronous caller reports the existing error.')

        restart(1)
        expect(mode('work')).to_have_text('실행 방식 · 비동기')
        saved = checkpoint.read_bytes()
        choose_completion(cancel=True)
        assert not pending() and checkpoint.read_bytes() == saved
        choose_completion()
        assert len(pending()) == 1 and pending()[0][1]['type'] == 'route:completion'
        completion = doc().locator('[data-document-panel="completion"]')
        expect(completion.locator('[data-document-cell="completed"]')).to_be_visible()
        doc().press('Control+z')
        expect(completion.locator('[data-document-cell="completed"]')).to_have_count(0)
        doc().press('Control+y')
        expect(completion.locator('[data-document-cell="completed"]')).to_be_visible()
        save()
        restart(2)
        doc().locator('[data-document-branch="completion"][data-document-owner="work"]').click()
        expect(doc().locator('[data-document-panel="completion"] [data-document-cell="completed"]')).to_be_visible()
        assert 'GRAPH_ASYNC_CALLER_REQUIRED' in json.dumps(t.read(t.caller)['diagnostics'])
        t.original()
        f.checked('Completion selects only the detached same-owner cell, keeps the port through restart and never promotes the caller.')

        panel().locator('[data-close]').first.click()
        # Current shell selection obtains the real Function entry via Browser.
        t.feature = f.n+'Main'
        open_document()
        expect(doc().locator('[data-document-cell="invoke"]')).to_be_visible()
        expect(mode('invoke')).to_have_count(0)
        expect(mode('$entry')).to_have_text('실행 방식 · 동기')
        toggle('$entry')
        save()
        t.original()
        review().locator('[data-reject]').click()
        t.original()
        done = review()
        done.locator('#confirm').click()
        expect(done).to_be_hidden(timeout=120000)
        f.idle()
        panel().locator('[data-close]').first.click()
        t.feature = t.impl.removesuffix('Body')
        open_document()
        doc().locator('[data-document-code="work"]').click()
        editor = f.page.locator('.bp-script-dialog')
        assert 'async global::System.Threading.Tasks.Task' in editor.locator('[data-code-source]').input_value()
        edit_body(editor, task)
        editor.locator('[data-code-save]').click()
        save()
        executable = review()
        executable.locator('#confirm').click()
        expect(executable).to_be_hidden(timeout=120000)
        f.idle()
        t.build('logic-async-confirmed', 10, 'task:start\ntask:done\ncompleted:10\ncallee:1\ndecision:10\nafter:10')
        result = json.loads((f.project/'Flow.graph.json').read_text())
        assert result['schema'] == root['schema'] and result['exits'] == root['exits']
        assert [edge for edge in result['edges'] if edge['port'] != 'completion'] == root['edges']
        assert t.edge('work', 'completed', 'completion') in result['edges']
        for file in ['Flow.node.json', 'Completed.node.json', 'Decision.node.json', 'After.node.json']:
            path = f.project/file
            assert json.loads(path.read_text())['source'] == json.loads(t.physical[path])['source']
        restart(3)
        assert t.read()['diagnostics']['state'] == 'source-ready'
        assert t.read(t.caller)['diagnostics']['state'] == 'source-ready'
        assert not f.errors and not f.external, (f.errors, f.external)
        f.checked('After explicit caller conversion and Review/Confirm, real Task completion publishes the out value before the completion branch and remaining work.')
        f.browser.close()
finally:
    (f.case/'logic-async-checks.json').write_text(json.dumps(f.checks, ensure_ascii=False))
    f.stop()
print('V821_DOCUMENT_ASYNC', f.case, flush=True)
