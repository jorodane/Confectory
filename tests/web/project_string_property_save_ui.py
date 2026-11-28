"""Ordinary local string saves on a build-capable synthetic project.

Run with REPO BUILD_REPORT [40|400] [--trace-files] [--guards] [--continuous] [--continuous-in-place] [--continuous-detached] and the built desktop target.
Unlike performance-restore-sample's intentionally tool-free registry,
this fixture has a real build target. The bounded single-scalar save must not
need to compile or access project assemblies.
--continuous performs five extra actual string saves; --continuous-in-place
keeps the same primary property window after ordinary commands are ready.
--continuous-detached measures five additional saves in the same independent
window and verifies an ordinary primary integer save.
--verify-relation-delta checks changed owned rows in the 400-object host trace.
"""
import json
import os
import re
import shutil
import sys
import time

from playwright.sync_api import expect, sync_playwright
from editor_navigation import goto_editor
from v821_project_browser_search_labels import browser_window
import v666_workspace_finder_fixture as f

count = int(sys.argv[3]) if len(sys.argv) > 3 else 40
assert count in (40, 400)
flags = set(sys.argv[4:])
assert flags <= {"--trace-files", "--guards", "--continuous", "--verify-relation-delta", "--continuous-in-place", "--continuous-detached"}
assert "--verify-relation-delta" not in flags or (count == 400 and "--continuous" in flags)
assert "--continuous-in-place" not in flags or "--continuous" in flags
assert "--continuous-detached" not in flags or ("--continuous" in flags and "--continuous-in-place" not in flags)
run = f.report["run"]
ns = "Confectory.PerformanceRestoreSample"
sample = f.root / "string-save"
shutil.copytree(f.repo / "examples/performance-restore-sample", sample)
target = f.repo / "targets/dotnet/pack.cpack"
assert (target.parent / "bin/Release/net10.0/Confectory.Build.DotNet.dll").is_file(), "Build the real desktop target first"
manifest = sample / "project.cpack"
text = manifest.read_text().replace('"build/pack.cpack"', json.dumps(str(target)))
registrations = []
for i in range(40, count):
    name = f"StringExtra{i:04}"
    (sample / f"{name}.celem").write_text(
        f'object {ns}::{name} {{ use schema {ns}::SampleInfo; data Count = {i}; data Note = "Synthetic extra"; }}\n')
    registrations.append(f'element {name} object "{name}.celem";')
manifest.write_text(text.rstrip()[:-1] + "\n" + "\n".join(registrations) + "\n}\n")
before = {path: path.read_bytes() for path in sample.rglob("*") if path.is_file()}
profile = f.root / "profile"
profile.mkdir()
(profile / "projects.json").write_text(json.dumps([{"path": str(manifest), "title": "String save", "description": ""}]))
f.env.update(CONFECTORY_HOME_STORAGE=str(profile), CONFECTORY_ENTRY_STORAGE=str(f.root / "entry"))
f.env.pop("CONFECTORY_WEB_PROJECT", None)
expect.set_options(timeout=120000)
if "--continuous" in flags: f.env["CONFECTORY_UI_TRACE"] = "1"


def page_for(browser, n):
    if "--trace-files" in flags:
        f.report["run"] = ["strace", "-f", "-e", "trace=execve,openat", "-o", str(f.root / f"files-{n}.log"), *run]
    f.start(n)
    page = browser.new_page(viewport={"width": 2000, "height": 1200})
    page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(f.origin + "/") else route.abort())
    goto_editor(page, f.url)
    card = page.locator(".project-card").filter(has=page.get_by_role("heading", name="String save", exact=True))
    expect(card.locator('[data-stat="objects"]')).to_have_text(str(count))
    card.locator("[data-enter]").click()
    expect(page.locator("#project-menu")).to_be_enabled()
    return page


def open_owner(page, name, primary=False):
    w = browser_window(page)
    w.get_by_role("textbox", name="의미 객체 검색", exact=True).fill("Sample " + name)
    w.get_by_role("button", name="검색 확정", exact=True).click()
    row = w.locator(f'[data-object="{ns}::Sample{name}"]')
    expect(row).to_be_visible()
    expect(page.locator("#project-menu")).to_be_enabled()
    row.click(button="right")
    page.locator(".context-menu").get_by_role(
        "button", name="스키마 열기" if primary else "새 창으로 열기", exact=True).click()
    window = page.locator('.window[data-key="schema"]' if primary else f'.window[data-element-owner="{ns}::Sample{name}"]')
    expect(window.get_by_label("Note 기본값", exact=True)).to_be_editable()
    return window


def note(name):
    text = (sample / f"Sample{name}.celem").read_text()
    return json.loads(re.search(r'data\s+Note\s*=\s*("(?:\\.|[^"\\])*")\s*;', text).group(1))


def replace_input(page, field, value):
    field.press("Control+A")
    if value:
        page.keyboard.insert_text(value)
    else:
        field.press("Backspace")
    expect(field).to_have_value(value)


def save(page, window, persisted):
    button = window.locator('[data-element-action="confirm"]')
    expect(button).to_have_text("저장")
    if "--continuous" in flags:
        # Timestamp the actual DOM click and readiness in the page rather than
        # interpreting Playwright's increasingly spaced assertion polls as UI latency.
        button.evaluate("""el => {
          globalThis.__saveTiming = null;
          el.addEventListener('click', () => {
            const start = performance.now(), timing = globalThis.__saveTiming = {start, success: null, ready: null};
            const status = document.querySelector('#status');
            let sawDisabled = false;
            // The preceding save may still display the same text. Only a new
            // status mutation after this click counts as this save's success.
            const observer = new MutationObserver(() => {
              if (status.textContent.trim() === '저장했습니다.' && timing.success === null) timing.success = performance.now() - start;
            });
            observer.observe(status, {childList: true, characterData: true, subtree: true});
            const tick = () => {
              if (globalThis.__saveTiming !== timing) { observer.disconnect(); return; }
              const menu = document.querySelector('#project-menu');
              if (menu?.disabled) sawDisabled = true;
              if (sawDisabled && timing.success !== null && menu && !menu.disabled) { timing.ready = performance.now() - start; observer.disconnect(); return; }
              if (performance.now() - start < 120000) requestAnimationFrame(tick); else observer.disconnect();
            };
            requestAnimationFrame(tick);
          }, {capture: true, once: true});
        }""")
    started = time.monotonic()
    button.click()
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline and not persisted():
        page.wait_for_timeout(100)
    assert persisted(), f.state().get("logs", [])[-10:]
    if "--continuous" in flags: print("save-file-ms", round((time.monotonic()-started)*1000,1), flush=True)
    expect(page.locator("#status")).to_have_text("저장했습니다.")
    expect(page.locator('.window[data-key="review"]')).to_be_hidden()
    expect(page.get_by_role("dialog", name="관련 변경 검토")).to_have_count(0)
    if "--continuous" in flags:
        print("save-ui-ms", round((time.monotonic()-started)*1000,1), flush=True)
        expect(page.locator("#project-menu")).to_be_enabled()
        print("save-ready-ms", round((time.monotonic()-started)*1000,1), flush=True)
        page.wait_for_function("() => globalThis.__saveTiming?.ready != null", timeout=120000)
        timing = page.evaluate("globalThis.__saveTiming")
        print("save-browser-success-ms", round(timing["success"],1), flush=True)
        print("save-browser-ready-ms", round(timing["ready"],1), flush=True)


try:
    with sync_playwright() as p, p.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
        page = page_for(browser, 0)
        primary = open_owner(page, "D", primary=True)
        unicode = "한글 문자열 · café"
        replace_input(page, primary.get_by_label("Note 기본값", exact=True), unicode)
        save(page, primary, lambda: note("D") == unicode)
        if "--continuous-detached" in flags:
            replace_input(page, primary.get_by_label("Count 기본값", exact=True), "77")
            save(page, primary, lambda: 'data Count = 77' in (sample / "SampleD.celem").read_text())
        elif "--continuous" in flags:
            for value in ("Continuous 1", "Continuous 2", "Continuous 3", "Continuous 4", unicode):
                expect(page.locator("#project-menu")).to_be_enabled()
                if "--continuous-in-place" not in flags:
                    primary = open_owner(page, "D", primary=True)
                replace_input(page, primary.get_by_label("Note 기본값", exact=True), value)
                save(page, primary, lambda: note("D") == value)

        detached = open_owner(page, "A")
        replace_input(page, detached.get_by_label("Note 기본값", exact=True), "")
        save(page, detached, lambda: note("A") == "")
        if "--continuous-detached" in flags:
            print("detached-repeated-begin", flush=True)
            for value in ("Detached 1", "Detached 2", "Detached 3", "Detached 4", ""):
                replace_input(page, detached.get_by_label("Note 기본값", exact=True), value)
                save(page, detached, lambda: note("A") == value)
            print("detached-repeated-end", flush=True)
        if "--verify-relation-delta" in flags:
            expect(page.locator("#project-menu")).to_be_enabled()
            deltas = [json.loads(line.split(' ', 1)[1]) for line in (f.root / 'host-0.log').read_text().splitlines() if line.startswith('CONFECTORY_RELATION_ROWS ')]
            assert sum(row['parsed']==1 and row['reused']>=400 for row in deltas)>=3, deltas
            print('PASS repeated actual property saves reparse only changed owned row', deltas, flush=True)
        peer = open_owner(page, "B")
        replace_input(page, peer.get_by_label("Note 기본값", exact=True), "Unsaved peer")
        # The independently opened peer overlaps A's Save button. Close it
        # normally (retaining its input) instead of forcing a hidden click.
        peer.locator("[data-close]").click()
        expect(peer).to_be_hidden()
        expect(page.locator("#project-menu")).to_be_enabled()
        replace_input(page, detached.get_by_label("Count 기본값", exact=True), "11")
        save(page, detached, lambda: 'data Count = 11' in (sample / "SampleA.celem").read_text())

        w = browser_window(page)
        w.get_by_role("textbox", name="의미 객체 검색", exact=True).fill("Sample B")
        w.get_by_role("button", name="검색 확정", exact=True).click()
        row = w.locator(f'[data-object="{ns}::SampleB"]')
        expect(row).to_be_visible()
        expect(page.locator("#project-menu")).to_be_enabled()
        row.press("Enter")
        expect(peer).to_be_visible()
        expect(peer.get_by_label("Note 기본값", exact=True)).to_have_value("Unsaved peer")
        assert all(path.read_bytes() == raw for path, raw in before.items()
                   if path.name not in ("SampleA.celem", "SampleD.celem"))
        page.evaluate("()=>confectoryFlushPresentation()")
        page.close()
        f.stop()
        page = page_for(browser, 1)
        a = page.locator(f'.window[data-element-owner="{ns}::SampleA"]')
        expect(a.get_by_label("Note 기본값", exact=True)).to_have_value("")
        expect(a.get_by_label("Count 기본값", exact=True)).to_have_value("11")
        expect(page.locator(f'.window[data-element-owner="{ns}::SampleB"]').get_by_label("Note 기본값", exact=True)).to_have_value("Unsaved peer")
        # Detached saving can move the primary selection. Explicitly reopen
        # D through the normal Browser rather than assuming its old layout.
        primary = open_owner(page, "D", primary=True)
        expect(primary.get_by_label("Note 기본값", exact=True)).to_have_value(unicode)
        assert note("D") == unicode and note("A") == "" and note("B") == "Synthetic sample B"
        if "--continuous-detached" in flags:
            expect(primary.get_by_label("Count 기본값", exact=True)).to_have_value("77")
        print(f"PASS {count} objects: primary Unicode and detached empty string, integer save, independent input, restart", flush=True)
        if "--guards" in flags:
            field = primary.get_by_label("Note 기본값", exact=True)
            replace_input(page, field, "Uncommitted local input")
            unrelated = sample / "ModelExtra00.celem"
            if os.name == "posix":
                mode = unrelated.stat().st_mode
                unrelated.chmod(0)
                try:
                    if not os.access(unrelated, os.R_OK):
                        primary.locator('[data-element-action="confirm"]').click()
                        expect(page.locator("#status")).to_have_text(re.compile("작업을 완료하지 못했습니다|저장하지 못했습니다|저장 검증에 실패했습니다"))
                        assert note("D") == unicode
                        expect(field).to_have_value("Uncommitted local input")
                        print("PASS unreadable unrelated source refuses save and retains input", flush=True)
                finally:
                    unrelated.chmod(mode)
            source = sample / "SampleD.celem"
            external = source.read_text().replace(json.dumps(unicode, ensure_ascii=False), json.dumps("External owner value"))
            assert external != source.read_text()
            source.write_text(external)
            primary.locator('[data-element-action="confirm"]').click()
            expect(page.locator("#status")).to_have_text(re.compile("작업을 완료하지 못했습니다|저장하지 못했습니다|저장 검증에 실패했습니다|충돌"))
            assert source.read_text() == external
            expect(field).to_have_value("Uncommitted local input")
            print("PASS external owner write refuses stale save and retains input", flush=True)
        page.close()
        f.stop()
        if "--trace-files" in flags:
            lines = [line for path in f.root.glob("files-*.log") for line in path.read_text(errors="replace").splitlines()]
            assert not any("execve(" in line and "csc.dll" in line for line in lines)
            assert not any("openat(" in line and str(sample) in line and '.dll"' in line for line in lines)
            print("compiler invocations 0; project DLL opens 0", flush=True)
finally:
    f.stop()
    print("evidence", f.root, flush=True)
