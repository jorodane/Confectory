"""Actual deletion UI for an unsupported large declared-reference graph.

The existing proof limit is intentional; never stage a partial deletion.
Run with REPO BUILD_REPORT on a disposable synthetic project.
"""
import sys
from playwright.sync_api import expect, sync_playwright
import v666_workspace_finder_fixture as f
from v821_project_browser_search_labels import NS, browser_window

count = 400
for manifest in f.projects:
    entries = []
    for i in range(count):
        name = f"BudgetObject{i:04}"
        path = manifest.parent / f"{name}.celem"
        path.write_text(f'object {NS}::{name} {{}}\n')
        f.before[str(path)] = path.read_bytes()
        entries.append(f'element {name} object "{path.name}";')
    manifest.write_text(manifest.read_text().rstrip()[:-1]+"\n"+"\n".join(entries)+"\n}\n")
    f.before[str(manifest)] = manifest.read_bytes()
try:
    f.start(0)
    with sync_playwright() as play, play.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
        page = f.setup(browser)
        b = browser_window(page)
        b.get_by_role("textbox", name="의미 객체 검색", exact=True).fill("BudgetObject0000")
        b.get_by_role("button", name="검색 확정", exact=True).click()
        row = b.locator(f'[data-object="{NS}::BudgetObject0000"]')
        expect(row).to_be_visible(timeout=60000)
        row.click(button="right")
        page.get_by_role("button", name="삭제", exact=True).click()
        dialog = page.get_by_role("dialog", name="의미 객체 삭제", exact=True)
        expect(dialog).to_be_visible(timeout=30000)
        expect(dialog).to_contain_text("지원 범위(256)")
        expect(dialog).to_contain_text("원본과 작업 사본은 변경하지 않았어요.")
        expect(dialog.locator("#delete-object")).to_have_count(0)
        dialog.get_by_role("button", name="닫기", exact=True).click()
        expect(row).to_be_visible()
        assert not any(item["endpoint"] in ("browserRetirement", "confirmGroup") for item in f.requests), f.requests[-10:]
        f.original()
        assert not f.errors and not f.external
        print("PASS large deletion explicitly refused; no stage/confirm or source change", flush=True)
finally:
    f.stop()
    print("evidence", f.root, flush=True)
