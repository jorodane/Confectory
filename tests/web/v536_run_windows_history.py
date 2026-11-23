"""Read recorded facts from the current Run window in two isolated editor projects."""
import json
import re
import uuid

from playwright.sync_api import expect, sync_playwright

from editor_navigation import open_run_window
import v666_workspace_finder_fixture as fixture


def open_window(page):
    opened = page.locator('.run-window:visible')
    if not opened.count():
        open_run_window(page)
    window = page.locator('.run-window:visible')
    expect(window.locator('[data-run-play]')).to_be_enabled()
    return window


def show_history(page, window):
    window.locator('[data-run-developer]').click()
    menu = page.locator('.run-dev-menu:popover-open')
    expect(menu).to_have_attribute('style',re.compile(r'left: .*px;.*top: .*px;'))
    history = menu.locator('[data-run-history]')
    history.locator('summary').click(timeout=5000)
    return history


def journal():
    paths = list((fixture.projects[0].parent / '.confectory/run-history').glob('*.json'))
    assert len(paths) == 1, paths
    return paths[0]


expect.set_options(timeout=30000)
print('Isolated Run history fixture:', fixture.root, flush=True)

try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        fixture.start(0)
        page = fixture.setup(browser)
        window = open_window(page)
        key = window.get_attribute('data-key')
        window.locator('[data-run-play]').click()
        expect(window.locator('[data-run-pause]')).to_be_enabled(timeout=180000)
        window.locator('[data-run-pause]').click()
        expect(window.locator('[data-run-step]')).to_be_enabled()
        window.locator('[data-run-step]').click()
        expect(window.locator('[data-run-step]')).to_be_enabled()
        window.locator('[data-run-play]').click()
        expect(window.locator('.caption strong')).to_have_text('실행 대기중')
        expect(window.locator('[data-run-pause]')).to_be_disabled()
        saved = journal()
        raw = saved.read_bytes()
        doc = json.loads(raw)
        stopped, = doc['rows']
        handle = stopped['execution']
        assert stopped['recordedState'] == 'stopped' and stopped['ack'] == 2 and int(stopped['frame']) >= 1, stopped
        calls_before_read = len(fixture.requests)
        history = show_history(page, window)
        row = history.locator('[data-run-history-execution="'+handle+'"]')
        expect(row).to_contain_text('중단됨')
        expect(row).to_contain_text('프레임 '+stopped['frame'])
        expect(row).to_contain_text('명령 확인 2')
        expect(row).to_contain_text('이 편집기에서 관측한 실행')
        expect(row.locator('button')).to_have_count(0)
        assert not any(call.get('endpoint') == 'runWindow' for call in fixture.requests[calls_before_read:])
        assert saved.read_bytes() == raw
        fixture.checked('현재 실행창에서 실제 프레임 제어·중단 기록 조회와 무변경 확인')

        page.locator('.run-dev-menu:popover-open [data-dev-close]').click()
        page.evaluate('async()=>await confectoryFlushPresentation()')
        page.close()
        fixture.stop()

        fixture.start(1)
        page = fixture.setup(browser)
        window = page.locator('.run-window[data-key="'+key+'"]')
        expect(window.locator('[data-run-play]')).to_be_enabled()
        expect(window.locator('.caption strong')).to_have_text('실행 대기중')
        expect(window.locator('[data-run-pause]')).to_be_disabled()
        history = show_history(page, window)
        row = history.locator('[data-run-history-execution="'+handle+'"]')
        expect(row).to_contain_text('중단됨')
        expect(row).to_contain_text('실행 소유자 없음')
        assert not any(call.get('input',{}).get('operation') in ('start','control','stop')
                       for call in fixture.requests[calls_before_read:] if call.get('endpoint')=='runWindow')
        fixture.checked('프로세스 재시작 후 저장된 결과만 복원하고 이전 실행·제어는 복원하지 않음')

        # Extend an observed format to exercise both pages without launching 32 synthetic processes.
        for order in range(2, 34):
            doc['rows'].append({**stopped, 'execution':uuid.uuid4().hex, 'order':order})
        doc['sequence'] = 33
        sample = json.dumps(doc).encode()
        saved.write_bytes(sample)
        history.locator('[data-run-history-refresh]').click()
        expect(history.locator('[data-run-history-status]')).to_contain_text('33건')
        expect(history.locator('[data-run-history-execution]')).to_have_count(32)
        history.locator('[data-run-history-next]').click()
        expect(row).to_contain_text('중단됨')
        expect(history.locator('[data-run-history-execution]')).to_have_count(1)
        history.locator('[data-run-history-prev]').click()
        expect(history.locator('[data-run-history-execution]')).to_have_count(32)
        assert saved.read_bytes() == sample
        corrupt = b'{"unrecognized":"PRIVATE_TEST_VALUE"}'
        saved.write_bytes(corrupt)
        history.locator('[data-run-history-refresh]').click()
        expect(history.locator('[data-run-history-status]')).to_contain_text('읽을 수 없어요')
        expect(history.locator('[data-run-history-execution]')).to_have_count(0)
        assert 'PRIVATE_TEST_VALUE' not in history.inner_text() and saved.read_bytes() == corrupt
        saved.write_bytes(raw)
        history.locator('[data-run-history-refresh]').click()
        expect(row).to_contain_text('실행 소유자 없음')
        fixture.checked('33건 페이지 이동과 손상 기록의 안전한 확인 및 원문 보존')

        page.close()
        fixture.stop()
        fixture.env['CONFECTORY_WEB_PROJECT'] = str(fixture.projects[1])
        fixture.start(2)
        page = fixture.setup(browser)
        window = open_window(page)
        history = show_history(page, window)
        expect(history.locator('[data-run-history-status]')).to_contain_text('저장된 실행 기록이 없어요')
        expect(history.locator('[data-run-history-execution]')).to_have_count(0)
        assert saved.read_bytes() == raw
        assert not (fixture.projects[1].parent / '.confectory/run-history').exists()
        fixture.original()
        assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
        fixture.checked('별개 프로젝트의 빈 기록, 양 프로젝트 원본 보존과 외부 요청 없음')
        browser.close()
finally:
    fixture.stop()
