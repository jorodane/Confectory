"""Confirmed project-owned card and table in the installed Linux editor."""

import json
import os
import subprocess
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
    (root / "profile").mkdir(exist_ok=True)
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


def project_menu(page, approved=False, *, identifier=WINDOW, title=WINDOW_TITLE):
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
    slot = menu.locator(f'[data-project-owned-window="{identifier}"]')
    if approved:
        expect(slot).to_have_text(title)
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


def select_registered_view(page, identifier):
    page.locator("#project-menu").click()
    page.locator(".context-menu").get_by_role("button", name="팩 관리", exact=True).click()
    packs = page.locator('[data-key="packs"]')
    packs.get_by_text("프로젝트 창 선언", exact=True).click()
    packs.get_by_role("button", name=identifier, exact=True).click()
    expect(page.locator("#selection")).to_have_text(identifier)
    source = page.locator("#source")
    expect(source).to_be_visible()
    return source


def stage_renderer(page, path, renderer, previous, *, add_input=False):
    before = path.read_bytes()
    source = select_registered_view(page, WINDOW)
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
    choices = panel.get_by_role("combobox", name="≡ 메뉴에 표시", exact=True)
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


def card_refresh_workflow(report, root, browser):
    checkout = Path(__file__).resolve().parents[2]
    (alpha, _), originals, proof = seed(report, root, checkout=checkout)
    path = Path(alpha["path"]).with_name("StockDesk.celem")
    initial = path.read_text().replace(" }", ' value editorWindow = "element-view-card"; }', 1)
    path.write_text(initial)
    writer_root = root / "writer"
    writer_profile = writer_root / "profile"
    writer_profile.mkdir(parents=True)
    (writer_profile / "projects.json").write_text(json.dumps([alpha]))

    with editor(report, root, "card-reader", checkout=checkout) as reader_address, \
            editor(report, writer_root, "card-writer", checkout=checkout) as writer_address:
        assert reader_address.split("/#")[0] != writer_address.split("/#")[0]
        reader, reader_errors = attach(browser, reader_address)
        writer, writer_errors = attach(browser, writer_address)
        open_project(reader, alpha["title"])
        open_project(writer, alpha["title"])
        assert state(reader_address)["projectId"] == state(writer_address)["projectId"]
        open_window(reader, "card", close=False)
        card = reader.get_by_role("dialog", name=WINDOW_TITLE, exact=True)

        hidden = stage_renderer(writer, path, "", "element-view-card")
        review = open_review(writer)
        review.locator("[data-reject]").click()
        expect(review).to_have_count(0)
        expect(writer.locator("#source")).to_have_value(hidden)
        assert path.read_text() == initial
        project_menu(reader, approved=True)
        reader.keyboard.press("Escape")
        expect(card).to_be_visible()

        confirm_review(writer)
        assert path.read_text() == hidden
        expect(card).to_be_visible()
        project_menu(reader)
        expect(card).to_have_count(0)
        assert not reader_errors and not writer_errors, (reader_errors, writer_errors)
        reader.close()
        writer.close()

    assert not proof.exists()
    originals[path] = hidden.encode()
    assert all(file.read_bytes() == value for file, value in originals.items())
    print("PASS two local Chromium editor sessions: cancel keeps the card; Confirm and manual menu refresh remove it")


def main_view_workflow(report, root, browser):
    checkout = Path(__file__).resolve().parents[2]
    (alpha, bravo), originals, proof = seed(report, root, checkout=checkout)
    path = Path(alpha["path"]).with_name("StockDesk.celem")
    initial = path.read_text().replace(" }", ' value editorWindow = "element-view-card"; }', 1)
    path.write_text(initial)
    # Bravo has the same View ID on disk and a registered but invalid main View.
    bravo_manifest = Path(bravo["path"])
    bravo_manifest.write_text(bravo_manifest.read_text().rstrip()[:-1] +
                              'element InvalidMain view "InvalidMain.celem";\n}\n')
    invalid = bravo_manifest.with_name("InvalidMain.celem")
    invalid.write_text(f'view {NS}::InvalidMain {{ use object {NS}::Missing; value editorName = "Invalid"; '
                       'value editorMain = "element-view-card"; }\n')
    originals[bravo_manifest] = bravo_manifest.read_bytes()
    originals[invalid] = invalid.read_bytes()

    with editor(report, root, "project-main-view", checkout=checkout) as address:
        page, errors = attach(browser, address)
        surface = page.locator("#workspace > [data-project-main-view]")

        def enter(title):
            with page.expect_response(lambda response: response.request.method == "POST"
                                      and response.url.endswith("/api/request")
                                      and (response.request.post_data_json or {}).get("endpoint")
                                      == "readProjectMainView") as pending:
                open_project(page, title)
            return pending.value.json()["result"]

        assert enter(alpha["title"])["status"] == "unavailable"
        expect(surface).to_have_count(0)
        source = select_registered_view(page, WINDOW)
        pending_text = initial + "// Pending workspace explanation must survive.\n"
        source.fill(pending_text)

        def opening_picker(previous, tab=page):
            tab.get_by_role("button", name="프로젝트 시작 화면 설정", exact=True).click()
            picker = tab.get_by_role("combobox", name="프로젝트 시작 화면", exact=True)
            expect(picker).to_have_value(previous)
            assert picker.locator("option").all_text_contents() == ["기본 화면", "읽기 전용 카드", "읽기 전용 표"]
            return picker

        opening_picker("").select_option("element-view-table")
        page.get_by_role("button", name="초안에 적용", exact=True).click()
        proposal = pending_text.replace(" }", ' value editorMain = "element-view-table"; }', 1)
        expect(source).to_have_value(proposal)
        assert path.read_text() == initial
        review = open_review(page)
        review.locator("[data-reject]").click()
        expect(review).to_have_count(0)
        expect(page.locator("#source")).to_have_value(proposal)
        assert path.read_text() == initial
        expect(surface).to_have_count(0)

        confirm_review(page)
        assert path.read_text() == proposal
        other_root = root / "opening-conflict"
        (other_root / "profile").mkdir(parents=True)
        (other_root / "profile" / "projects.json").write_text(json.dumps([alpha]))
        with editor(report, other_root, "opening-conflict", checkout=checkout) as other_address:
            other_page, other_errors = attach(browser, other_address)
            open_project(other_page, alpha["title"])
            other = select_registered_view(other_page, UNSUPPORTED)
            original_other = other.input_value()
            blocked = opening_picker("", other_page)
            expect(other_page.get_by_text(WINDOW + "의 시작 화면 지정을 먼저 해제하고 확정하세요.",
                                          exact=True)).to_be_visible()
            assert blocked.locator('option[value="element-view-card"]').evaluate("option => option.disabled")
            assert blocked.locator('option[value="element-view-table"]').evaluate("option => option.disabled")
            expect(other).to_have_value(original_other)
            assert not other_errors, other_errors
            other_page.close()

        home(page)
        expect(surface).to_have_count(0)
        assert enter(bravo["title"])["status"] == "unavailable"
        expect(surface).to_have_count(0)
        home(page)
        assert enter(alpha["title"])["window"]["renderer"] == "element-view-table"
        expect(surface).to_be_visible()
        expect(surface).to_have_attribute("data-project-main-view", WINDOW)
        expect(surface.locator("table")).to_contain_text("Local Alpha only")
        expect(surface.locator("input, textarea, button")).to_have_count(0)
        assert surface.locator("h2").evaluate("""heading => {
            const bounds = heading.getBoundingClientRect();
            return document.elementFromPoint(bounds.x + bounds.width / 2, bounds.y + bounds.height / 2)
                ?.closest('[data-project-main-view]') === heading.parentElement;
        }"""), "The main View must be on the visible workspace surface"
        open_window(page, "card")
        expect(surface.locator("table")).to_be_visible()
        source = select_registered_view(page, WINDOW)
        picker = opening_picker("element-view-table")
        picker.select_option("")
        page.get_by_role("button", name="초안에 적용", exact=True).click()
        cleared = proposal.replace('value editorMain = "element-view-table";', '', 1)
        expect(source).to_have_value(cleared)
        assert path.read_text() == proposal
        confirm_review(page)
        home(page)
        assert enter(alpha["title"])["status"] == "unavailable"
        expect(surface).to_have_count(0)
        open_window(page, "card")
        assert not proof.exists() and not errors, errors
        page.close()

    originals[path] = cleared.encode()
    assert all(file.read_bytes() == value for file, value in originals.items())
    print("PASS Chromium opening View picker: cancellation, confirmation, conflict, reset, menu independence and draft retention")


def stage_worker_opening_fixture(checkout, alpha):
    test_host = checkout / "tests/Confectory.Tests/bin/Release/net10.0/Confectory.Tests.dll"
    result = subprocess.run(
        [os.environ.get("CONFECTORY_DOTNET", "dotnet"), str(test_host), "--require-runtime",
         "test_worker_origin_opening_view_draft_requires_human_confirm"],
        env=dict(os.environ, CONFECTORY_TEST_OPENING_VIEW_BROWSER_FIXTURE="1",
                 CONFECTORY_TEST_AUTHOR_PROJECT=alpha["path"]),
        capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def worker_opening_review_workflow(report, root, browser):
    checkout = Path(__file__).resolve().parents[2]
    (alpha, _), originals, proof = seed(report, root, checkout=checkout)
    path = Path(alpha["path"]).with_name("StockDesk.celem")
    initial = path.read_text()
    with editor(report, root, "opening-review-identity", checkout=checkout) as address:
        page, errors = attach(browser, address)
        open_project(page, alpha["title"])
        assert not errors
        page.close()

    stage_worker_opening_fixture(checkout, alpha)
    assert path.read_text() == initial

    with editor(report, root, "opening-review-browser", checkout=checkout) as address:
        page, errors = attach(browser, address)
        open_project(page, alpha["title"])
        surface = page.locator("#workspace > [data-project-main-view]")
        expect(surface).to_have_count(0)
        source = select_registered_view(page, WINDOW)
        draft = source.input_value()
        assert draft != initial and 'editorMain = "element-view-card"' in draft
        review = open_review(page)
        change = review.get_by_role("group", name="프로젝트 시작 화면", exact=True)
        expect(change.get_by_role("group", name="변경 전")).to_have_text("기본 화면")
        expect(change.get_by_role("group", name="변경 후")).to_have_text("읽기 전용 카드")
        expect(review.locator("[data-opening-view-origin]")).to_have_text(
            "작업자 제안 · synthetic-worker · 작업 task-opening-view")
        review.locator("[data-reject]").click()
        expect(review).to_have_count(0)
        expect(source).to_have_value(draft)
        assert path.read_text() == initial
        home(page)
        open_project(page, alpha["title"])
        expect(surface).to_have_count(0)
        select_registered_view(page, WINDOW)
        confirm_review(page)
        assert path.read_text() == draft
        home(page)
        open_project(page, alpha["title"])
        expect(surface.locator("dl")).to_contain_text("Local Alpha only")
        assert not proof.exists() and not errors, errors
        page.close()

    originals[path] = draft.encode()
    assert all(file.read_bytes() == value for file, value in originals.items())
    print("PASS Chromium shows the exact Worker-origin opening View Review; Cancel keeps the default, Confirm opens the Alpha card")


def seed_recipe(report, root, checkout, *, both=False):
    (alpha, bravo), originals, proof = seed(report, root, checkout=checkout)
    title, identifier = "Assembly recipe", NS + "::RecipeDesk"
    for project, amount in ((alpha, 2), (bravo, 7)):
        manifest = Path(project["path"])
        directory = manifest.parent
        ingredients = json.dumps({NS + "::Fiber": amount, NS + "::Tile": 3})
        declarations = {
            "Fiber": ("object", f"object {NS}::Fiber {{}}"),
            "Tile": ("object", f"object {NS}::Tile {{}}"),
            "Panel": ("object", f"object {NS}::Panel {{}}"),
            "Assembly": ("object", f'object {NS}::Assembly {{ value concept = "recipe"; '
                         f'value ingredients = {json.dumps(ingredients)}; value output = "{NS}::Panel"; value outputCount = 4; }}'),
            "RecipeDesk": ("view", f'view {identifier} {{ use object {NS}::Assembly; value editorName = "{title}"; }}'),
        }
        source = manifest.read_text().rstrip()[:-1]
        for name, (kind, body) in declarations.items():
            path = directory / (name + ".celem")
            path.write_text(body + "\n")
            originals[path] = path.read_bytes()
            if name != "RecipeDesk" or project == alpha or both:
                source += f'element {name} {kind} "{name}.celem";\n'
        manifest.write_text(source + "}\n")
        originals[manifest] = manifest.read_bytes()

    return alpha, bravo, originals, proof, title, identifier


def recipe_view_workflow(report, root, browser):
    checkout = Path(__file__).resolve().parents[2]
    alpha, bravo, originals, proof, title, identifier = seed_recipe(report, root, checkout)
    path = Path(alpha["path"]).with_name("RecipeDesk.celem")
    initial = path.read_text()
    with editor(report, root, "recipe-view", checkout=checkout) as address:
        page, errors = attach(browser, address)
        open_project(page, alpha["title"])
        source = select_registered_view(page, identifier)
        scope = page.locator("[data-project-window-setting]")
        scope.get_by_role("button", name="메뉴 표시 설정", exact=True).click()
        choices = scope.get_by_role("combobox", name="≡ 메뉴에 표시", exact=True)
        expect(choices).to_have_value("")
        assert choices.locator("option").all_text_contents() == ["표시 안 함", "읽기 전용 레시피"]
        choices.select_option("element-view-recipe")
        scope.get_by_role("button", name="초안에 적용", exact=True).click()
        draft = initial.replace(" }", ' value editorWindow = "element-view-recipe"; }', 1)
        expect(source).to_have_value(draft)
        review = open_review(page)
        review.locator("[data-reject]").click()
        expect(review).to_have_count(0)
        assert path.read_text() == initial
        project_menu(page, identifier=identifier)
        page.keyboard.press("Escape")
        confirm_review(page)
        assert path.read_text() == draft

        project_menu(page, True, identifier=identifier, title=title).get_by_role(
            "button", name=title, exact=True).click()
        dialog = page.get_by_role("dialog", name=title, exact=True)
        recipe = dialog.locator('[data-project-window-renderer="recipe"]')
        inputs = recipe.locator("section").filter(has=page.get_by_role("heading", name="재료", exact=True))
        results = recipe.locator("section").filter(has=page.get_by_role("heading", name="결과", exact=True))
        expect(inputs.locator("li")).to_have_text([NS + "::Fiber × 2", NS + "::Tile × 3"])
        expect(results.locator("li")).to_have_text([NS + "::Panel × 4"])
        expect(recipe.locator("input, button, textarea, select")).to_have_count(0)
        home(page)
        expect(dialog).to_have_count(0)
        open_project(page, alpha["title"])
        expect(page.locator("#workspace > [data-project-main-view]")).to_have_count(0)
        home(page)
        open_project(page, bravo["title"])
        project_menu(page, identifier=identifier)
        expect(page.locator("[data-project-main-view], [data-project-window-renderer=recipe]")).to_have_count(0)
        assert not proof.exists() and not errors, errors
        page.close()

    originals[path] = draft.encode()
    assert all(file.read_bytes() == value for file, value in originals.items())
    print("PASS confirmed recipe shows owned ingredients and result separately; cancel, Home, Bravo and default Workspace remain isolated")


def recipe_editor_workflow(report, root, browser):
    checkout = Path(__file__).resolve().parents[2]
    alpha, bravo, originals, proof, title, identifier = seed_recipe(report, root, checkout, both=True)
    target = NS + "::Assembly"
    for project in (alpha, bravo):
        path = Path(project["path"]).with_name("RecipeDesk.celem")
        path.write_text(path.read_text().replace(" }", ' value editorWindow = "element-view-recipe"; }', 1))
        originals[path] = path.read_bytes()

    def recipe_dialog(page):
        project_menu(page, True, identifier=identifier, title=title).get_by_role(
            "button", name=title, exact=True).click()
        return page.get_by_role("dialog", name=title, exact=True)

    def snapshots(project):
        folder = Path(project["path"]).parent
        candidates = folder.glob(".confectory/edit-workspaces/*/draft.json")
        return {path: path.read_bytes() for path in candidates}

    with editor(report, root, "recipe-editor", checkout=checkout) as address:
        page, errors = attach(browser, address)
        open_project(page, alpha["title"])
        stock = select_registered_view(page, WINDOW)
        stock.fill(stock.input_value() + "// Keep this unrelated saved draft.\n")
        page.locator("#save").click()
        expect(page.locator("#status")).to_contain_text("Draft saved")
        assert snapshots(alpha), "The navigation check needs an existing saved draft"

        for project, count in ((alpha, 2), (bravo, 7)):
            before = snapshots(project)
            dialog = recipe_dialog(page)
            expect(dialog.locator('[data-project-window-renderer="recipe"]')).to_contain_text(
                f"{NS}::Fiber × {count}")
            dialog.get_by_role("button", name="레시피 편집기 열기", exact=True).click()
            expect(dialog).to_have_count(0)
            fallback = page.locator('.window[data-key="schema"]')
            expect(fallback).to_be_visible()
            expect(fallback.get_by_role("heading", name="Assembly", exact=True)).to_be_visible()
            selected = state(address)["draft"]
            assert selected["id"] == target and not selected["dirty"]
            assert selected["text"] == Path(project["path"]).with_name("Assembly.celem").read_text()
            assert snapshots(project) == before
            assert all(path.read_bytes() == value for path, value in originals.items())
            if project == alpha:
                home(page)
                open_project(page, bravo["title"])

        page.locator('.window[data-key="schema"]').get_by_role("button", name="창 닫기", exact=True).click()
        dialog = recipe_dialog(page)
        target_link = dialog.get_by_role("button", name="레시피 편집기 열기", exact=True)
        expect(target_link).to_be_visible()
        before = snapshots(bravo)
        manifest = Path(bravo["path"])
        # Remove only the disposable target's registration while its old card is open.
        manifest.write_text(manifest.read_text().replace('element Assembly object "Assembly.celem";\n', ""))
        originals[manifest] = manifest.read_bytes()
        target_link.click()
        expect(page.get_by_text("현재 프로젝트에서 이 창을 열 수 없어요.", exact=True)).to_be_visible()
        expect(page.locator('.window[data-key="schema"]:visible')).to_have_count(0)
        assert snapshots(bravo) == before and not proof.exists() and not errors, errors
        page.close()

    assert all(path.read_bytes() == value for path, value in originals.items())
    print("PASS recipe editor link opens only the current registered object, keeps saved drafts, and rejects revocation")



def recipe_quantity_workflow(report, root, browser):
    checkout = Path(__file__).resolve().parents[2]
    alpha, bravo, originals, proof, title, identifier = seed_recipe(report, root, checkout, both=True)
    target = NS + "::Assembly"
    alpha_recipe = Path(alpha["path"]).with_name("Assembly.celem")
    for project in (alpha, bravo):
        path = Path(project["path"]).with_name("RecipeDesk.celem")
        path.write_text(path.read_text().replace(" }", ' value editorWindow = "element-view-recipe"; }', 1))
        originals[path] = path.read_bytes()

    def recipe_dialog(page, fiber, panel):
        project_menu(page, True, identifier=identifier, title=title).get_by_role(
            "button", name=title, exact=True).click()
        dialog = page.get_by_role("dialog", name=title, exact=True)
        expect(dialog.get_by_role("listitem")).to_have_text(
            [f"{NS}::Fiber × {fiber}", f"{NS}::Tile × 3", f"{NS}::Panel × {panel}"])
        expect(dialog.locator("input")).to_have_count(0)
        return dialog

    with editor(report, root, "recipe-quantity", checkout=checkout) as address:
        page, errors = attach(browser, address)
        open_project(page, alpha["title"])
        dialog = recipe_dialog(page, 2, 4)
        dialog.get_by_role("button", name="레시피 편집기 열기", exact=True).click()
        fallback = page.locator('.window[data-key="schema"]')
        expect(fallback.get_by_role("heading", name="Assembly", exact=True)).to_be_visible()
        quantities = fallback.locator("[data-recipe-quantities]")
        fiber = quantities.get_by_role("spinbutton", name=f"{NS}::Fiber 수량")
        tile = quantities.get_by_role("spinbutton", name=f"{NS}::Tile 수량")
        panel = quantities.get_by_role("spinbutton", name=f"{NS}::Panel 수량")
        apply_ingredients = quantities.get_by_role("button", name="재료 수량을 초안에 적용")
        expect(fiber).to_have_value("2")
        expect(fallback.locator('[data-element-action="save"]')).to_be_disabled()
        for invalid in ("0", "101", "2.5"):
            fiber.fill(invalid)
            apply_ingredients.click()
            assert not fiber.evaluate("(input) => input.validity.valid")
            assert not state(address)["draft"]["dirty"]
        fiber.fill("5")
        panel.fill("6")
        apply_ingredients.click()
        expect(page.locator("#status")).to_contain_text("재료 수량을 초안에 적용했습니다.")
        expect(panel).to_have_value("6")
        expect(tile).to_have_value("3")
        quantities.get_by_role("button", name="결과 수량을 초안에 적용").click()
        expect(page.locator("#status")).to_contain_text("결과 수량을 초안에 적용했습니다.")
        assert "value outputCount = 6;" in state(address)["draft"]["text"]
        save = fallback.locator('[data-element-action="save"]')
        save.click()
        expect(page.locator("#project-menu")).to_be_enabled()
        expect(save).to_be_disabled()
        assert any(Path(alpha["path"]).parent.glob(".confectory/edit-workspaces/*/draft.json"))
        assert alpha_recipe.read_bytes() == originals[alpha_recipe]
        recipe_dialog(page, 2, 4).get_by_role("button", name="닫기", exact=True).click()
        fallback.locator('[data-element-action="confirm"]').click()
        review = page.locator('[data-key="review"]')
        expect(review.locator("#confirm")).to_be_enabled()
        review.locator("[data-reject]").click()
        recipe_dialog(page, 2, 4).get_by_role("button", name="닫기", exact=True).click()
        fallback.locator('[data-element-action="confirm"]').click()
        review.locator("#confirm").click()
        expect(review).to_have_count(0)
        dialog = recipe_dialog(page, 5, 6)
        dialog.get_by_role("button", name="닫기", exact=True).click()
        assert all(path.read_bytes() == value for path, value in originals.items() if path != alpha_recipe)
        assert state(address)["draft"]["id"] == target
        home(page)
        open_project(page, bravo["title"])
        recipe_dialog(page, 7, 4)
        expect(page.locator("[data-recipe-quantities]")).to_have_count(0)
        assert not proof.exists() and not errors, errors
        page.close()

    print("PASS Chromium recipe quantity draft, validation, Review cancel/Confirm and other-project isolation")


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
        if {"--settings", "--card-run", "--card-refresh", "--main-view", "--worker-opening-review", "--recipe-view", "--recipe-editor", "--recipe-quantity"} & set(sys.argv[2:]):
            with sync_playwright() as playwright:
                with playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"],
                                                ignore_default_args=["--disable-dev-shm-usage"]) as browser:
                    if "--card-run" in sys.argv[2:]:
                        card_run_workflow(package, Path(directory), browser)
                    elif "--card-refresh" in sys.argv[2:]:
                        card_refresh_workflow(package, Path(directory), browser)
                    elif "--main-view" in sys.argv[2:]:
                        main_view_workflow(package, Path(directory), browser)
                    elif "--worker-opening-review" in sys.argv[2:]:
                        worker_opening_review_workflow(package, Path(directory), browser)
                    elif "--recipe-view" in sys.argv[2:]:
                        recipe_view_workflow(package, Path(directory), browser)
                    elif "--recipe-quantity" in sys.argv[2:]:
                        recipe_quantity_workflow(package, Path(directory), browser)
                    elif "--recipe-editor" in sys.argv[2:]:
                        recipe_editor_workflow(package, Path(directory), browser)
                    else:
                        settings_workflow(package, Path(directory), browser)
        else:
            workflow(package, Path(directory))
