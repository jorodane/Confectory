"""A new detached view reuses only a proven, unchanged existing projection.

Run with the editor repository and build report, like the other v821 fixtures.
The external case changes only the fixture's registered schema after opening
existing views. Both cases use the real UI and an independent temporary profile.
"""
import json
import shutil

from playwright.sync_api import expect, sync_playwright

import v821_object_fallback_roundtrip_ui as fallback
import v821_property_window_floating_ui as floating
from v821_project_browser_search_labels import browser_window, choose_tree_location, search

fixture = fallback.fixture


def seed_extra():
    for manifest, title in zip(fixture.projects, (fallback.FIRST, fallback.SECOND)):
        folder = manifest.parent / 'private-source-ExtraFolder.celem'
        folder.write_text(f'category {fallback.NS}::ExtraFolder {{}}\n')
        source = manifest.parent / 'private-source-ExtraRecord.celem'
        source.write_text(f'''object {fallback.NS}::ExtraRecord {{
  use schema {fallback.NS}::StockInfo;
  value editorName = "{fallback.LABEL}";
  value editorFolder = "{fallback.NS}::ExtraFolder";
  data Count = 73;
  data Note = "{title} ExtraRecord";
}}\n''')
        manifest.write_text(manifest.read_text().rstrip()[:-1] + '\n'
                            'element ExtraFolder category "private-source-ExtraFolder.celem";\n'
                            'element ExtraRecord object "private-source-ExtraRecord.celem";\n}\n')
        for path in (folder, source, manifest):
            fixture.before[str(path)] = path.read_bytes()


def open_counts(log):
    rows = []
    for line in log.read_text().splitlines():
        if line.startswith('CONFECTORY_UI_TRACE '):
            rows.append(json.loads(line.split(' ', 1)[1]))
        elif line == 'CONFECTORY_SCHEMA_REUSED':
            rows.append({'stage': 'reused'})
    end = max(index for index, row in enumerate(rows) if row.get('endpoint') == 'openEditorView')
    start = max(index for index, row in enumerate(rows[:end]) if row.get('stage') == 'consumer')
    segment = rows[start + 1:end]
    return (sum(row.get('operation') == 'inspectEffective' for row in segment),
            sum(row.get('stage') == 'reused' for row in segment))


def exercise(browser, number, external):
    profile = fixture.root / f'schema-proof-profile-{number}'
    profile.mkdir()
    shutil.copy2(fixture.root / 'profile' / 'projects.json', profile / 'projects.json')
    fixture.env.update(CONFECTORY_HOME_STORAGE=str(profile), CONFECTORY_ENTRY_STORAGE=str(profile),
                       CONFECTORY_MCP_DIRECTORY=str(fixture.root / f'instances-{number}'),
                       CONFECTORY_UI_TRACE='1')
    fixture.start(number)
    page = None
    try:
        page = fixture.setup(browser)
        page.set_viewport_size({'width': 2000, 'height': 1200})
        primary, _ = fallback.open_from_search(page, fallback.FIRST, fallback.PEER, '41')
        extra, _ = floating.open_properties(page, 'ExtraRecord', 'ExtraFolder')
        expect(primary).to_be_visible()
        expect(extra).to_be_visible()
        window = browser_window(page)
        choose_tree_location(window, f'[data-tree-id="{fallback.NS}::StockFolder"]')
        search(window, fallback.LABEL, fallback.TARGET)
        state = fixture.state()
        assert state['schema']['id'] == f'{fallback.NS}::{fallback.PEER}'
        assert len(state['editorViews']) == 1
        if external:
            dependency = fixture.projects[0].parent / 'private-source-StockInfo.celem'
            dependency.write_text(dependency.read_text().rstrip()[:-1] + '  field ExternalFlag single general string;\n}\n')
            fixture.before[str(dependency)] = dependency.read_bytes()
        else:
            floating.property_value(primary, 'Note').fill('Unapplied primary input')
            floating.property_value(extra, 'Note').fill('Unapplied detached input')
        window.locator(f'[data-object="{fallback.NS}::{fallback.TARGET}"]').click(button='right')
        page.locator('.context-menu').get_by_role('button', name='새 창으로 열기', exact=True).click()
        target = page.locator('.window[data-key="editor-2"]')
        expect(floating.property_value(target, 'Note')).to_have_value(f'{fallback.FIRST} {fallback.TARGET}')
        expect(page.locator('#project-menu')).to_be_enabled()
        full, reused = open_counts(fixture.root / f'host-{number}.log')
        if external:
            for editor in (primary, extra, target):
                expect(fallback.field(editor, 'ExternalFlag')).to_be_visible()
            # A background read can already have refreshed one prior projection.
            assert full >= 2 and reused <= 1, (full, reused)
        else:
            assert (full, reused) == (1, 2), (full, reused)
            expect(floating.property_value(primary, 'Note')).to_have_value('Unapplied primary input')
            expect(floating.property_value(extra, 'Note')).to_have_value('Unapplied detached input')
        # A detached status read is not a schema mutation. It must still update
        # all open views if their shared registered dependency changes.
        if external:
            dependency.write_text(dependency.read_text().rstrip()[:-1] +
                                  '  field StatusExternalFlag single general string;\n}\n')
            fixture.before[str(dependency)] = dependency.read_bytes()
        owner = f'{fallback.NS}::{fallback.TARGET}'
        status = fixture.call('browserDrafts', {'action': 'status', 'view': '2', 'id': owner, 'ids': [owner]})
        assert owner in status['ids'], status
        if external:
            for editor in (primary, extra, target):
                expect(fallback.field(editor, 'StatusExternalFlag')).to_be_visible()
        else:
            expect(floating.property_value(primary, 'Note')).to_have_value('Unapplied primary input')
            expect(floating.property_value(extra, 'Note')).to_have_value('Unapplied detached input')
        fixture.original()
        print(f'PASS {"external dependency" if external else "unchanged views"}: full={full}, reused={reused}', flush=True)
    finally:
        if page is not None:
            page.close()
        fixture.stop()


if __name__ == '__main__':
    fallback.seed()
    seed_extra()
    with sync_playwright() as playwright, playwright.chromium.launch(
            executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-gpu']) as browser:
        expect.set_options(timeout=30000)
        exercise(browser, 0, False)
        exercise(browser, 1, True)
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
