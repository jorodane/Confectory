"""No-publication optional model preparation does not invalidate live transport reads.

Run with REPO BUILD_REPORT 40|400. Synthetic local editor only.
40 must publish the ordinary model; 400 cannot fit the existing complete proof.
--baseline records the previous 400-object revision advance and menu diagnostic.
"""
import sys
import uuid
import time
from playwright.sync_api import sync_playwright, expect
import v821_warm_source_refresh_ui as w

f = w.fixture
count = int(sys.argv[3])
baseline = "--baseline" in sys.argv[4:]
assert count in (40,400)
w.seed()
owner = f"{w.NS}::LookupObject"

def revision():
    mounted = f.mount()
    try:
        return mounted["revision"], mounted["state"]
    finally:
        f.raw({"op":"dispose","view":mounted["view"]})

def exact_read(expected, success):
    mounted = f.mount()
    rid = uuid.uuid4().hex
    try:
        input = {"operation":"list","projectId":mounted["state"]["projectId"],"id":owner,"target":"linux"}
        admitted=f.raw({"op":"invoke","view":mounted["view"],"scope":mounted["scope"],
                        "expectedRevision":expected,"requestId":rid,"endpoint":"contextActions","input":input})
        assert admitted["ok"],admitted
        for _ in range(3000):
            result=f.raw({"op":"update","view":mounted["view"],"scope":mounted["scope"]})
            rows=[row for row in result.get("results",[]) if row["requestId"]==rid]
            if rows:break
            time.sleep(.01)
        assert rows
        if success:
            assert rows[0]["ok"],rows[0]
            # The existing registered-command scan rejects this large fixture;
            # transport must not erase that explicit consumer diagnostic.
            outcome=rows[0]["result"]
            if outcome.get("status")=="failed":
                assert count==400 and "Menu object scan bound" in outcome.get("message",""),outcome
                print("PASS existing registered-menu scan bound remains explicit",flush=True)
        else:
            assert rows[0]["error"]["code"]=="stale_revision",rows[0]
    finally:
        f.raw({"op":"dispose","view":mounted["view"]})

f.start(0)
try:
    with sync_playwright() as p,p.chromium.launch(executable_path="/usr/bin/chromium",args=["--no-sandbox"]) as browser:
        expect.set_options(timeout=90000)
        page=f.setup(browser)
        window=w.browser_window(page)
        w.search(window,w.SAME,"LookupObject")
        # Use a second mounted real client after closing the browser view so
        # unrelated presentation and polling cannot change admission revision.
        page.evaluate("()=>confectoryFlushPresentation()")
        page.close()
        f.call("browserDrafts",{"action":"status","ids":[owner]})
        before,state_before=revision()
        f.call("preparePropertyModels",{"ids":[owner]})
        after,state_after=revision()
        assert state_after["projectId"]==state_before["projectId"]
        prepared={row["id"] for row in state_after["preparedPropertyModels"]}
        if count==400:
            assert owner not in prepared
            if baseline:
                assert after>before,(before,after)
                exact_read(after,True)
            else:
                assert after==before,(before,after)
                exact_read(before,True)
                f.call("objects",{"kind":"object","query":"Extra0000"})
                changed,_=revision()
                assert changed>before,(before,changed)
                exact_read(before,False)
        else:
            assert owner in prepared
            assert after>before,(before,after)
            exact_read(before,False)
        f.original()
        print("PASS actual browser search + exact admission after optional preparation",count,before,after,flush=True)
finally:
    f.stop()
    print("evidence",f.root,flush=True)
