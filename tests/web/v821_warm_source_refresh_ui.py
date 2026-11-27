"""Actual warm reactivation of an existing owned project after external edits.

Run with REPO BUILD_REPORT 40|400. Only synthetic projects and
the existing local Chromium editor; no account, external endpoint or game DLL.
"""
import json
import sys
from playwright.sync_api import expect, sync_playwright
import v666_workspace_finder_fixture as fixture
from v821_project_browser_search_labels import NS, browser_window, search

FIRST, SECOND = "Label Search First", "Label Search Second"
SAME, CATEGORY, MODULE = "안내 표식", "작업 분류", "조작 규격"
count = int(sys.argv[3]) if len(sys.argv)>3 else 40
assert count in (40,400)


def seed():
    for manifest, title in zip(fixture.projects, (FIRST, SECOND)):
        declarations = {
            "LookupObject": ("object", f'value editorName = "{SAME}";'),
            "LookupFunction": ("function", f'value editorName = "{SAME}";'),
            "LookupModule": ("module", f'value editorName = "{SAME}";'),
        }
        if title == FIRST:
            declarations.update({
                "Folder": ("category", f'value editorName = "{CATEGORY}";'),
                "LookupObject": ("object", f'value editorName = "{SAME}"; value editorFolder = "{NS}::Folder";'),
                "ContractModule": ("module", f'value editorName = "{MODULE}"; require {NS}::LookupFunction () -> int;'),
                "Unbound": ("function", ""),
            })
        else:
            declarations["LookupObject"] = ("object", 'value editorName = "대조 표식";')
            declarations["PeerOnly"] = ("object", f'value editorName = "{SAME}";')
        declarations.update({f"Extra{i:04}":("object",f'value editorName = "Extra {i:04}";') for i in range(count-2)})
        declarations["LookupInfo"]=("schema","field Note single general string;")
        old=declarations["LookupObject"][1]
        declarations["LookupObject"]=("object",f'use schema {NS}::LookupInfo; data Note = "Baseline Note"; '+old)
        declarations["Links"]=("schema",f"field Target single reference {NS}::LookupInfo;")
        declarations["LinkedObject"]=("object",f"use schema {NS}::Links; data Target = {NS}::LookupObject;")
        entries = []
        for name, (kind, details) in declarations.items():
            file = manifest.parent / f"private-source-{name}.celem"
            signature = " () -> int" if kind == "function" else ""
            file.write_text(f"{kind} {NS}::{name}{signature} {{ {details} }}\n", encoding="utf-8")
            fixture.before[str(file)] = file.read_bytes()
            entries.append(f'element {name} {kind} "{file.name}";')
        manifest.write_text(manifest.read_text().rstrip()[:-1] + "\n" + "\n".join(entries) + "\n}\n")
        fixture.before[str(manifest)] = manifest.read_bytes()
    profile = fixture.root / "profile"
    profile.mkdir(exist_ok=True)
    (profile / "projects.json").write_text(json.dumps([
        {"path": str(path), "title": title, "description": ""}
        for path, title in zip(fixture.projects, (FIRST, SECOND))
    ]))


def enter(page,title):
    page.get_by_role("button",name="Confectory 홈으로").click()
    expect(page.locator(".home-grid")).to_be_visible()
    page.locator(".project-card").filter(has=page.get_by_role("heading",name=title,exact=True)).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(title)

def property_editor(window, label):
    row=window.locator(f'[data-object="{NS}::LookupObject"]')
    row.click(button="right")
    window.page.locator(".context-menu").get_by_role("button",name="스키마 열기",exact=True).click()
    editor=window.page.locator('.window[data-key="schema"]')
    expect(editor.locator(".object-title-name")).to_have_text(label)
    expect(editor.locator(".object-info-button")).to_have_attribute("title",f"소유 · ProjectPack\nID · {NS}::LookupObject")
    expect(editor.get_by_label("Note 기본값",exact=True)).to_be_editable()
    return editor

def scenario(page):
    window=browser_window(page)
    search(window,SAME,"LookupObject")
    editor=property_editor(window,SAME)
    expect(editor.get_by_label("Note 기본값",exact=True)).to_have_value("Baseline Note")
    editor.get_by_role("button",name="창 닫기",exact=True).click()
    window=browser_window(page)
    search(window,"LinkedObject","LinkedObject")
    window.locator(f'[data-object="{NS}::LinkedObject"]').click(button="right")
    page.locator(".context-menu").get_by_role("button",name="스키마 열기",exact=True).click()
    linked=page.locator('.window[data-key="schema"]')
    ref=linked.get_by_role("button",name="Target 기본값 선택",exact=True)
    expect(ref).to_have_text(SAME)
    # The large reference-choice query is already rejected on a5041023
    # before any external edit; verify its exact-ID selector at 40 and
    # the actual reference value/hover at both sizes.
    if count==40:
        ref.click()
        picker=page.get_by_role("dialog",name="기본값 선택",exact=True)
        choice=picker.locator(f'[data-reference-choice="{NS}::LookupObject"]')
        expect(choice).to_be_visible()
        original_choice=choice.inner_text()
        choice.click()
    linked.get_by_role("button",name="창 닫기",exact=True).click()
    enter(page,SECOND)
    window=browser_window(page)
    search(window,"대조 표식","LookupObject")
    source=fixture.projects[0].parent/"private-source-LookupObject.celem"
    source.write_text(source.read_text().replace(SAME,"외부 수정 표식"))
    fixture.before[str(source)]=source.read_bytes()
    # A second owner outside the selected cursor and (at 400) current page
    # must also invalidate the previous projection.
    extra=f"Extra{count-3:04}"
    extra_path=fixture.projects[0].parent/f"private-source-{extra}.celem"
    extra_path.write_text(extra_path.read_text().replace(f"Extra {count-3:04}","Unselected external label"))
    fixture.before[str(extra_path)]=extra_path.read_bytes()
    enter(page,FIRST)
    window=browser_window(page)
    search(window,"Unselected external label",extra)
    expect(window.locator(f'[data-tree-id="{NS}::LookupObject"]')).to_contain_text("외부 수정 표식")
    search(window,SAME)
    search(window,"외부 수정 표식","LookupObject")
    editor=property_editor(window,"외부 수정 표식")
    expect(editor.get_by_label("Note 기본값",exact=True)).to_have_value("Baseline Note")
    editor.get_by_role("button",name="창 닫기",exact=True).click()
    window=browser_window(page)
    search(window,"LinkedObject","LinkedObject")
    window.locator(f'[data-object="{NS}::LinkedObject"]').hover()
    tip=page.get_by_role("tooltip")
    expect(tip).to_contain_text("외부 수정 표식")
    expect(tip).not_to_contain_text(SAME)
    window.locator(f'[data-object="{NS}::LinkedObject"]').click(button="right")
    page.locator(".context-menu").get_by_role("button",name="스키마 열기",exact=True).click()
    linked=page.locator('.window[data-key="schema"]')
    expect(linked.locator(".object-title-name")).to_have_text("LinkedObject")
    ref=linked.get_by_role("button",name="Target 기본값 선택",exact=True)
    expect(ref).to_have_text("외부 수정 표식")
    if count==40:
        ref.click()
        picker=page.get_by_role("dialog",name="기본값 선택",exact=True)
        choice=picker.locator(f'[data-reference-choice="{NS}::LookupObject"]')
        # Existing reference candidates use their qualified contract's short ID;
        # the selected value and hover use the current Browser display label.
        assert choice.inner_text()==original_choice, (original_choice,choice.inner_text())
        choice.click()
    linked.get_by_role("button",name="창 닫기",exact=True).click()
    print("PASS warm rename updates Browser search, exact property title, reference hover and value",flush=True)

    search(window,"외부 수정 표식","LookupObject")
    editor=property_editor(window,"외부 수정 표식")
    field=editor.get_by_label("Note 기본값",exact=True)
    field.fill("Unsaved local value")
    enter(page,SECOND)
    window=browser_window(page)
    search(window,"대조 표식","LookupObject")
    expect(window.locator(f'[data-tree-id="{NS}::LookupObject"]')).to_contain_text("대조 표식")
    source.write_text(source.read_text().replace("외부 수정 표식","다른 외부 이름"))
    fixture.before[str(source)]=source.read_bytes()
    enter(page,FIRST)
    window=browser_window(page)
    expect(window.locator(f'[data-tree-id="{NS}::LookupObject"]')).to_contain_text("다른 외부 이름")
    search(window,"다른 외부 이름","LookupObject")
    editor=property_editor(window,"다른 외부 이름")
    field=editor.get_by_label("Note 기본값",exact=True)
    expect(field).to_have_value("Unsaved local value")
    save=editor.locator('[data-element-action="confirm"]')
    expect(save).to_be_enabled()
    save.click()
    expect(page.locator("#project-menu")).to_be_enabled()
    expect(field).to_have_value("Unsaved local value")
    assert source.read_bytes()==fixture.before[str(source)]
    expect(editor.locator("[data-element-error]")).not_to_have_text("")
    print("PASS stale dirty input is retained and cannot overwrite externally changed source",flush=True)
    enter(page,SECOND)
    # Retained owner manifest change must fail closed without replacing the draft.
    manifest=fixture.projects[0]
    before=manifest.read_bytes()
    manifest.write_bytes(before+b"\n// external manifest edit\n")
    page.get_by_role("button",name="Confectory 홈으로").click()
    expect(page.locator(".home-grid")).to_be_visible()
    card=page.locator(".project-card").filter(has=page.get_by_role("heading",name=FIRST,exact=True)).locator("[data-enter]")
    card.click()
    expect(page.locator("#status")).to_contain_text("프로젝트 등록 원본이 변경됐습니다")
    expect(page.locator(".home-grid")).to_be_visible()
    assert manifest.read_bytes()==before+b"\n// external manifest edit\n"
    manifest.write_bytes(before)
    mode=source.stat().st_mode
    source.chmod(0)
    try:
        card.click()
        expect(page.locator("#status")).to_contain_text("원본을 읽을 권한이 없습니다")
        expect(page.locator(".home-grid")).to_be_visible()
    finally:source.chmod(mode)
    missing=source.with_suffix(".missing")
    source.rename(missing)
    try:
        card.click()
        expect(page.locator("#status")).to_contain_text("원본 파일이 없습니다")
        expect(page.locator(".home-grid")).to_be_visible()
    finally:missing.rename(source)
    correct=source.read_bytes()
    source.write_text(source.read_text().replace("::LookupObject {","::DifferentID {"))
    try:
        card.click()
        expect(page.locator("#status")).to_contain_text("선언 ID 또는 종류가 변경됐습니다")
        expect(page.locator(".home-grid")).to_be_visible()
    finally:source.write_bytes(correct)
    card.click()
    expect(page.locator("#title")).to_contain_text(FIRST)
    window=browser_window(page)
    search(window,"다른 외부 이름","LookupObject")
    editor=property_editor(window,"다른 외부 이름")
    expect(editor.get_by_label("Note 기본값",exact=True)).to_have_value("Unsaved local value")
    fixture.original()
    print("PASS manifest, unreadable, missing and wrong-ID sources fail closed, then retained input restores",flush=True)
    page.evaluate("()=>confectoryFlushPresentation()")
    browser=page.context.browser
    page.close()
    fixture.stop()
    fixture.env.pop("CONFECTORY_WEB_PROJECT",None)
    fixture.start(1)
    from editor_navigation import goto_editor
    page=browser.new_page(viewport={"width":1440,"height":1000})
    page.route("**/*",lambda route:route.continue_() if route.request.url.startswith(fixture.origin+"/") else route.abort())
    goto_editor(page,fixture.url)
    page.locator(".project-card").filter(has=page.get_by_role("heading",name=FIRST,exact=True)).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(FIRST)
    window=browser_window(page)
    search(window,"다른 외부 이름","LookupObject")
    editor=property_editor(window,"다른 외부 이름")
    expect(editor.get_by_label("Note 기본값",exact=True)).to_have_value("Unsaved local value")
    fixture.original()
    print("PASS process restart preserves external name and unsaved input",flush=True)


if __name__ == "__main__":
    seed()
    fixture.start(0)
    try:
        with sync_playwright() as playwright, playwright.chromium.launch(
                executable_path="/usr/bin/chromium", args=["--no-sandbox"]) as browser:
            expect.set_options(timeout=60000)
            page = fixture.setup(browser)
            scenario(page)
            assert not fixture.errors and not fixture.external
    finally:
        fixture.stop()
        print("evidence",fixture.root,flush=True)
