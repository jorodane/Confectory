"""Create a new function through EditorHome, write Logic Code, publish and run it."""
import json
from pathlib import Path
import re
import shutil
import sys

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as f
from editor_navigation import open_workspace_menu

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'gui'))
from editor_logic_workflow import review, run_from_dock

early = len(sys.argv)>3 and sys.argv[3]=='before-save'
name = 'LocalAuthorProbe'
target = 'Example.FrameLoop::' + name
marker = f.root / 'new-function-result.txt'
donor_marker = f.root / 'referenced-function-result.txt'
donor = 'Example.FrameLoop::LocalDonor'
# Add an ordinary published donor to the synthetic project only.
manifest = f.projects[0]
manifest.write_text(manifest.read_text().rstrip().removesuffix('}') +
    'element LocalDonor function "LocalDonor.celem";element LocalDonorBody implementation "LocalDonorBody.celem";}')
donor_sources = {
    'LocalDonor.celem': f'function {donor} (int amount) -> void {{provide {donor} with {donor}Body;}}',
    'LocalDonorBody.celem': f'implementation {donor}Body for {donor} (int amount) -> void {{body common "LocalDonor.csbody";}}',
    'LocalDonor.csbody': 'System.IO.File.WriteAllText(' + json.dumps(str(donor_marker)) + ', amount.ToString());',
}
for filename, text in donor_sources.items():
    path = manifest.parent / filename
    path.write_text(text)
    f.before[str(path)] = path.read_bytes()
f.before[str(manifest)] = manifest.read_bytes()
expect.set_options(timeout=60000)

try:
    with sync_playwright() as pw, pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) as browser:
        f.start(0)
        page = f.setup(browser)
        page.set_viewport_size({'width': 1800, 'height': 1200})
        menu = open_workspace_menu(page)
        menu.locator('[data-workspace-create-menu]').click()
        page.locator('[data-workspace-create=Feature]').click()
        dialog = page.get_by_role('dialog', name='새 기능 만들기', exact=True)
        dialog.locator('#object-name').fill(name)
        dialog.get_by_role('button', name='생성', exact=True).click()
        expect(dialog).to_be_hidden()
        declaration = page.locator('.window[data-key=declaration]')
        expect(declaration.locator('.object-title-name')).to_have_text(name)
        assert '() -> int' in f.state()['draft']['text']
        declaration.locator('[data-function-write-direct]').click()
        panel = page.locator('.window[data-key=blueprint]')
        expect(panel.locator('.function-document')).to_be_visible()
        panel.get_by_role('tab', name='논리 코드', exact=True).click()
        doc = panel.locator('.function-document')
        expect(doc.locator('[data-document-cell="$entry"]')).to_be_visible()
        if early:
            entry = doc.locator('[data-document-cell="$entry"]')
            entry.locator('[data-document-contract="$entry"]').click()
            contract = entry.locator('[data-document-contract-side=inputs]')
            contract.locator('[data-mobile-contract-add]').click()
            field=contract.locator('[data-mobile-contract-field=input1]')
            expect(field).to_be_visible()
            field.locator('[data-signature-type]').click()
            page.get_by_role('dialog',name='속성 타입 선택').locator('[data-type=int]').click()
            output=entry.locator('[data-document-contract-side=outputs] [data-mobile-contract-field=return]')
            output.locator('[data-signature-type]').click()
            page.get_by_role('dialog',name='속성 타입 선택').locator('[data-type=long]').click()
            entry.locator('[data-document-contract="$entry"]').click()
            f.original()
        code = doc.locator('[data-document-code=body]')
        expect(code).to_be_enabled()
        code.click()
        script = page.locator('.bp-script-dialog')
        source = script.locator('[data-code-source]')
        expect(source).to_be_visible()
        new = 'System.IO.File.WriteAllText(' + json.dumps(str(marker)) + ', "new function executed");\nreturn 0;'
        source.evaluate('''el => {
            const parts=Array.from(el.closest('.bp-script-editor').querySelectorAll('[data-code-highlight] > span'));
            const index=parts.findIndex(part=>part.dataset.codeRegion==='body');
            if(index<0)throw Error('Missing editable body');
            const start=parts.slice(0,index).reduce((offset,part)=>offset+part.textContent.length,0);
            el.focus();el.setSelectionRange(start,start+parts[index].textContent.length);
        }''')
        page.keyboard.insert_text(new)
        expect(script.locator('[data-code-region=body]')).to_have_text(new)
        script.locator('[data-code-save]').click()
        expect(script).to_be_hidden()
        if not early:
            panel.locator('[data-bp-save]').click()
            expect(panel.locator('.bp-status')).to_have_text('저장됨', timeout=120000)
            f.original()
            r=review(page,panel.locator('[data-bp-complete]'))
            r.locator('#confirm').click()
            expect(r).to_be_hidden(timeout=120000)
            assert name in f.projects[0].read_text() and name not in f.projects[1].read_text()
            print('PASS actual new feature declaration, document code edit, Save and Confirm', flush=True)
        # Add a typed published feature from the Logic Code view itself,
        # without switching to Blueprint or manually reconnecting execution.
        add = doc.locator('[data-document-insert-call="$entry"]')
        expect(add).to_be_enabled()
        add.click()
        picker = page.get_by_role('dialog', name='블루프린트 노드 검색')
        candidate = picker.locator(f'[data-resource-feature="{donor}"]')
        expect(candidate).to_be_visible()
        picker.locator('[data-resource-close]').click()
        expect(doc.locator('[data-document-cell^="call_"]')).to_have_count(0)
        add.click()
        expect(candidate).to_be_visible()
        candidate.click()
        call_cell = doc.locator('[data-document-cell^="call_"]')
        expect(call_cell).to_be_visible()
        call_id = call_cell.get_attribute('data-document-cell')
        assert doc.locator('[data-document-cell]').evaluate_all('(cells)=>cells.map(c=>c.dataset.documentCell)')[:3] == ['$entry',call_id,'body']
        doc.press('Control+z')
        expect(call_cell).to_have_count(0)
        doc.press('Control+y')
        expect(call_cell).to_be_visible()
        value = call_cell.locator('[data-document-value][data-document-port="field:amount"]')
        value.click()
        values = page.get_by_role('dialog', name='핀 값 선택')
        if early:
            values.get_by_role('button',name='입력 · input1',exact=True).click()
            expect(value).to_contain_text('input1')
        else:
            values.get_by_role('searchbox', name='값 검색').fill('37')
            values.get_by_role('searchbox', name='값 검색').press('Enter')
            expect(value).to_have_text('37')
        if early:
            f.original()
            candidate_path=manifest.parent/'LocalDonor.celem'
            original=candidate_path.read_bytes()
            candidate_path.write_bytes(original+b' ')
            try:
                panel.locator('[data-bp-save]').click()
                expect(panel.locator('.bp-status')).to_contain_text('모든 입력은 유지됩니다.',timeout=30000)
                assert not list(manifest.parent.glob('blueprints/*.graph.json'))
                assert not list(manifest.parent.glob('.confectory/edit-workspaces/*/draft.json'))
                assert candidate_path.read_bytes()==original+b' '
            finally:
                candidate_path.write_bytes(original)
            page.evaluate('async()=>await confectoryFlushPresentation()')
            page.close();f.stop();f.start(10)
            page=f.setup(browser);page.set_viewport_size({'width':1800,'height':1200})
            panel=page.locator('.window[data-key=blueprint]');doc=panel.locator('.function-document')
            expect(doc.locator(f'[data-document-cell="{call_id}"]')).to_be_visible()
            expect(doc.locator(f'[data-document-value="{call_id}"][data-document-port="field:amount"]')).to_contain_text('input1')
            f.original()
        panel.locator('[data-bp-save]').click()
        expect(panel.locator('.bp-status')).to_have_text('저장됨', timeout=120000)
        if early:
            f.original()
        r = review(page,panel.locator('[data-bp-complete]'))
        r.locator('[data-reject]').click()
        expect(r).to_be_hidden()
        r = review(page,panel.locator('[data-bp-complete]'))
        r.locator('#confirm').click()
        expect(r).to_be_hidden(timeout=120000)
        graph_path = next(manifest.parent.glob('blueprints/*.graph.json'))
        graph = json.loads(graph_path.read_text())
        if early:
            declaration_path=next(manifest.parent.rglob(name+'.celem'))
            assert '(int input1) -> long' in declaration_path.read_text()
        assert graph['feature'] == target and graph['entry'] == call_id
        assert {'from':call_id,'port':'next','to':'body'} in graph['edges']
        call = next(node for node in graph['nodes'] if node['id']==call_id)
        assert call['kind']=='call' and call['feature']==donor and call['arguments']=={'amount':{'input':'input1'} if early else {'constant':37}}
        assert all((manifest.parent / file).read_text()==source for file,source in donor_sources.items())
        assert donor not in f.projects[1].read_text()
        print('PASS actual Logic Code feature insertion, value binding, Undo/Redo and Review/Confirm', flush=True)
        page.close()
        f.stop()

        # Restore the same authored project and editor presentation before running.
        f.start(1)
        page = f.setup(browser)
        page.set_viewport_size({'width': 1800, 'height': 1200})
        restored = page.locator('.window[data-key=blueprint] .function-document')
        expect(restored.locator(f'[data-document-cell="{call_id}"]')).to_be_visible()
        expect(restored.locator(f'[data-document-value="{call_id}"][data-document-port="field:amount"]')).to_contain_text('input1' if early else '37')
        page.close()
        f.stop()
        print('PASS cold restart restores the committed call and typed input', flush=True)

        # The tested authoring product has no new test-only execution action.
        # Select the committed function as the ordinary entry in a separate
        # synthetic copy, without modifying any authored function or original project.
        pdir = f.root / 'new function execution harness'
        shutil.copytree(f.projects[0].parent, pdir, ignore=shutil.ignore_patterns('.confectory', '.build'))
        manifest = pdir / f.projects[0].name
        text, count = re.subn(r'\bentry\s+[^;]+;', f'entry {target};', manifest.read_text(), count=1)
        assert count == 1
        if early:
            # Execution harness uses the ordinary entry with the new input contract.
            text=text.replace('entry '+target+';', 'entry Example.FrameLoop::Main;')
            (pdir/'MainBody.celem').write_text(
                'implementation Example.FrameLoop::MainBody for Example.FrameLoop::Main () -> int {import '+target+' as Probe (int) -> long;body common "Main.csbody";}')
            (pdir/'Main.csbody').write_text('return checked((int)calls.Probe.Invoke(37));')
        manifest.write_text(text)
        f.env['CONFECTORY_WEB_PROJECT'] = str(manifest)
        f.start(2)
        page = f.setup(browser)
        page.set_viewport_size({'width': 1800, 'height': 1200})
        run_from_dock(page, marker, 'new function executed')
        assert donor_marker.read_text() == '37'
        assert not f.errors and not f.external, (f.errors, f.external)
        print('PASS ordinary editor Run in isolated entry harness executes the newly authored feature', flush=True)
        page.close()
finally:
    f.stop()
    print('evidence', f.root, flush=True)
