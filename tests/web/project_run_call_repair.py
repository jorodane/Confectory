"""Repair a real stale imported call from the project's Run failure."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from playwright.sync_api import expect, sync_playwright

from editor_navigation import open_workspace_menu
from project_run_compile_recovery import editor, find_project_item
from editor_logic_workflow import review


NAMESPACE = 'RunRepair.Active'
PEER_NAMESPACE = 'RunRepair.Peer'
LIBRARY = 'RunRepair.Library'
LABEL = 'Shared caller label'
PEER_DRAFT = 'The other project retains this draft'


def metadata(repo, operation, **fields):
    host = repo / 'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'
    result = subprocess.run([os.environ['CONFECTORY_DOTNET'], str(host)],
                            input=json.dumps(dict(operation=operation, **fields)), text=True,
                            capture_output=True, check=True, timeout=30)
    reply = json.loads(result.stdout)
    assert reply['ok'], reply
    return reply['result']


def publish(pack, name, parameter, parameter_type='long'):
    target, provider = f'{LIBRARY}::{name}', f'{LIBRARY}::{name}Body'
    (pack / (name + '.celem')).write_text(
        f'function {target} ({parameter_type} {parameter}) -> long {{ provide {target} with {provider}; }}')
    (pack / (name + 'Body.celem')).write_text(
        f'implementation {provider} for {target} ({parameter_type} {parameter}) -> long {{ body common "{name}.csbody"; }}')
    (pack / (name + '.csbody')).write_text(f'return checked((long){parameter}) + 5L;')


def manifest(repo, project, elements, *, library=False, namespace=NAMESPACE, entry='Main'):
    registrations = ''.join(f'element {name} {kind} "{name}.celem"; ' for name, kind in elements)
    registry = f'registry {LIBRARY} "../library/pack.cpack"; dependency {LIBRARY} version "1"; ' if library else ''
    target = json.dumps(str(repo / 'targets/dotnet/pack.cpack'))
    (project / 'project.cpack').write_text(f'''project {namespace} version "1" {{ standalone true;
      entry {namespace}::{entry}; target linux Confectory.Build.DotNet::Linux;
      registry Confectory.Build.DotNet {target}; dependency Confectory.Build.DotNet version "0.1.0";
      {registry}{registrations} }}''')


def caller(repo, project, name, imported, pack):
    feature, implementation = f'{NAMESPACE}::{name}', f'{NAMESPACE}::{name}Body'
    callee = (pack / (imported + '.celem')).read_text()
    declaration = f'function {feature} (long seed) -> long {{ value editorName = "{LABEL}"; provide {feature} with {implementation}; }}'
    generated = metadata(repo, 'blueprintPrepareFeature', id=feature, text=f'function {feature} (long seed) -> long {{}}',
                         implementation=implementation, graphPath=f'{name}.graph.json', nodePath=f'{name}.node.json')
    graph = generated['graph']
    definitions = metadata(repo, 'featureBlueprintNodes', featureSource=declaration, graph=graph)
    record = {'schema': 1, 'node': 'body', 'source': 'return seed;',
              'definitionHash': next(row['definitionHash'] for row in definitions['nodes'] if row['id'] == 'body')}
    with_call = metadata(repo, 'blueprintPrepareCall', id=implementation, text=generated['implementation'], targetText=callee,
                         graph=graph, definition={'id': 'invoke', 'feature': f'{LIBRARY}::{imported}',
                                                  'control': 'next', 'intent': 'Existing synchronous import'})
    graph = with_call['graph']
    execution = {'primary': 'next', 'members': [{'id': 'next', 'name': 'NoBranch', 'value': 0}]}
    wrapper = metadata(repo, 'blueprintCallWrapper', functionText=callee, executionEnum=execution,
                       returnMapping='native-return-out-v1', source='return Result.NoBranch;')
    call = next(row for row in graph['nodes'] if row['id'] == 'invoke')
    call.update(control='switch', executionEnum=execution, arguments={'amount': {'input': 'seed'}},
                postCall={'mode': 'execution-enum', 'returnMapping': 'native-return-out-v1',
                          'contractHash': wrapper['contractHash'], 'source': wrapper['source'],
                          'helpers': 'private static long Retained(long value) { return value; }'})
    graph.update(profile='sync-acyclic-switch-v1', entry='invoke')
    graph['edges'].append({'from': 'invoke', 'port': 'next', 'to': 'body'})
    next(row for row in graph['nodes'] if row['id'] == 'body')['arguments'] = {'seed': {'node': 'invoke'}}
    (project / f'{name}.celem').write_text(declaration)
    (project / f'{name}Body.celem').write_text(with_call['implementation'])
    (project / f'{name}.graph.json').write_text(json.dumps(graph))
    (project / f'{name}.node.json').write_text(json.dumps(record))


def fixture(root, repo):
    project, peer, pack = (root / name for name in ('Active', 'Peer', 'library'))
    for directory in (project, peer, pack):
        directory.mkdir()
    for name in ('Value', 'Other'):
        publish(pack, name, 'amount')
    entries = ''.join(f'element {name} function "{name}.celem"; element {name}Body implementation "{name}Body.celem"; '
                      for name in ('Value', 'Other'))
    (pack / 'pack.cpack').write_text(f'pack {LIBRARY} version "1" {{ {entries} }}')
    caller(repo, project, 'Caller', 'Value', pack)
    caller(repo, project, 'Sibling', 'Other', pack)
    marker = root / 'executions.txt'
    (project / 'Main.celem').write_text(f'function {NAMESPACE}::Main () -> int {{ provide {NAMESPACE}::Main with {NAMESPACE}::MainBody; }}')
    (project / 'MainBody.celem').write_text(f'''implementation {NAMESPACE}::MainBody for {NAMESPACE}::Main () -> int {{
      import {NAMESPACE}::Caller as Probe (long) -> long; body common "Main.csbody"; }}''')
    (project / 'Main.csbody').write_text(f'''System.IO.File.AppendAllText({json.dumps(str(marker))}, $"{{calls.Probe.Invoke(7L)}}/{{calls.Probe.Invoke(37L)}}\\n");
return 0;''')
    manifest(repo, project, [(name, kind) for feature in ('Main', 'Caller', 'Sibling')
                             for name, kind in ((feature, 'function'), (feature + 'Body', 'implementation'))], library=True)
    (peer / 'Caller.celem').write_text(f'function {PEER_NAMESPACE}::Caller () -> int {{ value editorName = "{LABEL}"; provide {PEER_NAMESPACE}::Caller with {PEER_NAMESPACE}::CallerBody; }}')
    (peer / 'CallerBody.celem').write_text(f'implementation {PEER_NAMESPACE}::CallerBody for {PEER_NAMESPACE}::Caller () -> int {{ body common "Caller.csbody"; }}')
    (peer / 'Caller.csbody').write_text('return 0;')
    manifest(repo, peer, [('Caller', 'function'), ('CallerBody', 'implementation')], namespace=PEER_NAMESPACE, entry='Caller')
    return project, peer, pack, marker


def exercise(root, repo, command, browser):
    project, peer, pack, marker = fixture(root, repo)
    # Open an unrelated project's same-named feature through the normal path.
    with editor(root, repo, command, peer, browser) as page:
        peer_title = page.locator('#title').inner_text().removesuffix(' ▾')
        find_project_item(page, PEER_NAMESPACE + '::Caller', '기능')
        declaration = page.locator('.window[data-key=declaration]')
        declaration.locator('[data-inline-description]').fill(PEER_DRAFT)
        declaration.locator('[data-feature-action=save]').click()
        expect(page.locator('#title')).to_be_enabled()
        page.locator('.brand').click()
        expect(page.locator('.home-grid')).to_be_visible()
    peer_checkpoint, = peer.glob('.confectory/edit-workspaces/*/draft.json')
    peer_draft = peer_checkpoint.read_bytes()
    assert PEER_DRAFT in peer_draft.decode()

    with editor(root, repo, command, project, browser) as page:
        dock = page.get_by_role('button', name='프로젝트 실행', exact=True)
        run = page.locator('.run-window:visible')
        workspace = page.get_by_role('tab', name='Workspace', exact=True)
        latest = project / '.confectory/outputs/linux/latest.json'
        calls = []

        def observe(request):
            if request.method == 'POST' and request.url.endswith('/api/request'):
                data = request.post_data_json
                if data.get('op') == 'invoke':
                    calls.append((data['endpoint'], data['input']))

        page.on('request', observe)
        open_workspace_menu(page).get_by_role('button', name='프로젝트 브라우저', exact=True).click()
        catalogue = page.locator('.window[data-key^="browser:project:"]')
        catalogue.get_by_role('button', name='기능', exact=True).click()
        catalogue.locator('[data-browser-control=object-query]').fill(LABEL)
        catalogue.locator('[data-browser-control=object-search]').click()
        for name in ('Caller', 'Sibling'):
            expect(catalogue.locator(f'[data-object="{NAMESPACE}::{name}"]')).to_contain_text(LABEL)
        catalogue.locator('[data-close]').first.click()
        dock.click()
        expect(run.locator('[data-run-frame]')).to_have_text('종료 코드 0', timeout=120000)
        assert marker.read_text().splitlines() == ['12/42']
        successful = latest.read_bytes()
        first_output = Path(json.loads(successful)['output'])
        binaries = {path: path.read_bytes() for path in first_output.glob('*.dll')}
        assert binaries
        workspace.click()

        # A local fixture publishes an updated registered pack; editor operations
        # below can edit only the caller. The old source stays read-only to it.
        publish(pack, 'Value', 'renamed')
        protected = {path: path.read_bytes() for directory in (project, peer, pack)
                     for path in directory.iterdir() if path.is_file()}
        graph_path = project / 'Caller.graph.json'
        graph_before = json.loads(protected[graph_path])
        call_before = next(row for row in graph_before['nodes'] if row['id'] == 'invoke')

        dock.click()
        expect(run.locator('.caption strong')).to_have_text('실행 실패', timeout=120000)
        expect(run.locator('[data-run-surface]')).to_contain_text('BLUEPRINT_NOT_READY')
        assert latest.read_bytes() == successful and marker.read_text().splitlines() == ['12/42']
        start = len(calls)
        run.get_by_role('button', name='기능 열기 · ' + NAMESPACE + '::Caller', exact=True).click()
        declaration = page.locator('.window[data-key=declaration]')
        expect(declaration.locator('.object-title-name')).to_have_text('Caller')
        declaration.locator('[data-function-write-direct]').click()
        author = page.locator('.window[data-key=blueprint]')
        expect(author.get_by_role('tab', name='논리 코드', exact=True)).to_have_attribute('aria-selected', 'true')
        cell = author.locator('[data-document-cell="invoke"]')
        expect(cell.locator('.fd-cell-state')).to_have_text('계약 확인 필요')
        assert [data['id'] for name, data in calls[start:] if name == 'select'] == [NAMESPACE + '::Caller']

        cell.locator('[data-document-call-compare]').click()
        comparison = page.get_by_role('dialog', name='원본 계약 비교')
        expect(comparison.locator('[data-call-contract-before]')).to_have_text('(long amount) → long')
        expect(comparison.locator('[data-call-contract-after]')).to_have_text('(long renamed) → long')
        comparison.locator('[data-call-input-rename]').click()
        mapping = page.get_by_role('dialog', name='기존 입력 연결 선택')
        pick = mapping.locator('[data-call-input-rename-source]')
        apply = mapping.locator('[data-call-input-rename-apply]')
        expect(pick).to_have_value('')
        expect(apply).to_be_disabled()
        pick.select_option('amount')
        apply.click()
        author.locator('[data-bp-save]').click()
        expect(author.locator('.bp-status')).to_have_text('저장됨', timeout=120000)
        remap, = [edit['definition']['abi'] for endpoint, body in calls
                  if endpoint == 'blueprint' and body.get('action') == 'authorBatch'
                  for edit in body['edits'] if edit['action'] == 'rebindCallAbi']
        assert remap['remap']['inputs'] == {'renamed': 'amount'}
        assert remap['receipt']['id'] == LIBRARY + '::Value'
        assert remap['receipt']['textHash'] == hashlib.sha256(protected[pack / 'Value.celem']).hexdigest()
        review(page, author.locator('[data-bp-complete]')).locator('[data-reject]').click()
        assert latest.read_bytes() == successful and marker.read_text().splitlines() == ['12/42']
        assert all(path.read_bytes() == raw for path, raw in protected.items())
        assert all(path.read_bytes() == raw for path, raw in binaries.items())
        assert peer_checkpoint.read_bytes() == peer_draft

        pending = review(page, author.locator('[data-bp-complete]'))
        pending.locator('#confirm').click()
        expect(pending).to_be_hidden(timeout=120000)
        expect(page.locator('#status')).to_have_text('검토한 변경을 최종 소스에 반영했습니다.')
        saved = json.loads(graph_path.read_text())
        call = next(row for row in saved['nodes'] if row['id'] == 'invoke')
        assert saved['edges'] == graph_before['edges'] and call['arguments'] == {'renamed': {'input': 'seed'}}
        for field in ('source', 'helpers'):
            assert call['postCall'][field] == call_before['postCall'][field]
        permitted = {graph_path, project / 'CallerBody.celem'}
        assert all(path.read_bytes() == raw for path, raw in protected.items() if path not in permitted)
        assert peer_checkpoint.read_bytes() == peer_draft and latest.read_bytes() == successful
        assert marker.read_text().splitlines() == ['12/42']
        dock.click()
        expect(run.locator('[data-run-frame]')).to_have_text('종료 코드 0', timeout=120000)
        assert marker.read_text().splitlines() == ['12/42', '12/42'] and latest.read_bytes() != successful
        assert sum(name == 'confirmGroup' for name, _ in calls) == 1
        assert sum(name == 'runWindow' and data.get('operation') == 'start' for name, data in calls) == 3
        assert not {'prepareAI', 'startAI'} & {name for name, _ in calls}
        print('PASS Run → exact caller → Logic Code comparison and explicit mapping → cancelled Review → Confirm → Run', flush=True)

        workspace.click()
        publish(pack, 'Value', 'renamed', 'double')
        dock.click()
        expect(run.locator('.caption strong')).to_have_text('실행 실패', timeout=120000)
        expect(run.locator('[data-run-surface]')).to_contain_text('CONTRACT_MISMATCH')
        expect(run.locator('[data-run-feature]')).to_be_hidden()
        assert marker.read_text().splitlines() == ['12/42', '12/42']
        page.locator('.brand').click()
        page.locator('.project-card').filter(has=page.get_by_role('heading', name=peer_title, exact=True)).locator('[data-enter]').click()
        expect(page.locator('#title')).to_contain_text('Peer')
        find_project_item(page, PEER_NAMESPACE + '::Caller', '기능')
        expect(declaration.locator('[data-inline-description]')).to_have_value(PEER_DRAFT)
        print('PASS an incompatible input type stays a contract failure with no recovery shortcut', flush=True)


if __name__ == '__main__':
    repository = Path(sys.argv[1]).resolve()
    command = json.loads(Path(sys.argv[2]).read_text())['run']
    expect.set_options(timeout=30000)
    with tempfile.TemporaryDirectory(prefix='cf-run-call-repair-') as temp, sync_playwright() as playwright:
        with playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-gpu'],
                                        ignore_default_args=['--disable-dev-shm-usage']) as browser:
            exercise(Path(temp), repository, command, browser)
