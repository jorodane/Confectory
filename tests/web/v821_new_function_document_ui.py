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

name = 'LocalAuthorProbe'
target = 'Example.FrameLoop::' + name
marker = f.root / 'new-function-result.txt'
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
        panel.locator('[data-bp-save]').click()
        expect(panel.locator('.bp-status')).to_have_text('저장됨', timeout=120000)
        f.original()
        r=review(page,panel.locator('[data-bp-complete]'))
        r.locator('#confirm').click()
        expect(r).to_be_hidden(timeout=120000)
        assert name in f.projects[0].read_text() and name not in f.projects[1].read_text()
        print('PASS actual new feature declaration, document code edit, Save and Confirm', flush=True)
        page.close()
        f.stop()

        # The tested authoring product has no new test-only execution action.
        # Select the committed function as the ordinary entry in a separate
        # synthetic copy, without modifying any authored function or original project.
        pdir = f.root / 'new function execution harness'
        shutil.copytree(f.projects[0].parent, pdir, ignore=shutil.ignore_patterns('.confectory', '.build'))
        manifest = pdir / f.projects[0].name
        text, count = re.subn(r'\bentry\s+[^;]+;', f'entry {target};', manifest.read_text(), count=1)
        assert count == 1
        manifest.write_text(text)
        f.env['CONFECTORY_WEB_PROJECT'] = str(manifest)
        f.start(1)
        page = f.setup(browser)
        page.set_viewport_size({'width': 1800, 'height': 1200})
        run_from_dock(page, marker, 'new function executed')
        print('PASS ordinary editor Run in isolated entry harness executes the newly authored feature', flush=True)
        page.close()
finally:
    f.stop()
    print('evidence', f.root, flush=True)
