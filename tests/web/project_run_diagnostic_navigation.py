"""Open a verified Blueprint diagnostic subject in the real Linux editor."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from playwright.sync_api import expect, sync_playwright

from editor_navigation import open_workspace_menu
from project_run_compile_recovery import editor
from editor_logic_workflow import review as prepare_review


LABEL = 'Shared feature name'
DRAFT = 'Review this draft separately'


def fixture(root, repo, title, *, stale_blueprint):
    project = root / title
    project.mkdir()
    namespace = 'DiagnosticNavigation.' + title
    target = namespace + '::Target'
    registrations = []

    def declare(name, kind, text):
        path = project / (name + '.celem')
        path.write_text(text)
        locator = f'element {name} {kind} "{path.name}";'
        if locator not in registrations:
            registrations.append(locator)

    def write_contracts(kind):
        declare('Entry', 'function', f'function {namespace}::Entry () -> int {{ provide {namespace}::Entry with {namespace}::EntryBody; }}')
        declare('Target', 'function', f'function {target} () -> {kind} {{ value editorName = "{LABEL}"; provide {target} with {namespace}::TargetBody; }}')
        output = 'blueprint common "target.graph.json";' if stale_blueprint else 'body common "Target.csbody";'
        declare('TargetBody', 'implementation', f'implementation {namespace}::TargetBody for {target} () -> {kind} {{ {output} }}')
        declare('EntryBody', 'implementation', f'''implementation {namespace}::EntryBody for {namespace}::Entry () -> int {{
            import {target} as Target () -> {kind}; body common "Entry.csbody"; }}''')

    write_contracts('int')
    declare('Decoy', 'function', f'function {namespace}::Decoy () -> int {{ value editorName = "{LABEL}"; }}')
    (project / 'Entry.csbody').write_text('return checked((int)calls.Target.Invoke());\n')
    (project / 'project.cpack').write_text(f'''project {namespace} version "1" {{ standalone true;
        registry Confectory.Build.DotNet {json.dumps(str(repo / 'targets/dotnet/pack.cpack'))};
        dependency Confectory.Build.DotNet version "0.1.0";
        entry {namespace}::Entry; target linux Confectory.Build.DotNet::Linux;
        {''.join(registrations)} }}''')
    if not stale_blueprint:
        (project / 'Target.csbody').write_text('return "wrong C# result";\n')
        return project, namespace

    dotnet = os.environ['CONFECTORY_DOTNET']
    signature = {'args': [], 'return': 'int'}
    old_contract = json.dumps({'feature': target, 'signature': signature}, sort_keys=True, separators=(',', ':'))
    graph = {'schema': 1, 'profile': 'sync-acyclic-v1', 'feature': target,
             'contractHash': hashlib.sha256(old_contract.encode()).hexdigest(), 'entry': 'body',
             'nodes': [{'id': 'body', 'kind': 'code', 'control': 'next', 'intent': 'Return a value',
                        'signature': signature, 'arguments': {}, 'implementation': 'target.node.json'}],
             'edges': [{'from': 'body', 'port': 'next', 'to': 'exit:done'}],
             'exits': {'done': {'node': 'body'}}}
    author = repo / 'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'
    response = subprocess.run([dotnet, str(author)], input=json.dumps({
        'operation': 'featureBlueprintDescribe', 'featureSource': (project / 'Target.celem').read_text(), 'graph': graph}),
        text=True, capture_output=True, check=True, timeout=30)
    described = json.loads(response.stdout)['result']
    assert described['state'] == 'needs-implementation', described
    node = {'schema': 1, 'node': 'body', 'definitionHash': described['nodes'][0]['definitionHash'], 'source': 'return 23;'}
    (project / 'target.node.json').write_text(json.dumps(node))
    (project / 'target.graph.json').write_text(json.dumps(graph))
    cli = repo / 'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'
    old = subprocess.run([dotnet, str(cli), 'build', str(project / 'project.cpack'), 'linux'],
                         capture_output=True, text=True, timeout=120)
    assert old.returncode == 0, old.stderr
    # Deliberately retain a real older graph while moving the fixture's public
    # signature and its caller forward. ▶ must encounter the engine's own refusal.
    write_contracts('long')
    return project, namespace


def exercise(root, repo, command, browser):
    peer, peer_namespace = fixture(root, repo, 'Peer', stale_blueprint=False)
    project, namespace = fixture(root, repo, 'Active', stale_blueprint=True)
    protected = {path: path.read_bytes() for directory in (project, peer) for path in directory.iterdir() if path.is_file()}
    with editor(root, repo, command, peer, browser) as page:
        peer_title = page.locator('#title').inner_text().removesuffix(' ▾')
        page.locator('.brand').click()
        expect(page.locator('.home-grid')).to_be_visible()

    with editor(root, repo, command, project, browser) as page:
        calls = []

        def observe(request):
            if request.method == 'POST' and request.url.endswith('/api/request'):
                data = request.post_data_json
                if data.get('op') == 'invoke':
                    calls.append((data['endpoint'], data['input']))

        page.on('request', observe)
        declaration = page.locator('.window[data-key=declaration]')
        open_workspace_menu(page).get_by_role('button', name='프로젝트 브라우저', exact=True).click()
        catalogue = page.locator('.window[data-key^="browser:project:"]')
        catalogue.get_by_role('button', name='기능', exact=True).click()
        catalogue.locator('[data-browser-control=object-query]').fill(LABEL)
        catalogue.locator('[data-browser-control=object-search]').click()
        decoy = catalogue.locator(f'[data-object="{namespace}::Decoy"]')
        for row in (decoy, catalogue.locator(f'[data-object="{namespace}::Target"]')):
            expect(row).to_contain_text(LABEL)
        decoy.press('Enter')
        catalogue.locator('[data-close]').first.click()
        expect(declaration.locator('.object-title-name')).to_have_text('Decoy')
        declaration.locator('[data-inline-description]').fill(DRAFT)
        declaration.locator('[data-feature-action=save]').click()
        review = prepare_review(page, declaration.locator('[data-feature-action=confirm]'))
        expect(review).to_contain_text('Decoy')
        checkpoint, = project.glob('.confectory/edit-workspaces/*/draft.json')
        saved = checkpoint.read_bytes()
        assert DRAFT in saved.decode()

        page.get_by_role('button', name='프로젝트 실행', exact=True).click()
        run = page.locator('.run-window:visible')
        expect(run.locator('.caption strong')).to_have_text('실행 실패', timeout=120000)
        expect(run.locator('[data-run-surface]')).to_contain_text('BLUEPRINT_NOT_READY')
        jump = run.get_by_role('button', name='기능 열기 · ' + namespace + '::Target', exact=True)
        expect(jump).to_be_enabled()
        retired = jump.element_handle()
        before = len(calls)
        jump.click()
        expect(page.locator('#status')).to_have_text('변경 검토를 닫은 뒤 이 기능을 열어 주세요.')
        assert 'select' not in [name for name, _ in calls[before:]]
        page.get_by_role('tab', name='Workspace', exact=True).click()
        expect(review).to_contain_text('Decoy')
        review.locator('[data-reject]').click()
        expect(review).to_be_hidden()
        page.get_by_role('tab', name='실행 실패', exact=True).click()
        jump.click()
        expect(declaration.locator('.object-title-name')).to_have_text('Target')
        assert [data['id'] for name, data in calls[before:] if name == 'select'] == [namespace + '::Target']
        assert checkpoint.read_bytes() == saved and not [name for name, _ in calls if name == 'confirmGroup']
        print('PASS the proven diagnostic opens only its owned function and respects an active Review', flush=True)

        page.locator('.brand').click()
        page.locator('.project-card').filter(has=page.get_by_role('heading', name=peer_title, exact=True)).locator('[data-enter]').click()
        expect(page.locator('#title')).to_contain_text('Peer')
        before = len(calls)
        # An obsolete DOM action must have no access to a different project.
        retired.dispatch_event('click')
        page.get_by_role('button', name='프로젝트 실행', exact=True).click()
        expect(run.locator('.caption strong')).to_have_text('실행 실패', timeout=120000)
        expect(run.locator('[data-run-surface]')).to_contain_text('CS0029')
        expect(run.locator('[data-run-feature]')).to_be_hidden()
        assert 'select' not in [name for name, _ in calls[before:]]
        assert str(root) not in run.inner_text()
        assert all(path.read_bytes() == content for path, content in protected.items())
        assert peer_namespace + '::Target' != namespace + '::Target'
        print('PASS another project cannot reuse the old action, and C# errors without a subject stay as text', flush=True)


if __name__ == '__main__':
    repository = Path(sys.argv[1]).resolve()
    command = json.loads(Path(sys.argv[2]).read_text())['run']
    expect.set_options(timeout=30000)
    with tempfile.TemporaryDirectory(prefix='cf-run-diagnostic-') as temp, sync_playwright() as playwright:
        with playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-gpu'],
                                        ignore_default_args=['--disable-dev-shm-usage']) as browser:
            exercise(Path(temp), repository, command, browser)
