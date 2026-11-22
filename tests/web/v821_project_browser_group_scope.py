"""Check independent Project Browser locations against two real EditorHome projects."""
import json

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture


owner_namespace = "Example.FrameLoop"
foreign_namespace = "BrowserProbe.External"
foreign_id = foreign_namespace + "::TwinExternal"
category_id = owner_namespace + "::TwinCategory"
feature_id = owner_namespace + "::TwinFunction"
module_id = owner_namespace + "::TwinModule"

foreign_pack = fixture.root / "foreign"
foreign_pack.mkdir()
foreign_manifest = foreign_pack / "pack.cpack"
foreign_manifest.write_text(
    f'pack {foreign_namespace} version "1" {{element TwinExternal concept "External.celem";}}'
)
(foreign_pack / "External.celem").write_text(f'concept {foreign_id} {{description "Registered concept";}}')
for project, label in zip(fixture.projects, ("First", "Second")):
    declarations = {
        "TwinCategory": ("category", f'category {category_id} {{ description "{label} category"; }}'),
        "TwinConcept": ("object", f'object {owner_namespace}::TwinConcept {{ description "{label} concept"; }}'),
        "TwinFunction": ("function", f'function {feature_id} () -> int {{ description "{label} function"; }}'),
        "TwinModule": ("module", f'module {module_id} {{ description "{label} module"; }}'),
    }
    manifest = project.read_text().rstrip()
    for name, (kind, source) in declarations.items():
        file = project.parent / (name + ".celem")
        file.write_text(source)
        fixture.before[str(file)] = file.read_bytes()
    project.write_text(manifest[:-1] + f'registry {foreign_namespace} "{foreign_manifest}";' +
                       f'dependency {foreign_namespace} version "1";' +
                       "".join(f'element {name} {kind} "{name}.celem";' for name, (kind, _) in declarations.items()) + "}")
    fixture.before[str(project)] = project.read_bytes()

for file in (foreign_manifest, foreign_pack / "External.celem"):
    fixture.before[str(file)] = file.read_bytes()
profile = fixture.root / "profile"
profile.mkdir(exist_ok=True)
(profile / "projects.json").write_text(json.dumps([
    {"path": str(project), "title": label, "description": ""}
    for project, label in zip(fixture.projects, ("Browser First", "Browser Second"))
]))


def open_browser(page):
    page.locator("#title").click()
    page.locator(".context-menu").get_by_role("button", name="프로젝트 브라우저", exact=True).click()
    window = page.locator('.window[data-key="browser"]')
    expect(window).to_be_visible()
    return window


def query(window):
    return window.locator('[data-browser-control="object-query"]')


def group(window, value):
    window.locator(f'[data-tab="{value}"]').click()
    expect(window.locator("[data-tab].selected")).to_have_attribute("data-tab", value)
    expect(query(window)).to_be_enabled()


def find(window, text, expected):
    query(window).fill(text)
    query(window).press("Enter")
    expect(window.locator("[data-object]")).to_have_count(len(expected))
    for identifier in expected:
        expect(window.locator(f'[data-object="{identifier}"]')).to_be_visible()


def module_declaration(page):
    heading = page.locator("[data-declaration-id]").filter(has_text=module_id)
    declaration = page.locator(".window").filter(has=heading)
    expect(declaration.locator("[data-declaration-id]")).to_have_text(module_id)
    return declaration


def open_project(page, name):
    page.evaluate("() => globalThis.confectoryFlushPresentation()")
    page.locator(".brand").click()
    expect(page.locator(".home-grid")).to_be_visible()
    enter_project(page, name)


def enter_project(page, name):
    page.locator(".project-card").filter(has=page.get_by_role("heading", name=name, exact=True)).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(name)
    expect(page.get_by_role("tab", name="Workspace", exact=True)).to_be_visible()


def verify_leave_during_browser_status(page):
    description = module_declaration(page).locator('[data-decl-property="description"]')
    chat = page.locator("#chat-input")
    pending = "First module unapplied input"
    draft = "First project local chat draft"
    endpoint = fixture.origin + "/api/request"
    chat_attempts = {}
    chat_results = {}
    fail_checkpoint = True
    checkpoint_failed = False
    race = None
    raced_request = None
    competing_draft = "Draft saved from another mounted view"

    def gate(route):
        nonlocal checkpoint_failed, raced_request
        body = route.request.post_data_json
        operation = body.get("endpoint") if body.get("op") == "invoke" else None
        if operation == "savePresentation" and fail_checkpoint:
            checkpoint_failed = True
            route.fulfill(json={"ok": False, "error": {"code": "test_checkpoint_failed"}})
            return
        if operation == "chatDraft" and race:
            request_id = body["requestId"]
            chat_attempts[request_id] = body["input"]["value"]
            if raced_request is None:
                raced_request = request_id
                # Complete a real operation before the held request reaches the host.
                # The client request keeps its original expected revision.
                operation, payload = (
                    ("browserDrafts", {"action": "status", "ids": [module_id]})
                    if race == "browser-status"
                    else ("chatDraft", {"value": competing_draft})
                )
                fixture.call(operation, payload)
        route.fallback()

    def observe(response):
        if response.url != endpoint or response.request.post_data_json.get("op") != "update":
            return
        for result in response.json().get("results", []):
            if result["requestId"] in chat_attempts:
                chat_results[result["requestId"]] = result

    page.route(endpoint, gate)
    page.on("response", observe)
    try:
        description.fill(pending)
        before_leave = len([row for row in fixture.requests if row["endpoint"] == "leaveProject"])
        page.locator(".brand").click()
        expect(page.locator("#status")).to_contain_text("test_checkpoint_failed")
        expect(page.locator("#title")).to_contain_text("Browser First")
        expect(description).to_have_value(pending)
        assert checkpoint_failed
        assert len([row for row in fixture.requests if row["endpoint"] == "leaveProject"]) == before_leave
        fixture.checked("A failed workspace checkpoint keeps the project open and the unapplied input intact")
        fail_checkpoint = False

        chat.fill(draft)
        race = "browser-status"
        page.locator(".brand").click()
        page.wait_for_function(
            """() => !!document.querySelector('.home-grid') ||
                document.querySelector('#status')?.textContent === 'stale_revision'"""
        )
        assert raced_request and chat_results[raced_request]["error"]["code"] == "stale_revision", chat_results
        fixture.checked("The real host rejected the held chat draft at transport admission")
        expect(page.locator(".home-grid")).to_be_visible()
        assert len(chat_attempts) >= 2 and set(chat_attempts.values()) == {draft}, chat_attempts
        assert [row["ok"] for row in chat_results.values()].count(True) == 1, chat_results

        race = None
        enter_project(page, "Browser Second")
        expect(chat).to_have_value("")
        window = open_browser(page)
        group(window, "module")
        find(window, "Twin", [module_id])
        window.locator(f'[data-object="{module_id}"]').click()
        second = module_declaration(page)
        expect(second.locator('[data-decl-property="description"]')).to_have_value("Second module")
        second.locator(".window-title [data-close]").click()
        open_project(page, "Browser First")
        expect(chat).to_have_value(draft)
        expect(module_declaration(page).locator('[data-decl-property="description"]')).to_have_value(pending)
        fixture.original()
        fixture.checked("Home navigation and re-entry restore the first project's layout and inputs without changing the second project")

        race = "competing-draft"
        raced_request = None
        chat_attempts.clear()
        chat_results.clear()
        unsaved_chat = "Local input to preserve when draft changed"
        chat.fill(unsaved_chat)
        before_leave = len([row for row in fixture.requests if row["endpoint"] == "leaveProject"])
        page.locator(".brand").click()
        expect(page.locator("#status")).to_contain_text("저장된 프로젝트 대화 초안이 바뀌었습니다")
        assert raced_request and chat_results[raced_request]["error"]["code"] == "stale_revision", chat_results
        assert list(chat_attempts.values()) == [unsaved_chat], chat_attempts
        assert len([row for row in fixture.requests if row["endpoint"] == "leaveProject"]) == before_leave
        assert fixture.state()["chatDraft"] == competing_draft
        expect(page.locator("#title")).to_contain_text("Browser First")
        expect(chat).to_have_value(unsaved_chat)
        expect(module_declaration(page).locator('[data-decl-property="description"]')).to_have_value(pending)
        fixture.original()
        fixture.checked("A competing saved draft blocks navigation without overwriting either draft or module input")
    finally:
        page.unroute(endpoint, gate)
        page.remove_listener("response", observe)


try:
    fixture.start(0)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
        page = fixture.setup(browser)
        try:
            window = open_browser(page)
            tree = window.locator(".browser-folder-tree")
            if not tree.is_visible():
                window.locator("[data-browser-detail]").click()
            expect(tree.locator(f'[data-tree-id="{category_id}"]')).to_be_visible()
            registered = tree.locator(f'[data-namespace="{foreign_namespace}"]')
            if not registered.is_visible():
                tree.locator('[data-tree-toggle="ns:BrowserProbe"]').click()
            registered.click()
            find(window, "Twin", [foreign_id])
            query(window).fill("Concept input A")
            fixture.checked("Concept search is scoped to its selected registered namespace")

            group(window, "feature")
            expect(query(window)).to_have_value("")
            find(window, "Twin", [feature_id])
            query(window).fill("Feature input A")
            group(window, "module")
            expect(query(window)).to_have_value("")
            find(window, "Twin", [module_id])
            group(window, "concept")
            expect(query(window)).to_have_value("Concept input A")
            expect(window.locator(f'[data-object="{foreign_id}"]')).to_be_visible()
            expect(tree.locator(f'[data-namespace="{foreign_namespace}"]')).to_have_attribute("aria-current", "location")
            group(window, "feature")
            expect(query(window)).to_have_value("Feature input A")
            expect(window.locator(f'[data-object="{feature_id}"]')).to_be_visible()
            fixture.checked("New function and module groups start at their own roots, with a scoped return to Concept")

            group(window, "module")
            expect(query(window)).to_have_value("Twin")
            window.locator(f'[data-object="{module_id}"]').click()
            declaration = module_declaration(page)
            description = declaration.locator('[data-decl-property="description"]')
            expect(description).to_have_value("First module")
            description.fill("Saved First module draft")
            declaration.locator("[data-properties-apply]").click()
            expect(page.locator("#status")).to_contain_text("공유 초안 갱신")
            declaration.locator("[data-declaration-save]").click()
            expect(page.locator("#status")).to_have_text("Draft saved; final sources unchanged")
            declaration.locator(".window-title [data-close]").click()
            group(window, "concept")

            open_project(page, "Browser Second")
            window = open_browser(page)
            expect(query(window)).to_have_value("")
            group(window, "module")
            find(window, "Twin", [module_id])
            window.locator(f'[data-object="{module_id}"]').click()
            declaration = module_declaration(page)
            expect(declaration.locator('[data-decl-property="description"]')).to_have_value("Second module")
            declaration.locator(".window-title [data-close]").click()
            open_project(page, "Browser First")
            window = open_browser(page)
            expect(window.locator("[data-tab].selected")).to_have_attribute("data-tab", "concept")
            expect(query(window)).to_have_value("Concept input A")
            expect(window.locator(f'[data-object="{foreign_id}"]')).to_be_visible()
            group(window, "module")
            expect(window.locator(f'[data-object="{module_id}"]')).to_be_visible()
            window.locator(f'[data-object="{module_id}"]').click()
            expect(module_declaration(page).locator('[data-decl-property="description"]')).to_have_value("Saved First module draft")
            fixture.original()
            assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
            fixture.checked("The two projects keep their browser positions and saved module drafts separate")
            verify_leave_during_browser_status(page)
            assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
        except Exception:
            page.screenshot(path=str(fixture.root / "failure.png"))
            print("BROWSER_FIXTURE", fixture.root)
            raise
        finally:
            browser.close()
finally:
    fixture.save_evidence()
    fixture.stop()
