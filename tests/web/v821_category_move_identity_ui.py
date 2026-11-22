"""Drag a concept between categories while its editor and declared links are open."""

import hashlib
import json
import uuid

from playwright.sync_api import expect, sync_playwright

import v666_workspace_finder_fixture as fixture


NAMESPACE = "Example.FrameLoop"
MOVING = NAMESPACE + "::Mover"
ORIGIN = NAMESPACE + "::StartFolder"
DESTINATION = NAMESPACE + "::DestinationFolder"
LINKS = NAMESPACE + "::ExistingLinks"
AGENT = "Confectory.Agent.Responses::Connection"


def seed_projects():
    for project, health in zip(fixture.projects, (41, 84)):
        declarations = {
            "Vitals": ("schema", f"schema {NAMESPACE}::Vitals {{ field HP single general long; }}"),
            "BaseUnit": ("object", f"object {NAMESPACE}::BaseUnit {{ use schema {NAMESPACE}::Vitals; data HP = 10; }}"),
            "Mover": ("object", f'''object {MOVING} extends {NAMESPACE}::BaseUnit {{
                value editorFolder = "{ORIGIN}";
                value keep = "category move preserves metadata";
                data HP = {health};
                description "Mover with an existing declared reference";
            }}'''),
            "StartFolder": ("category", f"category {ORIGIN} {{}}"),
            "DestinationFolder": ("category", f"category {DESTINATION} {{}}"),
            "ExistingLinks": ("category", f"category {LINKS} {{ contain object {MOVING}; }}"),
        }
        manifest = project.read_text().rstrip()
        registrations = []
        for name, (kind, text) in declarations.items():
            path = project.parent / f"{name}.celem"
            path.write_text(text, encoding="utf-8")
            fixture.before[str(path)] = path.read_bytes()
            registrations.append(f'element {name} {kind} "{path.name}";')
        project.write_text(manifest[:-1] + "\n" + "\n".join(registrations) + "\n}\n", encoding="utf-8")
        fixture.before[str(project)] = project.read_bytes()
    profile = fixture.root / "profile"
    profile.mkdir(exist_ok=True)
    labels = ("Category First", "Category Second")
    (profile / "projects.json").write_text(json.dumps([
        {"path": str(project), "title": label, "description": ""}
        for project, label in zip(fixture.projects, labels)
    ]), encoding="utf-8")


def open_browser(page):
    page.locator("#title").click()
    page.locator(".context-menu").get_by_role("button", name="프로젝트 브라우저", exact=True).click()
    window = page.locator('.window[data-key="browser"]')
    expect(window).to_be_visible()
    tree = window.locator(".browser-folder-tree")
    if not tree.is_visible():
        window.locator("[data-browser-detail]").click()
    expect(tree.locator(f'[data-tree-id="{ORIGIN}"]')).to_be_visible()
    return window


def title_point(window):
    # Find an exposed area in the title bar so other windows can stay open.
    point = window.evaluate("""el => {
        const header = el.querySelector(':scope > .window-title');
        const rect = header.getBoundingClientRect();
        const y = rect.top + rect.height / 2;
        for (let x = rect.left + 6; x < rect.right - 6; x += 8) {
            const target = document.elementFromPoint(x, y);
            if (target?.closest('.window-title') === header && !target.closest('button, input')) {
                return {x, y};
            }
        }
        return null;
    }""")
    assert point, "No exposed point on window title"
    return point


def focus_window(window):
    point = title_point(window)
    window.page.mouse.click(point["x"], point["y"])


def move_window_right(window):
    point = title_point(window)
    mouse = window.page.mouse
    mouse.move(point["x"], point["y"])
    mouse.down()
    mouse.move(point["x"] + 650, point["y"], steps=8)
    mouse.up()


def tree_id(window, identifier):
    return window.locator(f'.browser-folder-tree [data-tree-id="{identifier}"]')


def object_card(window):
    return window.locator(f'[data-object="{MOVING}"]')


def source_draft():
    draft = fixture.state()["draft"]
    assert draft["id"] == MOVING
    return draft["text"]


def flat_declaration(text):
    # This fixture has flat, semicolon-terminated fields. The engine formats their order.
    header, body = text.strip().removesuffix("}").split("{", 1)
    return header.strip(), sorted(field.strip() for field in body.split(";") if field.strip())


def assert_editor(page, old_window, health):
    editor = page.locator('.window[data-key="schema"]')
    expect(editor).to_be_visible()
    assert old_window.evaluate("node => node.isConnected && !node.hidden")
    expect(editor.locator(".object-title-name")).to_have_text("Mover")
    expect(editor.get_by_label("HP 기본값", exact=True)).to_have_value(str(health))
    return editor


def attach_local_worker(page):
    # Follow the local-only setup in v666_worker_badges_ui.py. Nothing is dispatched.
    page.locator("#add-agent").click()
    dialog = page.get_by_role("dialog", name="Agent 추가", exact=True)
    dialog.get_by_role("button", name="OpenAI Responses", exact=True).click()
    for field, value in (("model", "category-move-no-inference"), ("endpoint", "http://127.0.0.1:9"),
                         ("credentialReference", "")):
        dialog.locator(f'[data-connection-field="{field}"]').fill(value)
    dialog.locator("[data-agent-register]").click()
    expect(dialog.locator("[data-agent-registration-state]")).to_contain_text("Agent 등록됨")
    dialog.locator("[data-connection-cancel]").click()
    helper = fixture.call("helperGlobal", {
        "action": "create", "creationId": uuid.uuid4().hex, "name": "Category fixture Helper",
        "personality": "fixture", "speciality": "fixture", "agent": AGENT,
    })["helper"]
    page.locator("#add-helper").click()
    placement = page.get_by_role("dialog", name="프로젝트 도우미 배치", exact=True)
    placement.locator(f'[data-project-helper="{helper}"]').click()
    placement.locator('button[type="submit"]').click()
    expect(placement).to_have_count(0)
    assert fixture.state()["projectHelperIds"] == [helper]
    fixture.call("customProposal", {
        "target": MOVING, "commandID": uuid.uuid4().hex, "text": "Keep this task assigned to the same concept",
    })
    card = fixture.state()["augment"]["customCards"][-1]
    fixture.call("selectCard", {"card": card["id"]})
    journal = fixture.projects[0].parent / ".confectory" / "ai-development" / "helpers" / (
        hashlib.sha256(helper.encode()).hexdigest()[:16]
    ) / "tasks.json"
    return helper, journal, journal.read_bytes()


def enter_second_project(page):
    page.evaluate("() => globalThis.confectoryFlushPresentation()")
    page.locator(".brand").click()
    expect(page.locator(".home-grid")).to_be_visible()
    page.locator(".project-card").filter(
        has=page.get_by_role("heading", name="Category Second", exact=True)
    ).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text("Category Second")


def check_category_move(page):
    helper, task_journal, original_task = attach_local_worker(page)
    browser = open_browser(page)
    tree_id(browser, LINKS).dblclick()
    primary_declaration = page.locator('.window[data-key="declaration"]')
    expect(primary_declaration.locator("[data-declaration-id]")).to_have_text(LINKS)
    primary_declaration.locator("[data-declaration-keep]").click()
    reference_panel = page.locator('.window[data-key^="editor-"]').filter(
        has=page.locator("[data-declaration-id]").filter(has_text=LINKS)
    )
    expect(reference_panel.locator("[data-declaration-id]")).to_have_text(LINKS)
    move_window_right(reference_panel)
    reference_panel.locator("[data-declaration-references] summary").click()
    link = reference_panel.locator(f'[data-reference-target="{MOVING}"]')
    link.click()
    editor = page.locator('.window[data-key="schema"]')
    original_editor = editor.element_handle()
    assert_editor(page, original_editor, 41)
    original_draft = source_draft()
    fixture.checked("The existing typed contain reference opens the exact concept before the move")

    focus_window(browser)
    tree_id(browser, ORIGIN).click()
    expect(browser.locator(".browser-title-path")).to_contain_text("StartFolder")
    expect(object_card(browser).locator(f'[data-assigned-helper="{helper}"]')).to_be_visible()
    object_card(browser).drag_to(tree_id(browser, DESTINATION))
    expect(page.locator("#status")).to_contain_text("분류 위치를 변경했어요")
    expect(object_card(browser)).to_have_count(0)
    assert_editor(page, original_editor, 41)
    tree_id(browser, DESTINATION).click()
    expect(browser.locator(".browser-title-path")).to_contain_text("DestinationFolder")
    expect(object_card(browser)).to_be_visible()
    expect(tree_id(browser, DESTINATION)).to_have_attribute("aria-current", "location")
    expect(object_card(browser).locator(f'[data-assigned-helper="{helper}"]')).to_be_visible()
    assert list(row["assignedSourceIds"] for row in fixture.state()["assignmentWorkers"]) == [[MOVING]]
    assert task_journal.read_bytes() == original_task
    after_move = source_draft()
    expected_move = original_draft.replace(f'"{ORIGIN}"', f'"{DESTINATION}"')
    assert flat_declaration(after_move) == flat_declaration(expected_move), {
        "staged": after_move, "expected": expected_move,
    }
    fixture.original()
    fixture.checked("Dragging moves only the displayed path and folder metadata while the editor and Task stay bound to the original ID")

    focus_window(reference_panel)
    expect(reference_panel.locator("[data-declaration-id]")).to_have_text(LINKS)
    expect(link).to_be_visible()
    before_link = len(fixture.requests)
    link.click()
    expect(page.locator(".brand")).to_be_enabled()
    assert any(row["endpoint"] == "select" and row["input"]["id"] == MOVING for row in fixture.requests[before_link:])
    assert_editor(page, original_editor, 41)
    assert DESTINATION in source_draft()
    fixture.original()
    fixture.checked("The existing declaration reference still opens the same editor and unmodified field after the move")

    enter_second_project(page)
    browser = open_browser(page)
    tree_id(browser, ORIGIN).click()
    expect(object_card(browser)).to_be_visible()
    expect(object_card(browser).locator("[data-assigned-helper]")).to_have_count(0)
    object_card(browser).click()
    second_window = page.locator('.window[data-key="schema"]')
    expect(second_window.get_by_label("HP 기본값", exact=True)).to_have_value("84")
    assert ORIGIN in source_draft() and DESTINATION not in source_draft()
    assert not fixture.state()["assignmentWorkers"]
    fixture.original()
    assert task_journal.read_bytes() == original_task
    assert not fixture.errors and not fixture.external, (fixture.errors, fixture.external)
    fixture.checked("The second project retains its own category, value and assignments for the same qualified ID")


if __name__ == "__main__":
    seed_projects()
    try:
        fixture.start(0)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox"])
            page = fixture.setup(browser)
            page.set_viewport_size({"width": 1850, "height": 1180})
            try:
                check_category_move(page)
            except Exception:
                page.screenshot(path=str(fixture.root / "failure.png"))
                print("CATEGORY_MOVE_FIXTURE", fixture.root)
                raise
            finally:
                browser.close()
    finally:
        fixture.save_evidence()
        fixture.stop()
