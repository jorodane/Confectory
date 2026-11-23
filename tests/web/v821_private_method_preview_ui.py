"""Preview a directly owned methods frame, including at depth two."""
import copy
import hashlib
import json
import shutil
import sys
import time

from playwright.sync_api import expect, sync_playwright

import v666_node_internal_api as fixture
from v821_internal_flow_document_ui import document, open_feature, panel, restart, tab

f = fixture.f
root_id = fixture.graph
frames = ('first', 'second')
names = ('AlphaOnly', 'BetaOnly')
mode = sys.argv[3] if len(sys.argv) > 3 else 'direct'
assert mode in {'direct', 'alias', 'nested', 'nested-alias', 'parent', 'parent-shared-leaf'}
parent = mode.startswith('parent')
nested = parent or mode.startswith('nested')
alias = mode.endswith('alias')


def frame_path(frame):
    return f'{frame}/methods' if nested else frame


def frame_id(frame):
    return f'{root_id}/graph:' + frame_path(frame).replace('/', '/graph:')


def prepare_project():
    graph = copy.deepcopy(fixture.g)
    graph['profile'] = 'sync-acyclic-nested-v1'
    graph['entry'] = frames[0]
    graph['nodes'] = []
    graph['edges'] = [{'from': frames[0], 'port': 'next', 'to': frames[1]},
                      {'from': frames[1], 'port': 'next', 'to': 'exit:return'}]
    graph['exits'] = {'return': {'node': frames[1]}}
    sources = {}
    for index, name in enumerate(frames):
        child = copy.deepcopy(fixture.g)
        del child['feature'], child['contractHash']
        leaf = child['nodes'][0]
        leaf['implementation'] = f'{name}.node.json'
        signature = leaf['signature']
        marker = names[index]
        sources[f'{frame_path(name)}/calculate'] = (
            leaf['implementation'], f'return {marker}(amount);',
            f'private static long {marker}(long value) => value + {10 + index};')
        if nested:
            finish = dict(leaf, id='finish', implementation=f'{name}.finish.node.json',
                          arguments={'amount': {'node': 'calculate'}})
            child['nodes'].append(finish)
            child['edges'] = [{'from': 'calculate', 'port': 'next', 'to': 'finish'},
                              {'from': 'finish', 'port': 'next', 'to': 'exit:return'}]
            child['exits'] = {'return': {'node': 'finish'}}
            sources[f'{frame_path(name)}/finish'] = (finish['implementation'], f'return {marker}Finish(amount);',
                                                    f'private static long {marker}Finish(long value) => value;')
            ancestor = f'{name}.ancestor.node.json'
            child = {'schema': 1, 'profile': 'sync-acyclic-nested-v1', 'entry': 'methods',
                     'nodes': [{'id': 'methods', 'kind': 'graph', 'control': 'next', 'intent': 'Methods',
                                'signature': signature, 'arguments': {'amount': {'input': 'amount'}}, 'graph': child},
                               {'id': 'trace', 'kind': 'code', 'control': 'next', 'intent': 'Ancestor trace',
                                'signature': {'args': [], 'return': 'void'}, 'arguments': {}, 'implementation': ancestor}],
                     'edges': [{'from': 'methods', 'port': 'next', 'to': 'trace'},
                               {'from': 'trace', 'port': 'next', 'to': 'exit:return'}],
                     'exits': {'return': {'node': 'methods'}}}
            sources[f'{name}/trace'] = (ancestor, f'System.Console.WriteLine("AncestorOnly_{name}");', '')
            if parent:
                extra_file = f'{name}.extra.node.json'
                extra = dict(leaf, implementation=extra_file)
                extra_graph = {'schema': 1, 'profile': 'sync-acyclic-methods-v1', 'entry': 'calculate',
                               'nodes': [extra], 'edges': [{'from': 'calculate', 'port': 'next', 'to': 'exit:return'}],
                               'exits': {'return': {'node': 'calculate'}}}
                child['nodes'].insert(1, {'id': 'extra', 'kind': 'graph', 'control': 'next', 'intent': 'Extra method',
                                          'signature': signature, 'arguments': {'amount': {'node': 'methods'}},
                                          'graph': extra_graph})
                child['edges'][0]['to'] = 'extra'
                child['edges'].insert(1, {'from': 'extra', 'port': 'next', 'to': 'trace'})
                child['exits'] = {'return': {'node': 'extra'}}
                sources[f'{name}/extra/calculate'] = (extra_file, f'return {marker}Extra(amount);',
                                                     f'private static long {marker}Extra(long value) => value;')
        graph['nodes'].append({'id': name, 'intent': name, 'kind': 'graph', 'control': 'next',
                               'graph': child, 'signature': signature,
                               'arguments': {'amount': {'input': 'amount'} if index == 0 else {'node': frames[0]}}})
    context = {'implementation': fixture.impl, 'feature': fixture.feature,
               'signature': graph['nodes'][0]['signature'], 'imports': {}}
    definitions = f.metadata('featureBlueprintNodes', featureSource=fixture.function, graph=graph,
                             implementationContext=context, bodyTarget='common')
    rows = {row['id']: row for row in definitions['nestedNodes']}
    for path, (filename, source, helpers) in sources.items():
        record = dict(fixture.record, node=path.split('/')[-1], definitionHash=rows[path]['definitionHash'], source=source,
                      helpers=helpers)
        (f.project / filename).write_text(json.dumps(record))
    (f.project / 'Flow.graph.json').write_text(json.dumps(graph))
    if alias:
        impl = f.project / 'FlowBody.celem'
        impl.write_text(impl.read_text().replace('blueprint common "Flow.graph.json";',
                                                 'blueprint common "Flow.graph.json"; blueprint windows "Flow.graph.json";'))
    if mode == 'parent-shared-leaf':
        # Give another registered body a distinct graph and the same code files.
        (f.project / 'Alternate.graph.json').write_text(json.dumps(graph))
        impl = f.project / 'FlowBody.celem'
        impl.write_text(impl.read_text().replace('blueprint common "Flow.graph.json";',
                                                 'blueprint common "Flow.graph.json"; blueprint windows "Alternate.graph.json";'))
    fixture.physical = {path: path.read_bytes() for path in f.project.iterdir() if path.is_file()}


def enter(frame):
    document().locator(f'[data-document-internal="{frame}"]').click()
    if nested:
        expect(document().locator('[data-document-cell="methods"]')).to_be_visible()
        if frame == 'first':
            tab('블루프린트 보기').click()
            panel().locator('[data-bp-node="methods"] [data-internal-flow]').click()
        else:
            document().locator('[data-document-internal="methods"]').click()
    expect(document().locator('[data-document-cell="calculate"]')).to_be_visible()


def go_root():
    panel().locator('.bp-breadcrumbs button').first.click()
    expect(document().locator('[data-document-cell="first"]')).to_be_visible()


def native():
    tab('네이티브 미리보기').click()
    return panel().locator('.function-native-preview')


def shown(view, frame, result):
    expect(view.locator('[role=status]')).to_contain_text('생성됨')
    code = result['diagnostics']
    assert code['assembledPath'] == frame
    for key in ('body', 'members'):
        assert view.locator(f'[data-native-{key}]').text_content() == code[key]
    assert view.locator('textarea,input,[contenteditable=true]').count() == 0


def assert_empty(view, message):
    expect(view.locator('[role=status]')).to_contain_text(message)
    for key in ('body', 'members'):
        assert not view.locator(f'[data-native-{key}]').text_content()


def open_original_and_cancel():
    document().locator('[data-document-code="calculate"]').click()
    dialog = f.page.locator('.bp-script-dialog')
    expect(dialog.locator('[data-code-region="body"]')).to_contain_text(f'return {names[0]}(amount);')
    expect(dialog.locator('[data-code-source]')).to_be_editable()
    dialog.locator('[data-code-cancel]').click()
    expect(dialog).to_be_hidden()


def request(frame, data):
    return dict(action='nativePreview', id=frame_id(frame), documentFrame=data['documentFramePreviewBinding'],
                sourceProof=fixture.proof(data), checkpointHash=data['checkpointHash'])


def preview(options, success=True):
    return f.invoke('blueprint', options, success)['result'].get('result')


def history():
    return f.invoke('draftHistory', {'action': 'inspect'})['result']['result']


def enter_parent(frame):
    document().locator(f'[data-document-internal="{frame}"]').click()
    expect(document().locator('[data-document-cell="methods"]')).to_be_visible()


def parent_request(frame):
    identity = f'{root_id}/graph:{frame}'
    return dict(request(frame, fixture.read(identity)), id=identity)


def check_parent(copy_project, other_files, checkpoint_before, history_before):
    enter_parent('first')
    view = native()
    if mode == 'parent-shared-leaf':
        assert not fixture.read(f'{root_id}/graph:first').get('documentFramePreviewBinding')
        assert_empty(view, '지원하지')
        assert fixture.checkpoint() == checkpoint_before and history() == history_before
        fixture.original()
        f.checked('A separate graph registered with the same code files cannot supply a parent preview')
        return

    expect(view.locator('[role=status]')).to_contain_text('생성됨', timeout=12000)
    first_options = parent_request('first')
    first, second = (preview(parent_request(frame)) for frame in frames)
    full = preview({'action': 'nativePreview', 'id': root_id})['diagnostics']
    for index, result in enumerate((first, second)):
        frame, sibling = frames[index], frames[1 - index]
        code = result['diagnostics']
        child = preview(request(frame, fixture.read(frame_id(frame))))['diagnostics']
        extra_id = f'{root_id}/graph:{frame}/graph:extra'
        extra = preview(dict(request(frame, fixture.read(extra_id)), id=extra_id))['diagnostics']
        assert code['body'] in full['body'] and child['body'] in code['body'] and extra['body'] in code['body']
        assert code['members'] == child['members'] + extra['members'] and code['members'] in full['members']
        assert names[index] + 'Extra' not in child['members']
        assert f'AncestorOnly_{frame}' in code['body']
        assert f'AncestorOnly_{sibling}' not in json.dumps(result) and names[1 - index] not in json.dumps(result)
        for member in (names[index], names[index] + 'Finish', names[index] + 'Extra'):
            assert f'return {member}(amount);' in code['members'] and f'private static long {member}(' in code['members']
        assert hashlib.sha256((code['body'] + code['members']).encode()).hexdigest() == code['bodyHash']
        assert not result['sourceWritten'] and not result['compiled']
    shown(view, 'first', first)
    assert preview(dict(first_options, id=f'{root_id}/graph:second'), False) is None
    assert preview(dict(first_options, id=frame_id('first')), False) is None
    assert preview(dict(first_options, sourceProof='[]'), False) is None
    assert preview(dict(first_options, checkpointHash='0' * 64), False) is None

    tab('논리 코드').click()
    tab('블루프린트 보기').click()
    panel().locator('[data-bp-node="methods"] [data-internal-flow]').click()
    expect(document().locator('[data-document-cell="calculate"]')).to_be_visible()
    child = preview(request('first', fixture.read(frame_id('first'))))
    shown(native(), frame_path('first'), child)
    panel().locator('.bp-breadcrumbs button').nth(1).click()
    expect(tab('블루프린트 보기')).to_have_attribute('aria-selected', 'true')
    shown(native(), 'first', first)
    f.checked('Parent and child previews match exact emitter scopes through both views and breadcrumb return')

    changed = f.project / 'first.finish.node.json'
    original = changed.read_bytes()
    changed.write_bytes(original + b' ')
    try:
        panel().locator('[data-native-refresh]').click()
        assert_empty(panel().locator('.function-native-preview'), '실패')
    finally:
        changed.write_bytes(original)
    tab('논리 코드').click()
    go_root()
    enter_parent('second')
    shown(native(), 'second', second)
    assert fixture.checkpoint() == checkpoint_before and history() == history_before
    fixture.original()
    f.checked('Stale descendant sources clear both panes; the same-ID sibling has an independent result')

    f.env['CONFECTORY_WEB_PROJECT'] = str(copy_project / 'project.cproj')
    restart(1)
    f.invoke('select', {'id': fixture.feature})
    assert preview(first_options, False) is None
    fresh = parent_request('first')
    old_binding, new_binding = first_options['documentFrame'], fresh['documentFrame']
    assert old_binding['workspace'] != new_binding['workspace']
    assert dict(old_binding, workspace=new_binding['workspace']) == new_binding
    assert preview(dict(fresh, documentFrame=old_binding), False) is None
    open_feature('first')
    enter_parent('first')
    shown(native(), 'first', preview(fresh))
    assert all(path.read_bytes() == raw for path, raw in other_files.items())
    f.env['CONFECTORY_WEB_PROJECT'] = str(fixture.manifest)
    restart(2)
    shown(panel().locator('.function-native-preview'), 'second', second)
    assert not f.pending()['blueprint']
    assert fixture.checkpoint() == checkpoint_before and history() == history_before
    fixture.original()
    fixture.build('parent-method-preview-unchanged', 24)
    assert not f.errors and not f.external, (f.errors, f.external)
    f.checked('Project switching keeps the bound scope and existing originals, checkpoint, history and return value 24')


def run():
    prepare_project()
    copy_project = f.case / 'same graph different project'
    shutil.copytree(f.project, copy_project)
    other_files = {path: path.read_bytes() for path in copy_project.iterdir() if path.is_file()}
    f.start(0)
    f.invoke('select', {'id': fixture.feature})
    f.invoke('saveDraft', {})
    checkpoint_before = fixture.checkpoint()
    history_before = history()

    with sync_playwright() as playwright:
        expect.set_options(timeout=60000)
        f.browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        f.page = f.setup()
        f.page.set_viewport_size({'width': 1800, 'height': 1400})
        open_feature('first')
        if parent:
            check_parent(copy_project, other_files, checkpoint_before, history_before)
            f.browser.close()
            return
        selected = fixture.read(frame_id('first'))
        enter('first')
        open_original_and_cancel()
        view = native()
        if alias:
            assert 'documentFramePreviewBinding' not in selected
            assert selected['documentFrameOrderBinding'] is None
            assert_empty(view, '지원하지')
            fixture.original()
            assert fixture.checkpoint() == checkpoint_before and history() == history_before
            f.checked('Shared physical graph remains unavailable in the actual preview')
            return
        expect(view.locator('[role=status]')).to_contain_text('생성됨', timeout=12000)
        options = request('first', selected)
        order_binding = selected['documentFrameOrderBinding']
        assert order_binding is not None
        assert order_binding['sources']
        frame_binding = {key: value for key, value in order_binding.items() if key != 'sources'}
        assert dict(frame_binding, workspace=options['documentFrame']['workspace']) == options['documentFrame']
        assert preview(dict(options, documentFrame=order_binding), False) is None
        first = preview(options)
        second = preview(request('second', fixture.read(frame_id('second'))))
        full = preview({'action': 'nativePreview', 'id': root_id})['diagnostics']
        if nested:
            assert all(f'AncestorOnly_{frame}' in full['body'] for frame in frames)
        for index, result in enumerate((first, second)):
            code = result['diagnostics']
            assert code['body'] in full['body'] and code['members'] in full['members']
            assert names[index] in code['members'] and names[1-index] not in json.dumps(result)
            if nested:
                assert f'return {names[index]}(amount);' in code['members']
                assert f'return {names[index]}Finish(amount);' in code['members']
                assert f'private static long {names[index]}Finish(' in code['members']
                assert 'AncestorOnly_' not in json.dumps(result)
            assert hashlib.sha256((code['body'] + code['members']).encode()).hexdigest() == code['bodyHash']
            assert not result['sourceWritten'] and not result['compiled']
        shown(view, frame_path('first'), first)
        assert not f.pending()['blueprint']
        fixture.original()
        assert fixture.checkpoint() == checkpoint_before and history() == history_before
        f.checked('Editable private body and read-only preview show the exact selected emitter body and helper members')

        assert preview(dict(options, id=frame_id('second')), False) is None
        if nested:
            assert preview(dict(options, id=f'{root_id}/graph:first'), False) is None
            assert preview(dict(options, documentFrame=dict(options['documentFrame'], path='methods')), False) is None
        assert preview(dict(options, checkpointHash='0' * 64), False) is None
        assert preview(dict(options, sourceProof='[]'), False) is None
        changed = f.project / 'second.node.json'
        raw = changed.read_bytes()
        changed.write_bytes(raw + b' ')
        try:
            view.locator('[data-native-refresh]').click()
            assert_empty(view, '실패')
        finally:
            changed.write_bytes(raw)

        tab('논리 코드').click()
        if nested:
            panel().locator('.bp-breadcrumbs button').nth(1).click()
            expect(tab('블루프린트 보기')).to_have_attribute('aria-selected', 'true')
            expect(panel().locator('[data-bp-node="methods"]')).to_be_visible()
        go_root()
        enter('second')
        shown(native(), frame_path('second'), second)
        f.checked('Exact scope, checkpoint and full source observations reject stale requests and clear both code panes')

        requests = set()
        held = {}

        def hold_preview(route):
            body = route.request.post_data_json
            if body.get('op') == 'invoke' and body.get('endpoint') == 'blueprint' and body['input'].get('action') == 'nativePreview':
                requests.add(body['requestId'])
            response = route.fetch()
            payload = response.json()
            if not held and any(row.get('requestId') in requests for row in payload.get('results', [])):
                held.update(route=route, response=response)
            else:
                route.fulfill(response=response)

        f.page.route('**/api/request', hold_preview)
        panel().locator('[data-native-refresh]').click()
        deadline = time.monotonic() + 60
        while not held and time.monotonic() < deadline:
            f.page.wait_for_timeout(30)
        assert held, 'The real preview response never arrived'
        tab('논리 코드').click()
        name = document().locator('[data-document-name="calculate"]')
        name.fill('Keep pending method title')
        document().locator('.fd-document-title').click()
        view = native()
        assert_empty(view, '저장하지 않은 입력')
        held['route'].fulfill(response=held['response'])
        f.page.unroute_all(behavior='wait')
        f.idle()
        assert_empty(view, '저장하지 않은 입력')
        pending = f.pending()['blueprint']
        assert len(pending) == 1 and pending[0][1]['text'] == 'Keep pending method title'
        fixture.original()
        assert fixture.checkpoint() == checkpoint_before and history() == history_before
        f.checked('Leaving preview and changing a private input discards the late result and retains the input')

        f.env['CONFECTORY_WEB_PROJECT'] = str(copy_project / 'project.cproj')
        restart(1)
        f.invoke('select', {'id': fixture.feature})
        assert preview(options, False) is None
        assert not f.pending()['blueprint']
        open_feature('first')
        enter('first')
        current_options = request('first', fixture.read(frame_id('first')))
        old_binding, current_binding = options['documentFrame'], current_options['documentFrame']
        assert dict(old_binding, workspace=current_binding['workspace']) == current_binding
        assert old_binding['workspace'] != current_binding['workspace']
        assert preview(dict(current_options, documentFrame=old_binding), False) is None
        current = preview(current_options)
        shown(native(), frame_path('first'), current)
        assert all(path.read_bytes() == raw for path, raw in other_files.items())

        f.env['CONFECTORY_WEB_PROJECT'] = str(fixture.manifest)
        restart(2)
        assert_empty(panel().locator('.function-native-preview'), '저장하지 않은 입력')
        assert f.pending()['blueprint'] == pending
        assert fixture.checkpoint() == checkpoint_before
        fixture.original()
        fixture.build('private-method-preview-unchanged', 24)
        assert not f.errors and not f.external, (f.errors, f.external)
        f.checked('Another project with the same IDs uses its own observation; returning restores only the original private draft')
        f.browser.close()


if __name__ == '__main__':
    print('Isolated fixture:', f.case, flush=True)
    try:
        run()
    finally:
        f.stop()
