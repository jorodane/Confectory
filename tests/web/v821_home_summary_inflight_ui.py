"""An admitted Home metadata job must not own the foreground project cursor.

Uses actual catalog reads and a separate, externally edited registered project.
Run with REPO BUILD_REPORT and the usual local web fixture environment.
"""
import re
from playwright.sync_api import expect, sync_playwright
import v821_object_fallback_roundtrip_ui as d
from editor_navigation import choose_project_tool

f = d.fixture
source = d.seed()
f.env['CONFECTORY_UI_TRACE'] = '1'
expect.set_options(timeout=90000)
try:
    with sync_playwright() as p, p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-gpu']) as browser:
        f.start(0)
        page = f.setup(browser)
        page.evaluate('()=>{globalThis.confectoryWebUITrace=[];}')
        d.leave_to_home(page)
        page.wait_for_function("()=>confectoryWebUITrace.some(row=>row.stage==='call'&&row.endpoint==='homeSummaries'&&row.code==='completed')")
        # No fake response or held request: the semantic admission finished,
        # but the real confirmed metadata is still being computed.
        assert page.locator('[data-stat="objects"][data-status="pending"]').count() > 0
        card = page.locator('.project-card').filter(has=page.get_by_role('heading', name=d.FIRST, exact=True))
        card.locator('[data-enter]').click()
        expect(page.locator('#title')).to_contain_text(d.FIRST)
        expect(page.locator('#project-menu')).to_be_enabled()
        assert f.state()['projectId']
        # A pure pack display requests confirmed inventory, not draft relations.
        mark = len(f.requests)
        page.locator('#workspace-pack-tab').click()
        expect(page.locator('#pack-manager-view [data-pack]').first).to_be_visible()
        expect(page.locator('#project-menu')).to_be_enabled()
        calls = [row['endpoint'] for row in f.requests[mark:]]
        assert 'localInventory' in calls and 'relationsMap' not in calls, calls
        page.locator('#workspace-home-tab').click()
        mark = len(f.requests)
        editor, _ = d.open_from_search(page, d.FIRST, d.TARGET, d.BEFORE)
        assert 'relationsMap' in [row['endpoint'] for row in f.requests[mark:]]

        note = d.field(editor, 'Note').get_by_label('Note 기본값', exact=True)
        note.fill('Retained while Home summary retired')
        # Explicit relation reload must still revalidate a changed schema,
        # rather than keeping a stale primary projection for speed.
        choose_project_tool(page, '개념 맵')
        graph = page.locator('.window[data-key="map"]')
        expect(graph.locator('[data-map-scene]')).to_be_visible()
        expect(page.locator('#project-menu')).to_be_enabled()
        schema = f.projects[0].parent / 'private-source-StockInfo.celem'
        schema.write_text(schema.read_text().rstrip()[:-1] + ' field RelationLater single general string;\n}\n')
        f.before[str(schema)] = schema.read_bytes()
        graph.locator('[data-map-reload]').click()
        expect(d.field(editor, 'RelationLater')).to_be_visible()
        expect(note).to_have_value('Retained while Home summary retired')
        expect(page.locator('#project-menu')).to_be_enabled()
        # Change only the other synthetic project's committed manifest.
        other = f.projects[1]
        added = other.parent / 'private-source-HomeLater.celem'
        added.write_text(f'object {d.NS}::HomeLater {{}}\n')
        other.write_text(other.read_text().rstrip()[:-1] + '\n element HomeLater object "private-source-HomeLater.celem";\n}\n')
        f.before[str(added)] = added.read_bytes()
        f.before[str(other)] = other.read_bytes()
        expected = len(re.findall(r'\belement\s+\w+\s+object\s+', other.read_text()))
        d.leave_to_home(page)
        second = page.locator('.project-card').filter(has=page.get_by_role('heading', name=d.SECOND, exact=True))
        expect(second.locator('[data-stat="objects"]')).to_have_text(str(expected))
        expect(second.locator('[data-stat="objects"]')).to_have_attribute('data-status', 'available')
        card.locator('[data-enter]').click()
        expect(page.locator('#title')).to_contain_text(d.FIRST)
        expect(note).to_have_value('Retained while Home summary retired')
        f.original()
        assert not f.errors and not f.external, (f.errors, f.external)
        print('PASS actual admitted Home read, foreground project, fresh other-project count and retained input', flush=True)
finally:
    f.stop()
    print('evidence', f.root, flush=True)
