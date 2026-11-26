"""Actual saved Logic Code caller using installed runtime pack contracts.

Run after project_installed_pack_registration.py on its disposable UI-created
Timing Puzzle evidence directory. No feature/source files are seeded or edited.
"""
import sys
from pathlib import Path
from playwright.sync_api import expect, sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'gui'))
import editor_local_first_workflow as f
from editor_logic_workflow import open_main, review, run_from_dock

repo = Path(sys.argv[2]).resolve()
root = Path(sys.argv[3]).resolve()
project = root / 'projects' / 'Timing Puzzle'
assert root.name.startswith('confectory-local-first-') and project.is_dir()
manifest = project / 'project.cproj'
marker = root / 'puzzle-score.txt'
old = f.ROOT
f.ROOT, f.PROFILE, f.PROJECTS, f.TITLE, f.repo = root, root/'profile', root/'projects', 'Timing Puzzle', repo
f.ENV = {key: str(value).replace(str(old), str(root)) for key, value in f.ENV.items()}
f.ENV.update(CONFECTORY_EDITOR_REPO=str(repo), CONFECTORY_ELEMENT_AUTHORING_HOST=str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'), CONFECTORY_PROJECT_EXECUTION_HOST=str(repo/'targets/project-execution-host/bin/Release/net10.0/Confectory.ProjectExecutionHost.dll'))
expect.set_options(timeout=30000)


def open_document(page):
    page.evaluate('async()=>await confectoryFlushPresentation()')
    for key in ('targets', 'packs'):
        other = page.locator(f'.window[data-key={key}]')
        if other.is_visible():
            other.locator('[data-close]').first.click()
    panel = open_main(page, manifest.read_text().split()[1]+'::PlayTimingPuzzle')
    panel.locator(':scope > .window-title .caption').click(position={'x':5, 'y':8})
    doc = panel.locator('.function-document')
    expect(doc).to_be_visible()
    return panel, doc


def select_search(picker, search, expected):
    picker.locator('[data-resource-query]').fill(search)
    candidate = picker.locator(f'[data-resource-feature="{expected}"]')
    expect(candidate).to_be_visible()
    return candidate


with sync_playwright() as pw, pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) as browser:
    if '--cold-only' not in sys.argv:
        with f.web(browser, 'registered-runtime-call') as page:
            before = manifest.read_bytes()
            panel, doc = open_document(page)
            add = doc.locator('[data-document-insert-call="$entry"]')
            add.click()
            picker = page.get_by_role('dialog', name='블루프린트 노드 검색')
            select_search(picker, 'Confectory.Window::Open', 'Confectory.Window::Open')
            select_search(picker, 'Confectory.RenderInput::Pump', 'Confectory.RenderInput::Pump')
            picker.locator('[data-resource-close]').click()
            expect(doc.locator('[data-document-cell^="call_"]')).to_have_count(0)
            add.click()
            candidate = select_search(picker, 'TextStyle', 'Confectory.Window::TextStyle')
            candidate.click()
            cell = doc.locator('[data-document-cell^="call_"]')
            expect(cell).to_be_visible()
            expect(doc).to_contain_text('TextStyle')
            panel.locator('[data-bp-save]').click()
            expect(panel.locator('.bp-status')).to_have_text('저장됨', timeout=120000)
            result = review(page, panel.locator('[data-bp-complete]'))
            result.locator('#confirm').click()
            expect(result).to_be_hidden(timeout=120000)
            assert manifest.read_bytes() == before
            run_from_dock(page, marker, '1')
            print('PASS runtime contracts searchable, cancel leaves graph unchanged, call inserted, saved, confirmed and executed', flush=True)
    with f.web(browser, 'cold-registered-runtime-call') as page:
        _, doc = open_document(page)
        expect(doc.locator('[data-document-cell^="call_"]')).to_be_visible()
        expect(doc).to_contain_text('TextStyle')
        run_from_dock(page, marker, '1')
        print('PASS cold editor restores registered call and executes existing score', flush=True)
