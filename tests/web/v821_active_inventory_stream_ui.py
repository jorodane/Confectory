"""Actual active-project inventory starts its scoped reader, never a home prewarm."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import v821_warm_source_refresh_ui as w

f=w.fixture
w.seed()
local=f.root/"performance";local.mkdir()
f.env.update(CONFECTORY_PERFORMANCE="1",XDG_DATA_HOME=str(local))
f.start(0)
try:
    with sync_playwright() as p,p.chromium.launch(executable_path="/usr/bin/chromium",args=["--no-sandbox"]) as browser:
        expect.set_options(timeout=90000)
        page=f.setup(browser)
        for title,label in ((w.SECOND,"대조 표식"),(w.FIRST,w.SAME)):
            w.enter(page,title)
            window=w.browser_window(page)
            w.search(window,label,"LookupObject")
            expect(page.locator("#project-menu")).to_be_enabled()
        f.original();assert not f.errors and not f.external
finally:
    f.stop()

log=next(local.rglob("engine.jsonl"))
records=[json.loads(line) for line in log.read_text().splitlines()]
combined=[]
for row in records:
    if row.get("stage")!="consumer" or row.get("operation")!="localInventory":
        continue
    start=row["atMs"]-row["elapsedMs"]-1
    reads=[r for r in records if start<=r["atMs"]<=row["atMs"]+1
           and r.get("stage") in ("authoring-stream","authoring-process")]
    relations=[r for r in reads if r.get("operation")=="relationsMap"]
    if not relations:
        continue
    assert all(r["stage"]=="authoring-stream" for r in relations),relations
    assert any(r["operation"]=="catalog" and r["stage"]=="authoring-stream" for r in reads),reads
    combined.append(row)
assert len(combined)>=2,combined
print("PASS two actual active-project transitions use fresh scoped inventory and relationship reads",len(combined),flush=True)
print("evidence",f.root,flush=True)
