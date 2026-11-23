"""Explicitly keep a wrapped call's existing input through a published rename."""
import json
from pathlib import Path
import subprocess
import sys

from playwright.sync_api import expect, sync_playwright

import v821_call_contract_status_ui as base

f = base.f
legacy = '--legacy' in sys.argv[3:]
manifest = f.projects[0]
directory = manifest.parent
graph_path = directory / f'{base.A}.graph.json'


def seed():
    base.seed()
    feature = base.NS + 'ImpactProbe'
    body = feature + 'Body'
    caller = base.NS + base.A
    source = directory / f'{base.TARGET}.csbody'
    source.write_text('return amount + 5L;\n')
    (directory/'ImpactProbe.celem').write_text(f'function {feature} () -> int {{provide {feature} with {body};}}')
    (directory/'ImpactProbeBody.celem').write_text(
        f'implementation {body} for {feature} () -> int {{import {caller} as Probe (long) -> long; body common "ImpactProbe.csbody";}}')
    (directory/'ImpactProbe.csbody').write_text(
        'System.Console.WriteLine(calls.Probe.Invoke(7L));\nSystem.Console.WriteLine(calls.Probe.Invoke(37L));\nreturn 0;\n')
    original = manifest.read_text().replace(f'entry {base.NS}Main;', f'entry {feature};')
    manifest.write_text(original.rstrip()[:-1] + '\nelement ImpactProbe function "ImpactProbe.celem";\n'
                        'element ImpactProbeBody implementation "ImpactProbeBody.celem";\n}\n')


def execute(label):
    cli = f.repo / 'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'
    compiled = subprocess.run([f.env['CONFECTORY_DOTNET'], str(cli), 'build', str(manifest), 'portable'],
                              capture_output=True, text=True, env=f.env)
    (f.root/f'{label}-build.log').write_text(compiled.stdout + compiled.stderr)
    assert compiled.returncode == 0, (compiled.stdout[-3000:], compiled.stderr[-3000:])
    run = json.loads(compiled.stdout)['run']
    output = subprocess.run(run, env=f.env, capture_output=True, text=True, check=True)
    (f.root/f'{label}-run.txt').write_text(output.stdout)
    assert output.stdout.splitlines() == ['12', '42'], output.stdout


def pending(page):
    page.evaluate('() => confectoryFlushPresentation()')
    return f.state()['presentation']['inputs']['blueprint']


def choose(page, window):
    if legacy:
        window.get_by_role('tab', name='블루프린트 보기', exact=True).click()
        window.locator(f'[data-bp-overview-node="{base.CALL}"]').click()
        window.locator(f'[data-bp-node="{base.CALL}"] [data-wrapper-refresh]').click()
        dialog = page.get_by_role('dialog', name='호출 계약 갱신')
        select = dialog.locator('[data-abi-input="renamed"]')
        apply = dialog.locator('[data-abi-remap-accept]')
        cancel = dialog.locator('[data-abi-remap-cancel]')
        old = 'pin:amount'
    else:
        window.locator(f'[data-document-call-compare="{base.CALL}"]').click()
        comparison = page.get_by_role('dialog', name='원본 계약 비교')
        expect(comparison.locator('[data-call-contract-before]')).to_have_text('(long amount) → long')
        expect(comparison.locator('[data-call-contract-after]')).to_have_text('(long renamed) → long')
        comparison.locator('[data-call-input-rename]').click()
        dialog = page.get_by_role('dialog', name='기존 입력 연결 선택')
        select = dialog.locator('[data-call-input-rename-source]')
        apply = dialog.get_by_role('button', name='선택한 계약 갱신', exact=True)
        cancel = dialog.get_by_role('button', name='취소', exact=True)
        old = 'amount'
        expect(apply).to_be_disabled()
        assert select.locator('option').evaluate_all('(options)=>options.map(option=>option.value)') == ['', old]
    expect(select).to_have_value('')
    select.select_option(old)
    expect(apply).to_be_enabled()
    return dialog, apply, cancel


def review(page, author):
    author.locator('[data-bp-complete]').click()
    base.idle(page)
    page.locator('.window[data-key=review]:visible,.window[data-key=targets]:visible').first.wait_for(timeout=90000)
    choices = page.locator('.window[data-key=targets]')
    if choices.is_visible():
        choices.locator('[data-target-choice]').select_option('portable')
        choices.locator('[data-close]').click()
        author.locator('[data-bp-complete]').click()
    result = page.locator('.window[data-key=review]')
    expect(result).to_be_visible(timeout=90000)
    if result.locator('[data-review-advanced]').is_visible():
        result.locator('[data-review-advanced]').click()
    if result.locator('[data-advanced-reviewed]').count():
        result.locator('[data-advanced-reviewed]').check()
    return result


def check_publication_change(page):
    feature = base.NS + base.TARGET

    def publish(value):
        f.call('select', {'id': feature})
        f.call('inspectDeclaration', {'id': feature})
        declaration = f.state()['declaration']
        f.call('editMetadata', {'id': feature, 'revision': declaration['revision'],
                                'hash': declaration['textHash'], 'field': 'blueprintPublishedOutputs', 'value': value})
        f.call('saveDraft', {})

    publish('["return"]')
    window = base.open_document(page, base.A)
    assert not base.graph(base.A)[1].get('callInputRename')
    window.locator(f'[data-document-call-compare="{base.CALL}"]').click()
    comparison = page.get_by_role('dialog', name='원본 계약 비교')
    expect(comparison).to_be_visible()
    expect(comparison.locator('[data-call-input-rename]')).to_have_count(0)
    comparison.locator('[data-call-contract-close]').click()
    assert not pending(page)
    publish('[]')
    f.original()
    f.checked('A concurrent published-output change keeps the rename action out of Logic Code')


def run(browser):
    f.call('select', {'id': base.NS + base.A})
    f.call('saveDraft', {})
    page = f.setup(browser)
    page.set_viewport_size({'width': 1500, 'height': 1050})
    if not legacy:
        check_publication_change(page)
    author = base.open_document(page, base.A)
    previous, call = base.graph(base.A)
    expected_binding = call['arguments'][0]['valueJson']
    assert call['postCallStale'] and call['callAbiAvailable'] and not call['postCallSignatureMatches']
    assert call['callAbiRemap'] == {'inputs': {'renamed': None}, 'outputs': {'return': 'return'}}
    assert not (call.get('callAbiGroupBinding') or call.get('callAbiUseGroupBinding'))
    if not legacy:
        assert call['callInputRename'] == {'before': 'amount', 'after': 'renamed'}
    checkpoint, = directory.glob('.confectory/edit-workspaces/*/draft.json')
    before = checkpoint.read_bytes()
    dialog, _, cancel = choose(page, author)
    cancel.click()
    expect(dialog).to_be_hidden()
    assert not pending(page) and checkpoint.read_bytes() == before
    assert base.graph(base.A)[1]['arguments'] == call['arguments']
    f.original()

    if legacy:
        author.get_by_role('tab', name='논리 코드', exact=True).click()
    dialog, apply, _ = choose(page, author)
    apply.click()
    expect(dialog).to_be_hidden()
    held = pending(page)
    plan, = [json.loads(row['text']) for _, row in held if row['type'] == 'wrapper']
    assert len(held) == 1 and plan['abi']['remap'] == {'inputs': {'renamed': 'amount'}, 'outputs': {'return': 'return'}}
    assert checkpoint.read_bytes() == before
    preview = author.locator(f'[data-document-value="{base.CALL}"][data-document-port="field:renamed"]')
    if not legacy:
        expect(preview).to_have_text('seed')
    author.locator('[data-bp-save]').click()
    status = author.locator('.bp-status')
    expect(status).not_to_have_text('저장 중…', timeout=120000)
    expect(status).to_have_text('저장됨')
    assert not pending(page)
    edits = [row['input']['edits'] for row in f.requests if row['endpoint'] == 'blueprint'
             and row['input'].get('action') == 'authorBatch']
    assert len(edits) == 1 and len(edits[0]) == 1 and edits[0][0]['action'] == 'rebindCallAbi', edits
    f.original()

    page.close()
    f.stop()
    f.start(1)
    page = f.setup(browser)
    page.set_viewport_size({'width': 1500, 'height': 1050})
    author = page.locator('.window[data-key="blueprint"]')
    if author.get_by_role('tab', name='블루프린트 보기', exact=True).get_attribute('aria-selected') == 'true':
        author.get_by_role('tab', name='논리 코드', exact=True).click()
    expect(author.locator(f'[data-document-value="{base.CALL}"][data-document-port="field:renamed"]')).to_have_text('seed')
    restored, updated = base.graph(base.A)
    assert restored['edges'] == previous['edges'] and not updated['postCallStale']
    assert [(row['name'], row['valueJson']) for row in updated['arguments']] == [('renamed', expected_binding)]
    assert all(updated['postCall'][key] == call['postCall'][key] for key in ['source', 'helpers'])
    review(page, author).locator('[data-reject]').click()
    f.original()
    window = review(page, author)
    window.locator('#confirm').click()
    expect(window).to_be_hidden(timeout=120000)
    saved_call = next(row for row in json.loads(graph_path.read_text())['nodes'] if row['id'] == base.CALL)
    assert saved_call['arguments'] == {'renamed': {'input': 'seed'}}
    mutable = {graph_path, directory / f'{base.A}Body.celem'}
    assert all(Path(path).read_bytes() == raw for path, raw in f.before.items() if Path(path) not in mutable)
    assert not f.errors and not f.external, (f.errors, f.external)
    execute('confirmed')
    f.checked('Cancel, explicit mapping, cold Save, Review/Confirm and two executable inputs preserve the existing binding and values 12 and 42')


try:
    seed()
    execute('before-rename')
    for filename in [f'{base.TARGET}.celem', f'{base.TARGET}Body.celem', f'{base.TARGET}.csbody']:
        path = directory / filename
        path.write_text(path.read_text().replace('amount', 'renamed'))
    f.before = {str(path): path.read_bytes() for project in f.projects
                for path in project.parent.iterdir() if path.is_file()}
    f.start(0)
    with sync_playwright() as playwright:
        expect.set_options(timeout=30000)
        with playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) as browser:
            run(browser)
finally:
    f.save_evidence()
    f.stop()
    print('Evidence:', f.root, flush=True)
