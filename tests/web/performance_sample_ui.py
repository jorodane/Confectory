"""Disposable packaged performance sample, exercised through actual Chromium UI.

Run with REPO BUILD_REPORT and the standard editor fixture environment.
The Windows batch itself is not executed by this Linux test.
"""
import json
import shutil
import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright
import v666_workspace_finder_fixture as f
import v821_direct_property_save_ui as d
from editor_navigation import goto_editor
from v821_project_browser_search_labels import browser_window

template = Path(__file__).resolve().parents[2] / 'examples/performance-sample'
sample = f.root / 'performance-sample'
shutil.copytree(template, sample)
before = {p: p.read_bytes() for p in sample.rglob('*') if p.is_file()}
local = f.root / 'local-appdata'
local.mkdir()
f.env.update(XDG_DATA_HOME=str(local), CONFECTORY_WEB_PROJECT=str(sample / 'project.cpack'))
f.env.pop('CONFECTORY_PERFORMANCE', None)
logs = local / 'Confectory' / 'Performance'
secret = 'SYNTHETIC_PRIVATE_PERF_SENTINEL'
expect.set_options(timeout=60000)

def find(page, name):
    browser = browser_window(page)
    browser.get_by_role('textbox', name='의미 객체 검색', exact=True).fill('Sample ' + name)
    browser.get_by_role('button', name='검색 확정', exact=True).click()
    owner = 'Confectory.PerformanceSample::Sample' + name
    row = browser.locator(f'[data-object="{owner}"]')
    expect(row).to_be_visible()
    expect(page.locator('#project-menu')).to_be_enabled()
    return row, owner

def open_property(page, name):
    row, owner = find(page, name)
    row.click(button='right')
    page.locator('.context-menu').get_by_role('button', name='새 창으로 열기', exact=True).click()
    w = page.locator(f'.window[data-element-owner="{owner}"]:visible')
    expect(d.value(w, 'Count')).to_have_value('10')
    expect(d.value(w, 'Count')).to_be_editable()
    expect(page.locator('#project-menu')).to_be_enabled()
    return page.locator(f'.window[data-key="{w.get_attribute("data-key")}"]')

def capture_file():
    return max(logs.glob('*/engine.jsonl'), key=lambda path: path.stat().st_mtime_ns)

def wait_events(page, path, expected):
    end = time.monotonic() + 30
    while time.monotonic() < end:
        try:
            rows = [json.loads(line) for line in path.read_text().splitlines()]
        except (OSError, json.JSONDecodeError):
            page.wait_for_timeout(100)
            continue
        if expected <= {(r['stage'], r['operation']) for r in rows}:
            for r in rows:
                assert set(r) == {'stage', 'operation', 'elapsedMs', 'atMs', 'pageMs'}, r
            assert secret not in path.read_text() and str(sample) not in path.read_text()
            assert 'Synthetic sample' not in path.read_text() and 'Confectory.PerformanceSample' not in path.read_text()
            return rows
        page.wait_for_timeout(100)
    raise AssertionError((path, expected))

try:
    with sync_playwright() as p, p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox']) as browser:
        f.env.update(CONFECTORY_HOME_STORAGE=str(f.root/'off-profile'), CONFECTORY_ENTRY_STORAGE=str(f.root/'off-entry'))
        f.start(0); page = f.setup(browser); open_property(page, 'A')
        page.close(); f.stop()
        assert not logs.exists()
        print('PASS sample capture disabled; no performance files', flush=True)

        f.env.update(CONFECTORY_PERFORMANCE='1', CONFECTORY_HOME_STORAGE=str(f.root/'on-profile'), CONFECTORY_ENTRY_STORAGE=str(f.root/'on-entry'))
        f.start(1); page = f.setup(browser); page.set_viewport_size({'width':2000,'height':1200})
        first = open_property(page, 'A')
        first_capture = capture_file()
        wait_events(page, first_capture, {('window-ready','openEditorView')})
        first.get_by_role('button', name='창 닫기', exact=True).click()
        expect(first).to_be_hidden()
        row, _ = find(page, 'A')
        row.press('Enter')
        expect(first).to_be_visible()
        expect(d.value(first, 'Count')).to_be_editable()
        wait_events(page, first_capture, {('window-ready','reopenEditorView')})
        second = open_property(page, 'B')
        third = open_property(page, 'C')
        d.value(first, 'Note').fill(secret)
        page.locator('#chat-input').fill(secret)
        d.value(third, 'Count').fill('11')
        d.commit(page, third)
        assert 'data Count = 11' in (sample/'SampleC.celem').read_text()
        for path, original in before.items():
            if path != sample/'SampleC.celem':
                assert path.read_bytes() == original, path
        expect(d.value(first, 'Note')).to_have_value(secret)
        page.evaluate('()=>confectoryFlushPresentation()')
        events = {('window-ready','openEditorView'), ('window-ready','reopenEditorView'),
                  ('property-save-ready','direct-property-save'), ('consumer','confirmGroup')}
        rows = wait_events(page, first_capture, events)
        for r in rows:
            if (r['stage'],r['operation']) in events:
                print('observed', r['stage'], r['operation'], r['elapsedMs'], flush=True)
        page.close(); f.stop()

        f.env.pop('CONFECTORY_WEB_PROJECT', None)
        f.start(2); page = browser.new_page(viewport={'width':2000,'height':1200}); goto_editor(page, f.url)
        card = page.locator('.project-card').filter(has=page.get_by_role('heading', name='Confectory.PerformanceSample', exact=True))
        expect(card).to_have_count(1)
        card.locator('[data-enter]').click()
        expect(page.locator('.window[data-key^="editor-"]:visible')).to_have_count(3)
        for n,value in [('A','10'),('B','10'),('C','11')]:
            w=page.locator(f'.window[data-element-owner="Confectory.PerformanceSample::Sample{n}"]:visible')
            expect(d.value(w,'Count')).to_have_value(value)
            expect(d.value(w,'Count')).to_be_editable()
        expect(d.value(page.locator('.window[data-element-owner="Confectory.PerformanceSample::SampleA"]:visible'),'Note')).to_have_value(secret)
        second_capture = capture_file()
        assert second_capture != first_capture
        rows = wait_events(page, second_capture, {(stage,'restore') for stage in ('restore-view','restore-total','restore-layout','workspace-attach')})
        for r in rows:
            if r['stage'] in ('restore-view','restore-total','restore-layout','workspace-attach'):
                print('observed',r['stage'],r['elapsedMs'],flush=True)
        print('PASS sample capture distinguishes first/reopen/direct save/three-window cold restore; private inputs absent', flush=True)
finally:
    f.stop()
    print('evidence', f.root, flush=True)
