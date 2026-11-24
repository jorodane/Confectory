"""Confirmed project-owned card and table in the installed Linux editor."""

import json
from pathlib import Path
import sys
import tempfile
import time
from urllib.request import Request, urlopen

from playwright.sync_api import expect, sync_playwright

from v821_home_recent_edits import attach, editor, home, make_project, open_project
from editor_logic_workflow import find_project_item
from editor_navigation import open_project_tools

NS = "Recent.Alpha"
WINDOW = NS + "::StockDesk"
WINDOW_TITLE = "Project-owned Stock Desk"
UNSUPPORTED = NS + "::OtherDesk"


def seed(package, root, *, checkout=None):
    (root / "profile").mkdir()
    catalog = []
    proof = root / "run-proof.txt"
    originals = {}

    for name in ("Alpha", "Bravo"):
        project, body = make_project(package, root, name, checkout=checkout)
        directory = project.parent
        title = "Local " + name
        source = project.read_text().replace("Recent." + name, NS).rstrip()[:-1]
        source += 'element Stock object "Stock.celem";\nelement StockSchema schema "StockSchema.celem";\n'
        (directory / "StockSchema.celem").write_text(
            f'schema {NS}::StockSchema {{ field Note single general string; }}\n')
        (directory / "Stock.celem").write_text(
            f'object {NS}::Stock {{ use schema {NS}::StockSchema; data Note = "{title} only"; }}\n')
        entry = directory / "Main.celem"
        entry_text = entry.read_text().replace("Recent." + name, NS)
        (directory / "MainBody.celem").write_text(
            (directory / "MainBody.celem").read_text().replace("Recent." + name, NS))
        # The same declaration bytes exist in both fixtures. Only A registers and reaches the view.
        (directory / "StockDesk.celem").write_text(
            f'view {WINDOW} {{ use object {NS}::Stock; value editorName = "{WINDOW_TITLE}"; '
            'value nodeIDs = "stock"; }\n')
        if name == "Alpha":
            source += 'element StockDesk view "StockDesk.celem";\n'
            source += 'element OtherDesk view "OtherDesk.celem";\n'
            (directory / "OtherDesk.celem").write_text(
                f'view {UNSUPPORTED} {{ use object {NS}::Stock; value editorName = "Unsupported renderer"; '
                'value editorWindow = "external-script"; }\n')
            entry_text = entry_text.replace("{", f"{{ use view {WINDOW};", 1)
        project.write_text(source + "}\n")
        entry.write_text(entry_text)
        body.write_text(f"System.IO.File.AppendAllText({json.dumps(str(proof))}, {json.dumps(name + chr(10))});\nreturn 0;\n")
        originals.update({path: path.read_bytes() for path in directory.iterdir()})
        catalog.append({"path": str(project), "title": title, "description": ""})

    listings = root / "profile" / "projects.json"
    listings.write_text(json.dumps(catalog, separators=(",", ":")))
    originals[listings] = listings.read_bytes()
    return catalog, originals, proof


def state(address):
    origin, token = address.split("/#")

    def send(payload):
        request = Request(origin + "/api/request", data=json.dumps(payload).encode(), headers={
            "Content-Type": "application/json", "X-Confectory-Session": token,
        })
        with urlopen(request, timeout=15) as reply:
            return json.load(reply)

    for _ in range(150):
        mounted = send({"op": "mount"})
        if mounted["ok"]:
            break
        assert mounted["error"]["code"] == "busy", mounted["error"]
        time.sleep(.04)
    else:
        raise AssertionError("The packaged editor did not become idle")
    try:
        return mounted["state"]
    finally:
        assert send({"op": "dispose", "view": mounted["view"]})["ok"]


def project_menu(page, approved=False):
    def lookup(response):
        if not response.url.endswith("/api/request") or response.request.method != "POST":
            return False
        body = response.request.post_data_json
        return body.get("endpoint") == "listProjectWindows" and response.json().get("ok") is True

    with page.expect_response(lookup) as pending:
        page.locator("#project-menu").click()
    reply = pending.value.json()
    assert reply.get("ok"), reply
    menu = page.locator(".context-menu")
    expect(menu.get_by_role("button", name="프로젝트 정보", exact=True)).to_be_visible()
    expect(menu.get_by_role("button", name="Unsupported renderer", exact=True)).to_have_count(0)
    slot = menu.locator(f'[data-project-owned-window="{WINDOW}"]')
    if approved:
        expect(slot).to_have_text(WINDOW_TITLE)
    else:
        assert not reply["result"].get("windows")
        expect(slot).to_have_count(0)
    return menu


def check_project_tools(page, *, approved=False):
    menu = project_menu(page, approved=approved)
    menu.get_by_role("button", name="프로젝트 도구", exact=True).click()
    tools = page.get_by_role("navigation", name="프로젝트 작업 공간")
    expect(tools).to_be_visible()
    for label in ("개념", "기능"):
        expect(tools.get_by_role("button", name=label, exact=True)).to_be_enabled()
    expect(tools).not_to_contain_text(WINDOW_TITLE)
    open_project_tools(page)
    expect(tools).to_be_hidden()


def stage_renderer(page, path, renderer, previous, *, add_input=False):
    before = path.read_bytes()
    page.locator("#project-menu").click()
    page.locator(".context-menu").get_by_role("button", name="팩 관리", exact=True).click()
    packs = page.locator('[data-key="packs"]')
    packs.get_by_text("프로젝트 창 선언", exact=True).click()
    packs.get_by_role("button", name=WINDOW, exact=True).click()
    expect(page.locator("#selection")).to_have_text(WINDOW)
    source = page.locator("#source")
    expect(source).to_be_visible()
    text = source.input_value()
    if add_input:
        text += "// Preserve this unconfirmed comment beside the menu setting.\n"
        source.fill(text)
    property_text = f'value editorWindow = "{previous}";'
    if previous:
        edited = text.replace(property_text,
                              f'value editorWindow = "{renderer}";' if renderer else "", 1)
    else:
        edited = text.replace(" }", f' value editorWindow = "{renderer}"; }}', 1)
    panel = page.locator("[data-project-window-setting]")
    panel.get_by_role("button", name="메뉴 표시 설정", exact=True).click()
    choices = panel.get_by_role("combobox", name="메뉴에 표시", exact=True)
    expect(choices).to_have_value(previous)
    assert choices.locator("option").all_text_contents() == ["표시 안 함", "읽기 전용 카드", "읽기 전용 표"]
    choices.select_option(renderer)
    panel.get_by_role("button", name="초안에 적용", exact=True).click()
    expect(source).to_have_value(edited)
    assert path.read_bytes() == before
    return edited


def open_review(page):
    page.locator("#review").click()
    review = page.locator('[data-key="review"]')
    expect(review.locator("#confirm")).to_be_visible()
    return review


def confirm_review(page):
    review = open_review(page)
    advanced = review.locator("[data-review-advanced]")
    if advanced.is_visible() and review.locator("#confirm").is_disabled():
        advanced.click()
        ack = review.locator("[data-advanced-reviewed]")
        if ack.is_visible():
            ack.check()
    review.locator("#confirm").click()
    expect(review).to_have_count(0)
    expect(page.locator("#status")).to_contain_text("최종 소스에 반영")


def change_renderer(page, path, renderer, previous, *, cancel_first=False):
    edited = stage_renderer(page, path, renderer, previous, add_input=cancel_first)
    if cancel_first:
        before = path.read_bytes()
        review = open_review(page)
        review.locator("[data-reject]").click()
        expect(review).to_have_count(0)
        expect(page.locator("#source")).to_have_value(edited)
        assert path.read_bytes() == before
        project_menu(page)
        page.keyboard.press("Escape")
    confirm_review(page)
    assert path.read_text() == edited
    return edited


def open_window(page, renderer, *, close=True):
    project_menu(page, approved=True).get_by_role("button", name=WINDOW_TITLE, exact=True).click()
    dialog = page.get_by_role("dialog", name=WINDOW_TITLE, exact=True)
    content = dialog.locator(f'[data-project-window-renderer="{renderer}"]')
    expect(content).to_contain_text("Note")
    expect(content).to_contain_text("Local Alpha only")
    expect(content).not_to_contain_text("Local Bravo only")
    expect(dialog.locator("textarea, input")).to_have_count(0)
    if close:
        dialog.get_by_role("button", name="닫기", exact=True).click()
        expect(dialog).to_have_count(0)


def check_builtins(page, title):
    find_project_item(page, NS + "::Stock", "개념")
    concept = page.locator('.window[data-key="schema"]')
    expect(concept.get_by_role("heading", name="Stock", exact=True)).to_be_visible()
    expect(concept.get_by_label("Note 기본값", exact=True)).to_have_value(title + " only")
    concept.get_by_role("button", name="창 닫기", exact=True).click()

    find_project_item(page, NS + "::Main", "기능")
    function = page.locator('.window[data-key="declaration"]')
    expect(function.locator(".object-title-name")).to_have_text("Main")
    function.get_by_role("button", name="창 닫기", exact=True).click()


def check_run(page, project, registered):
    title = project["title"]
    page.get_by_role("button", name="프로젝트 실행", exact=True).click()
    run = page.locator(".run-window:visible")
    expect(run.locator("[data-run-project]")).to_contain_text(title)
    expect(run.locator("[data-run-frame]")).to_have_text("종료 코드 0", timeout=120000)
    latest = Path(project["path"]).parent / ".confectory" / "outputs" / "linux" / "latest.json"
    report = json.loads(latest.read_text())
    linkage = json.loads(Path(report["publicCatalog"]).read_text())
    assert linkage["entry"] == NS + "::Main"
    owned = [element for element in linkage["elements"] if element["id"] == WINDOW]
    if registered:
        assert len(owned) == 1 and owned[0]["kind"] == "view"
        assert owned[0]["metadataValues"]["editorName"]["value"] == WINDOW_TITLE
    else:
        assert not owned


def workflow(package, root):
    projects, originals, proof = seed(package, root)
    ids = []
    with sync_playwright() as playwright:
        with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"],
                                        ignore_default_args=["--disable-dev-shm-usage"]) as browser:
            with editor(package, root, "installed-view-boundary") as address:
                page, errors = attach(browser, address)
                for index, project in enumerate(projects):
                    expect(page.locator(".home-grid")).to_be_visible()
                    expect(page.locator("#project-menu, #run, .nav-menu")).to_have_count(0)
                    expect(page.locator(".home-grid")).not_to_contain_text(WINDOW_TITLE)
                    assert not any(row["id"] == WINDOW for row in state(address)["units"])

                    open_project(page, project["title"])
                    current = state(address)
                    ids.append(current["projectId"])
                    registered = index == 0
                    assert not any(row["id"] == WINDOW for row in current["editorViews"])
                    check_project_tools(page)
                    if registered:
                        path = Path(project["path"]).with_name("StockDesk.celem")
                        change_renderer(page, path, "element-view-card", "", cancel_first=True)
                        open_window(page, "card")
                        expect_bytes = change_renderer(page, path, "element-view-table", "element-view-card").encode()
                        assert path.read_bytes() == expect_bytes
                        originals[path] = expect_bytes
                        open_window(page, "table")
                    check_builtins(page, project["title"])
                    expected = ["Alpha", "Bravo"][:index]
                    assert (proof.read_text().splitlines() if proof.exists() else []) == expected
                    check_run(page, project, registered)
                    assert proof.read_text().splitlines() == ["Alpha", "Bravo"][:index + 1]
                    expect(page.locator('body')).not_to_contain_text(str(root))
                    if registered:
                        open_window(page, "table", close=False)
                    home(page)
                    expect(page.get_by_role("dialog", name=WINDOW_TITLE, exact=True)).to_have_count(0)
                assert all(ids) and len(set(ids)) == 2
                assert not errors, errors
                page.close()

    assert all(path.read_bytes() == data for path, data in originals.items())
    print("PASS packaged Chromium confirmed card and table only in A, canceled review, Home/B scope, built-in editors and real Run")


def card_run_workflow(report, root, browser):
    checkout = Path(__file__).resolve().parents[2]
    (alpha, _), originals, proof = seed(report, root, checkout=checkout)
    path = Path(alpha["path"]).with_name("StockDesk.celem")
    with editor(report, root, "local-card-run", checkout=checkout) as address:
        page, errors = attach(browser, address)
        open_project(page, alpha["title"])
        expect(page.locator('[data-project-owned-window]')).to_have_count(0)
        card = change_renderer(page, path, "element-view-card", "", cancel_first=True)
        check_project_tools(page, approved=True)
        expect(page.locator('[data-project-owned-window]')).to_have_count(0)
        assert not proof.exists()
        open_window(page, "card", close=False)
        check_run(page, alpha, registered=True)
        expect(page.get_by_role("dialog", name=WINDOW_TITLE, exact=True)).to_be_visible()
        assert proof.read_bytes() == b"Alpha\n"
        assert not errors, errors
        page.close()

    originals[path] = card.encode()
    assert all(file.read_bytes() == value for file, value in originals.items())
    print("PASS Chromium canceled Review leaves no menu; confirmed card stays open during the one real Alpha Run")


def settings_workflow(package, root, browser):
    (alpha, bravo), originals, proof = seed(package, root)
    path = Path(alpha["path"]).with_name("StockDesk.celem")
    with editor(package, root, "window-settings") as address:
        page, errors = attach(browser, address)
        open_project(page, alpha["title"])
        card = change_renderer(page, path, "element-view-card", "", cancel_first=True)
        open_window(page, "card")
        table = stage_renderer(page, path, "element-view-table", "element-view-card")
        review = open_review(page)
        review.locator("[data-reject]").click()
        expect(review).to_have_count(0)
        assert path.read_text() == card
        expect(page.locator("#source")).to_have_value(table)
        open_window(page, "card")
        confirm_review(page)
        assert path.read_text() == table
        open_window(page, "table")
        assert not proof.exists() and not errors, errors
        print("PASS Chromium picker, draft preservation, canceled Review and confirmed card and table", flush=True)
        page.close()

    with editor(package, root, "window-settings-restart") as address:
        page, errors = attach(browser, address)
        open_project(page, alpha["title"])
        open_window(page, "table", close=False)
        check_run(page, alpha, registered=True)
        assert proof.read_bytes() == b"Alpha\n"
        page.get_by_role("dialog", name=WINDOW_TITLE, exact=True).get_by_role("button", name="닫기", exact=True).click()
        print("PASS cold editor reopen: confirmed table and real Alpha Run with the view still open", flush=True)
        hidden = stage_renderer(page, path, "", "element-view-table")
        open_window(page, "table")
        confirm_review(page)
        project_menu(page)
        page.keyboard.press("Escape")
        assert path.read_text() == hidden
        originals[path] = hidden.encode()
        home(page)
        open_project(page, bravo["title"])
        project_menu(page)
        assert not errors, errors
        page.close()

    assert all(path.read_bytes() == value for path, value in originals.items())
    print("PASS Chromium hide takes effect only after Confirm, Bravo remains isolated and unrelated sources are unchanged")


if __name__ == "__main__":
    package = Path(sys.argv[1]).resolve()
    expect.set_options(timeout=25000)
    with tempfile.TemporaryDirectory(prefix="project-owned-view-") as directory:
        if {"--settings", "--card-run"} & set(sys.argv[2:]):
            with sync_playwright() as playwright:
                with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"],
                                                ignore_default_args=["--disable-dev-shm-usage"]) as browser:
                    if "--card-run" in sys.argv[2:]:
                        card_run_workflow(package, Path(directory), browser)
                    else:
                        settings_workflow(package, Path(directory), browser)
        else:
            workflow(package, Path(directory))
