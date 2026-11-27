"""Actual large-project context action retains another independent window's input."""
import json, re, shutil
from playwright.sync_api import sync_playwright, expect
import v821_property_window_reopen_ui as r

f,d=r.fixture,r.fallback
r.seed()
library=f.root/"schema-editing"
shutil.copytree(f.repo/"packs/schema-editing",library)
late_paths=[]
for manifest in f.projects:
    action=manifest.parent/"ZZLateMenu.celem"
    action.write_text((f.repo/"examples/editor-context-actions/MetadataProposal.celem").read_text().replace("Example.EditorContextActions::MetadataProposal",d.NS+"::ZZLateMenu"))
    text=manifest.read_text().rstrip()[:-1]+f' registry Confectory.SchemaEditing {json.dumps(str(library/"pack.cpack"))}; dependency Confectory.SchemaEditing version "0.1.0"; element ZZLateMenu object "ZZLateMenu.celem";'
    existing=len(re.findall(r'\belement\s+\S+\s+object\s+',text))
    for i in range(400-existing):
        name=f"AAAA{i:04}";path=manifest.parent/(name+".celem")
        path.write_text(f"object {d.NS}::{name} {{}}\n")
        f.before[str(path)]=path.read_bytes();text+=f'\nelement {name} object "{path.name}";'
    late_paths.append(manifest.parent/f"AAAA{400-existing-1:04}.celem")
    manifest.write_text(text+"\n}\n")
    for file in (manifest,action):f.before[str(file)]=file.read_bytes()
expect.set_options(timeout=90000)
f.start(0)
try:
    with sync_playwright() as p,p.chromium.launch(executable_path="/usr/bin/chromium",args=["--no-sandbox"]) as b:
        page=f.setup(b);page.set_viewport_size({"width":2200,"height":1200})
        other,key=r.floating.open_properties(page,d.PEER,"PeerFolder")
        note=r.floating.property_value(other,"Note")
        note.fill("Independent unsaved input")
        title=other.locator(".window-title");box=title.bounding_box()
        page.mouse.move(box["x"]+min(180,box["width"]/2),box["y"]+box["height"]/2)
        page.mouse.down();page.mouse.move(1700,260,steps=12);page.mouse.up()
        browser=r.browser_window(page);r.choose_tree_location(browser,f'[data-tree-id="{d.NS}::StockFolder"]')
        r.search(browser,d.LABEL,d.TARGET)
        item=browser.locator(f'[data-object="{d.NS}::{d.TARGET}"]')
        item.click(button="right")
        page.locator(".context-menu").get_by_role("button",name="등록 기능 · 메타데이터 변경안",exact=True).click()
        dialog=page.get_by_role("dialog",name="메타데이터 변경안")
        dialog.locator("[data-action-field]").fill("editorName")
        dialog.locator("[data-action-value]").fill('"Explicit proposal"')
        dialog.locator("[data-action-invoke]").click()
        expect(dialog).to_have_attribute("data-action-status","completed")
        expect(dialog.locator("[data-action-result]")).to_contain_text("Explicit proposal")
        dialog.locator("[data-close]").click()
        expect(note).to_have_value("Independent unsaved input")
        print("PASS 400-object late registered menu, explicit proposal and independent dirty input",flush=True)
        # A fresh registration after the first page must become visible on an
        # ordinary project reentry, without leaking into the same-ID peer.
        page.evaluate("()=>confectoryFlushPresentation()")
        d.leave_to_home(page)
        late=late_paths[0]
        template=(f.repo/"examples/editor-context-actions/MetadataProposal.celem").read_text()
        late.write_text(template.replace("Example.EditorContextActions::MetadataProposal",d.NS+"::"+late.stem).replace("메타데이터 변경안","Late new menu"))
        f.before[str(late)]=late.read_bytes()
        page.locator(".project-card").filter(has=page.get_by_role("heading",name=d.FIRST,exact=True)).locator("[data-enter]").click()
        expect(page.locator("#title")).to_contain_text(d.FIRST)
        browser=r.browser_window(page);r.choose_tree_location(browser,f'[data-tree-id="{d.NS}::StockFolder"]')
        r.search(browser,d.LABEL,d.TARGET)
        browser.locator(f'[data-object="{d.NS}::{d.TARGET}"]').click(button="right")
        expect(page.locator(".context-menu").get_by_role("button",name="등록 기능 · Late new menu",exact=True)).to_be_visible()
        page.keyboard.press("Escape")
        # Errors in a late declaration must remain visible, never produce a
        # partial menu or a stale usable token from the preceding query.
        saved=late.read_bytes();mode=late.stat().st_mode
        for failure in ("missing","permission"):
            if failure=="missing":late.unlink()
            else:late.chmod(0)
            try:
                browser.locator(f'[data-object="{d.NS}::{d.TARGET}"]').click(button="right")
                error=page.locator(".context-menu").get_by_role("button",name="등록 기능 조회 실패 · 다시 여세요",exact=True)
                expect(error).to_be_visible()
                assert not page.locator(".context-menu").get_by_role("button",name="등록 기능 · Late new menu",exact=True).count()
                error.click()
                expect(page.locator("#status")).to_contain_text("AUTHORING")
                page.keyboard.press("Escape")
            finally:
                if failure=="permission":late.chmod(mode)
                late.write_bytes(saved)
        restored=page.locator(f'.window[data-element-owner="{d.NS}::{d.PEER}"]:visible')
        expect(r.floating.property_value(restored,"Note")).to_have_value("Independent unsaved input")
        assert late_paths[1].read_bytes()==f.before[str(late_paths[1])]
        f.original();assert not f.external and not f.errors
        print("PASS late new registration after reentry and retained independent input; peer source unchanged",flush=True)
finally:
    f.stop();print("evidence",f.root,flush=True)
