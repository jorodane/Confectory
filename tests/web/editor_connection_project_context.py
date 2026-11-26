"""Open the normal Agent setup in two isolated projects, then restart.

Uses the existing synthetic same-ID project fixture and never authenticates.
Arguments: repository path and Linux editor build report.
"""
import hashlib
from playwright.sync_api import sync_playwright, expect
import v821_object_fallback_roundtrip_ui as fallback

fixture = fallback.fixture
connection = 'Confectory.Agent.Codex::Connection'


def setup_connection(page):
    page.locator('#add-agent').click()
    dialog = page.get_by_role('dialog', name='Agent 추가', exact=True)
    dialog.get_by_role('button', name='Codex', exact=True).click()
    expect(dialog.locator('[data-cli-login]')).to_be_enabled()
    dialog.locator('[data-connection-cancel]').click()
    expect(dialog).to_have_count(0)


fallback.seed()
fixture.env['CONFECTORY_UI_TRACE'] = '1'
fixture.start(0)
try:
    with sync_playwright() as playwright, playwright.chromium.launch(
            executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-gpu']) as browser:
        expect.set_options(timeout=30000)
        page = fixture.setup(browser)
        fallback.open_from_search(page, fallback.FIRST, fallback.TARGET, fallback.BEFORE)
        first = fixture.state()['projectId']
        setup_connection(page)
        assert fixture.state()['projectId'] == first
        settings = fixture.root / 'profile' / 'ai-settings' / hashlib.sha256(connection.encode()).hexdigest()[:16]
        pair = {name: (settings / name).read_bytes() for name in ('project.cpack', 'Settings.celem')}
        fallback.enter_from_home(page, fallback.SECOND)
        fallback.open_from_search(page, fallback.SECOND, fallback.TARGET, '19')
        second = fixture.state()['projectId']
        assert second != first
        setup_connection(page)
        assert fixture.state()['projectId'] == second
        fallback.enter_from_home(page, fallback.FIRST)
        fallback.open_from_search(page, fallback.FIRST, fallback.TARGET, fallback.BEFORE)
        assert fixture.state()['projectId'] == first
        assert all((settings / name).read_bytes() == data for name, data in pair.items())
        fixture.original()
        fixture.checked('Agent setup preserves active project identity and same-ID project values across switches')
        page.close()
        fixture.stop()
        fixture.start(1)
        page = fixture.setup(browser)
        fallback.open_from_search(page, fallback.FIRST, fallback.TARGET, fallback.BEFORE)
        setup_connection(page)
        assert fixture.state()['projectId'] == first
        assert all((settings / name).read_bytes() == data for name, data in pair.items())
        fixture.original()
        assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
        fixture.checked('Cold restart revalidates the existing settings and preserves project/source identity')
finally:
    fixture.stop()
print('PASS', fixture.root)
