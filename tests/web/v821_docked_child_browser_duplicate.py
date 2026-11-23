"""A docked child Browser can open a second view without rebinding either view."""
from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture
from v821_category_move_identity_ui import MOVING, open_browser, seed_projects


MENU_LABEL = "같은 브라우저 새 창으로 열기"
PENDING_QUERY = "아직 적용하지 않은 원래 검색"
NO_MATCH = "이름이 일치하지 않는 복제 검색"


def query(window):
    return window.locator('[data-browser-control="object-query"]')


def mover(window):
    return window.locator(f'[data-object="{MOVING}"]')


def context(page, element):
    element.click(button="right")
    return page.locator(".context-menu")


def verify_copy(window):
    expect(window.locator(".browser-title-path")).to_contain_text("StartFolder")
    expect(query(window)).to_have_value(PENDING_QUERY)
    expect(mover(window)).to_be_visible()
    expect(window.locator('[data-density="100"]')).to_have_attribute("aria-pressed", "true")


def main():
    seed_projects()
    expect.set_options(timeout=30000)
    print("Isolated Browser fixture:", fixture.root, flush=True)
    try:
        fixture.start(0)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
            page = fixture.setup(browser)
            page.set_viewport_size({"width": 1800, "height": 1150})
            primary = open_browser(page)
            caption = primary.locator(':scope > .window-title .caption')
            menu = context(page, caption)
            expect(menu.get_by_role("button", name=MENU_LABEL, exact=True)).to_have_count(0)
            menu.get_by_role("button", name="탭으로 열기", exact=True).click()
            menu = context(page, page.locator('[data-window-tab="browser"]'))
            expect(menu.get_by_role("button", name=MENU_LABEL, exact=True)).to_have_count(0)
            menu.get_by_role("button", name="탭 닫기", exact=True).click()

            page.locator("#workspace").click(button="right", position={"x": 920, "y": 200})
            finder = page.get_by_role("dialog", name="작업 공간 창 검색")
            finder.get_by_role("searchbox").fill("StartFolder")
            finder.get_by_role("button", name="StartFolder", exact=False).click()
            source = page.locator('.window[data-key^="browser-tree:concept:"]')
            expect(mover(source)).to_be_visible()
            source_key = source.get_attribute("data-key")
            source.locator('[data-density="100"]').click()
            query(source).fill("Mover")
            query(source).press("Enter")
            expect(mover(source)).to_be_visible()
            query(source).fill(PENDING_QUERY)
            menu = context(page, source.locator(':scope > .window-title .caption'))
            expect(menu.get_by_role("button", name=MENU_LABEL, exact=True)).to_be_visible()
            menu.get_by_role("button", name="탭으로 열기", exact=True).click()
            tab = page.locator(f'[data-window-tab="{source_key}"]')
            expect(tab).to_have_attribute("aria-selected", "true")
            verify_copy(source)
            menu = context(page, tab)
            menu.get_by_role("button", name=MENU_LABEL, exact=True).click(timeout=5000)

            clone = page.locator('.window[data-key^="browser:concept:"]')
            expect(clone).to_have_count(1)
            expect(clone).to_be_visible()
            clone_key = clone.get_attribute("data-key")
            assert clone_key != source_key
            expect(tab).to_have_attribute("aria-selected", "false")
            verify_copy(clone)
            fixture.checked("문서 탭의 하위 브라우저를 같은 경로·모드·검색을 가진 별도 Workspace 창으로 열기")

            query(clone).fill(NO_MATCH)
            query(clone).press("Enter")
            expect(mover(clone)).to_have_count(0)
            tab.click()
            verify_copy(source)
            menu = context(page, source.locator(':scope > .window-title .caption'))
            expect(menu.get_by_role("button", name=MENU_LABEL, exact=True)).to_be_visible()
            tab.click()
            expect(menu).to_be_hidden()
            expect(clone).to_have_count(1)
            page.evaluate("async()=>await confectoryFlushPresentation()")
            page.close()
            fixture.stop()

            fixture.start(1)
            page = fixture.setup(browser)
            source = page.locator(f'.window[data-key="{source_key}"]')
            clone = page.locator(f'.window[data-key="{clone_key}"]')
            tab = page.locator(f'[data-window-tab="{source_key}"]')
            expect(tab).to_have_attribute("aria-selected", "true")
            verify_copy(source)
            page.get_by_role("tab", name="Workspace", exact=True).click()
            expect(clone).to_be_visible()
            expect(query(clone)).to_have_value(NO_MATCH)
            expect(mover(clone)).to_have_count(0)
            fixture.original()
            assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
            fixture.checked("독립 검색 변경·메뉴 취소·실제 재시작 복원과 원본 바이트 보존")
            browser.close()
    finally:
        fixture.stop()


if __name__ == "__main__":
    main()
