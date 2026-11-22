"""Real Linux editor: a canceled Yogi pointer selection must not save a cell."""
import ast
import json
import re
import shutil
import time
from pathlib import Path

from playwright.sync_api import expect, sync_playwright
import v666_node_names_recovery_fixture as t

f = t.f
source = Path(t.__file__).with_name("v821_function_document_ui.py")
tree = ast.parse(source.read_text(), filename=str(source))
exec(compile(ast.Module(
    body=[n for n in tree.body if isinstance(n, ast.FunctionDef)
          and n.name in {"open_document","panel","doc","pending","save"}],
    type_ignores=[]), str(source), "exec"), globals())

CAPTURING = re.compile(r"\byogi-capturing\b")
FIRST, SECOND = "First blueprint", "Second blueprint"
A, B = "첫 프로젝트의 계산", "둘째 프로젝트의 계산"
second = f.case / "other project"
shutil.copytree(f.project, second, ignore=shutil.ignore_patterns(".confectory"))
(f.storage / "projects.json").write_text(json.dumps([
    {"path":str(path / "project.cproj"), "title":title, "description":""}
    for path,title in [(f.project,FIRST),(second,SECOND)]
]))
original = {p:p.read_bytes() for root in (f.project,second) for p in root.rglob("*") if p.is_file()}


def switch(page, title):
    page.locator(".brand").click()
    expect(page.locator(".home-grid")).to_be_visible(timeout=30000)
    card = page.locator(".project-card").filter(has=page.get_by_role("heading",name=title,exact=True))
    card.locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(title,timeout=30000)
    f.idle()
    open_document()


def name():
    return doc().locator('[data-document-name="body"]')


def verify_pending(wanted, excluded):
    entries = pending()
    text = json.dumps(entries,ensure_ascii=False)
    assert wanted in text and excluded not in text, entries


def relevant(mark):
    watched = {"blueprint","saveDraft","confirmGroup","select","yogi","sendChat","submitProjectChat"}
    return [(req["endpoint"], req.get("input",{}).get("action"))
            for row in f.traffic[mark:] if (req:=row.get("invoke",{})).get("endpoint") in watched]


def capture_cancel(page):
    page.keyboard.press("Control+y")
    expect(page.locator("body")).to_have_class(CAPTURING)
    button = panel().locator("[data-bp-save]")
    expect(button).to_be_enabled()
    bounds = button.bounding_box()
    x,y = bounds["x"] + bounds["width"]/2,bounds["y"] + bounds["height"]/2
    assert button.evaluate("(el, [x,y]) => el.contains(document.elementFromPoint(x,y))", [x,y])
    page.mouse.move(x,y)
    page.mouse.down()
    page.keyboard.press("Escape")
    expect(page.locator("body")).not_to_have_class(CAPTURING)
    page.mouse.up()
    f.idle()


try:
    f.start(0)
    f.invoke("select",{"id":t.feature})
    f.invoke("saveDraft",{})
    checkpoint = t.checkpoint()
    base_checkpoint = checkpoint.read_bytes()
    with sync_playwright() as pw:
        f.browser = pw.chromium.launch(executable_path="/usr/bin/chromium",
            args=["--no-sandbox","--disable-gpu","--renderer-process-limit=2"],
            ignore_default_args=["--disable-dev-shm-usage"])
        try:
            f.page = page = f.setup()
            page.set_viewport_size({"width":1800,"height":1400})
            expect(page.locator("#title")).to_contain_text(FIRST)
            open_document()
            first_scope = f.state()["projectId"]
            switch(page, SECOND)
            second_scope = f.state()["projectId"]
            assert first_scope != second_scope
            name().fill(B)
            verify_pending(B, A)
            switch(page, FIRST)
            expect(name()).to_have_value("body")
            name().fill(A)
            name().press("End")
            page.keyboard.type("x")
            expect(name()).to_have_value(A+"x")
            assert name().evaluate("""el => el.dispatchEvent(new KeyboardEvent('keydown',{
              key:'z',ctrlKey:true,isComposing:true,bubbles:true,cancelable:true
            }))""")
            expect(name()).to_have_value(A+"x")
            page.keyboard.press("Control+z")
            expect(name()).to_have_value(A)
            verify_pending(A, B)
            name().focus()
            mark = len(f.traffic)
            capture_cancel(page)
            changes = relevant(mark)
            print(f"Yogi cancel commands: {changes}; checkpoint changed {checkpoint.read_bytes()!=base_checkpoint}",
                  flush=True)
            assert changes == [("yogi","show")], changes
            assert checkpoint.read_bytes()==base_checkpoint
            expect(name()).to_be_focused()
            expect(name()).to_have_value(A)
            verify_pending(A,B)
            local_box = f.state().get("yogi")
            assert local_box is None or not local_box["items"]
            switch(page, SECOND)
            assert f.state()["projectId"]==second_scope
            expect(name()).to_have_value(B)
            verify_pending(B,A)
            switch(page, FIRST)
            assert f.state()["projectId"]==first_scope
            expect(name()).to_have_value(A)
            save()
            assert t.current()["body"]==A
            assert not pending()
            switch(page, SECOND)
            expect(name()).to_have_value(B)
            verify_pending(B,A)
            switch(page, FIRST)
            expect(name()).to_have_value(A)
            assert not pending()
            assert all(p.read_bytes()==b for p,b in original.items())
            assert not f.external and not f.errors, (f.external,f.errors)
            print("PASS cancel causes no save or capture; explicit Save and two-project reentry preserve both drafts",flush=True)
        finally:
            f.page.close()
            f.browser.close()
finally:
    f.stop()
