"""Actual Linux editor: explicit, held, and composing Ctrl+Y."""
import ast
from pathlib import Path
import re

from playwright.sync_api import expect, sync_playwright
import v666_node_names_recovery_fixture as t

f = t.f
helpers = Path(t.__file__).with_name("v821_function_document_ui.py")
functions = ast.parse(helpers.read_text(), filename=str(helpers))
exec(compile(ast.Module(
    body=[n for n in functions.body if isinstance(n, ast.FunctionDef)
          and n.name in {"open_document","panel","doc","pending"}], type_ignores=[]
), str(helpers), "exec"), globals())

CAPTURING = re.compile(r"\byogi-capturing\b")
DRAFT = "편집 중인 계산 이름"


def capture_state(page, expected):
    body = expect(page.locator("body"))
    if expected:
        body.to_have_class(CAPTURING)
    else:
        body.not_to_have_class(CAPTURING)
    f.idle()


def commands(mark):
    watched = {"yogi","blueprint","saveDraft","confirmGroup","sendChat","submitProjectChat"}
    return [(req["endpoint"],req.get("input",{}).get("action")) for row in f.traffic[mark:]
            if (req:=row.get("invoke",{})).get("endpoint") in watched]


def composing(field, legacy=False):
    return field.evaluate("""(el, legacy) => {
      const event = new KeyboardEvent('keydown',{
        key:'y',code:'KeyY',ctrlKey:true,isComposing:!legacy,bubbles:true,cancelable:true
      });
      if(legacy)Object.defineProperty(event,'keyCode',{value:229});
      return el.dispatchEvent(event);
    }""", legacy)


def explicit_and_held(page):
    mark = len(f.traffic)
    page.keyboard.down("Control")
    try:
        page.keyboard.down("y")
        capture_state(page, True)
        page.keyboard.down("y")
        capture_state(page, True)
        page.keyboard.down("y")
        capture_state(page, True)
        page.keyboard.up("y")
        assert commands(mark) == [("yogi","show")], commands(mark)
        observed = page.evaluate("() => window.observedYogiKeys")
        assert observed[:3] == [
            {"repeat":False,"trusted":True,"prevented":True},
            {"repeat":True,"trusted":True,"prevented":True},
            {"repeat":True,"trusted":True,"prevented":True},
        ], observed
        print("PASS first key opens once and two trusted repeats are consumed without toggling",flush=True)
        page.keyboard.down("y")
        capture_state(page, False)
        page.keyboard.down("y")
        capture_state(page, False)
        assert commands(mark) == [("yogi","show")]*2, commands(mark)
        print("PASS a fresh keypress toggles off and holding the new press leaves it off",flush=True)
        page.keyboard.up("y")
    finally:
        page.keyboard.up("Control")


def cancel_over_save(page, checkpoint, before):
    mark = len(f.traffic)
    page.keyboard.press("Control+y")
    capture_state(page, True)
    button = panel().locator("[data-bp-save]")
    expect(button).to_be_enabled()
    bounds = button.bounding_box()
    x,y = bounds["x"]+bounds["width"]/2,bounds["y"]+bounds["height"]/2
    assert button.evaluate("(el,[x,y]) => el.contains(document.elementFromPoint(x,y))", [x,y])
    page.mouse.move(x,y)
    page.mouse.down()
    page.keyboard.press("Escape")
    capture_state(page, False)
    page.mouse.up()
    f.idle()
    assert commands(mark)==[("yogi","show")], commands(mark)
    assert checkpoint.read_bytes()==before
    print("PASS Escape during a pointer selection still suppresses the underlying Save",flush=True)


try:
    f.start(0)
    f.invoke("select",{"id":t.feature})
    f.invoke("saveDraft",{})
    checkpoint=t.checkpoint()
    before=checkpoint.read_bytes()
    with sync_playwright() as pw:
        f.browser=pw.chromium.launch(executable_path="/usr/bin/chromium",
            args=["--no-sandbox","--disable-gpu","--renderer-process-limit=2"],
            ignore_default_args=["--disable-dev-shm-usage"])
        try:
            f.page=page=f.setup()
            page.set_viewport_size({"width":1800,"height":1400})
            open_document()
            field=doc().locator('[data-document-name="body"]')
            field.fill(DRAFT)
            field.press("End")
            page.keyboard.type("x")
            expect(field).to_have_value(DRAFT+"x")
            page.keyboard.press("Control+z")
            expect(field).to_have_value(DRAFT)
            pending()
            field.focus()
            page.evaluate("""() => {
              window.observedYogiKeys=[];
              addEventListener('keydown',e=>{
                if(e.ctrlKey&&e.key==='y')window.observedYogiKeys.push({
                  repeat:e.repeat,trusted:e.isTrusted,prevented:e.defaultPrevented
                });
              });
            }""")
            explicit_and_held(page)
            expect(field).to_have_value(DRAFT)
            expect(field).to_be_focused()
            mark=len(f.traffic)
            assert composing(field) and composing(field,legacy=True)
            capture_state(page,False)
            assert commands(mark)==[]
            expect(field).to_have_value(DRAFT)
            expect(field).to_be_focused()
            print("PASS synthetic IME composing and 229 keydown leave the draft and capture unchanged",flush=True)
            cancel_over_save(page,checkpoint,before)
            assert checkpoint.read_bytes()==before
            assert DRAFT in str(pending())
            t.x.original()
            assert not f.errors and not f.external,(f.errors,f.external)
        finally:
            f.page.close()
            f.browser.close()
finally:
    f.stop()
