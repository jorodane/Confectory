"""Alternating scalar/reference direct-save timing on disposable 40/400-object packs.

Usage: REPO BUILD_REPORT 40|400 [--detached] [--reverse] [--diagnostic] [--timeline] [--expect-single-detached-status] [--stale-detached-status].
Run one fixture at a time, without compiler/build/regression jobs. The default
runs three scalar and three reference saves; --diagnostic captures operation
names and process count separately, so its timing is not comparable. The
--timeline flag captures one instrumented scalar/reference pair without strace;
run separate isolated alternating processes for comparison.
"""
import json
import sys
import time
import statistics
import threading
from pathlib import Path
from playwright.sync_api import expect, sync_playwright
import v666_workspace_finder_fixture as f
from v821_project_browser_search_labels import NS, browser_window

count = int(sys.argv[3])
flags = set(sys.argv[4:])
assert count in (40, 249, 250, 400)
assert flags <= {"--detached","--trace-files","--reverse","--diagnostic","--timeline","--expect-single-detached-status","--stale-detached-status"}
assert "--malformed" not in flags or "--pick" in flags
assert not flags.intersection({"--expect-single-detached-status","--stale-detached-status"}) or {"--timeline","--detached"} <= flags
FIRST, SECOND = "Reference First", "Reference Second"
TARGETS = {"TargetZero": "Zero label", "TargetNonzero": "Nonzero label", "TargetAbsent": "Absent label"}
prefix = NS + "::"
for manifest, peer in zip(f.projects, (False, True)):
    label = lambda name: ("Peer " if peer else "") + TARGETS[name]
    declarations = {
        "TargetInfo": ("schema", "field Count single general long;"),
        "LinkInfo": ("schema", f"field Target single reference {prefix}TargetInfo; field Note single general string;"),
        "TargetZero": ("object", f'use schema {prefix}TargetInfo; data Count = 0; value editorName = "{label("TargetZero")}";'),
        "TargetNonzero": ("object", f'use schema {prefix}TargetInfo; data Count = 7; value editorName = "{label("TargetNonzero")}";'),
        "TargetAbsent": ("object", f'use schema {prefix}TargetInfo; value editorName = "{label("TargetAbsent")}";'),
        "WrongTarget": ("object", 'value editorName = "Wrong label";'),
        "ScalarObject": ("object", f'use schema {prefix}TargetInfo; data Count = 10;'),
        "SourceLink": ("object", f'use schema {prefix}LinkInfo; data Target = {prefix}TargetZero; data Note = "Keep note";'),
    }
    for i in range(count - 6):
        declarations[f"Extra{i:04}"] = ("object", f'value editorName = "Extra {i:04}";')
    entries = []
    for name, (kind, body) in declarations.items():
        path = manifest.parent / f"{name}.celem"
        text = f"{kind} {prefix}{name} {{ {body} }}\n"
        if "--malformed" in flags and name == "Extra0000" and not peer:
            text = f"object {prefix}{name} {{ !"
        path.write_text(text)
        f.before[str(path)] = path.read_bytes()
        entries.append(f'element {name} {kind} "{path.name}";')
    manifest.write_text(manifest.read_text().rstrip()[:-1] + "\n" + "\n".join(entries) + "\n}\n")
    f.before[str(manifest)] = manifest.read_bytes()
profile = f.root / "profile"
profile.mkdir(exist_ok=True)
(profile / "projects.json").write_text(json.dumps([{"path": str(p), "title": t, "description": ""} for p, t in zip(f.projects, (FIRST, SECOND))]))
source = f.projects[0].parent / "SourceLink.celem"
trace = f.root / "files.log"
if "--trace-files" in flags:
    f.report["run"] = ["strace", "-f", "-s", "256", "-e", "trace=execve,openat", "-o", str(trace), *f.report["run"]]
expect.set_options(timeout=120000)

def idle(page):
    expect(page.locator("#project-menu")).to_be_enabled()

def enter(page, title):
    page.get_by_role("button", name="Confectory 홈으로").click()
    expect(page.locator(".home-grid")).to_be_visible()
    page.locator(".project-card").filter(has=page.get_by_role("heading", name=title, exact=True)).locator("[data-enter]").click()
    expect(page.locator("#title")).to_contain_text(title)

def owner(page,name="SourceLink"):
    idle(page)
    if "--detached" in flags:
        restored = page.locator(f'.window[data-element-owner="{prefix}{name}"][data-element-mode="properties"]:visible')
        if restored.count():
            expect(restored).to_have_count(1)
            expect(restored.locator(".object-title-name")).to_have_text(name)
            return restored
    w = browser_window(page)
    if "--detached" in flags:
        # A restored independent window may overlap the Browser. Raise the
        # Browser by the user's ordinary title gesture before searching.
        heading = page.locator('.window[data-key="browser"] .window-title')
        if heading.is_visible():
            heading.click(position={"x":20,"y":10})
    w.get_by_role("textbox", name="의미 객체 검색", exact=True).fill(name)
    w.get_by_role("button", name="검색 확정", exact=True).click()
    row = w.locator(f'[data-object="{prefix}{name}"]')
    expect(row).to_be_visible()
    idle(page)
    row.click(button="right")
    page.locator(".context-menu").get_by_role("button", name="새 창으로 열기" if "--detached" in flags else "스키마 열기", exact=True).click()
    editor = page.locator(f'.window[data-element-owner="{prefix}{name}"][data-element-mode="properties"]:visible' if "--detached" in flags else '.window[data-key="schema"]')
    expect(editor.locator(".object-title-name")).to_have_text(name)
    return editor


local=f.root/"local-appdata";local.mkdir()
f.env.update(XDG_DATA_HOME=str(local),CONFECTORY_PERFORMANCE="1")
if "--timeline" in flags:f.env["CONFECTORY_UI_TRACE"]="1"
if "--diagnostic" in flags:
    f.env["CONFECTORY_UI_TRACE"]="1"
    f.report["run"]=["strace","-f","-ttt","-s","256","-e","trace=execve","-o",str(trace),*f.report["run"]]
logs=local/"Confectory"/"Performance"
def rows():
    files=list(logs.rglob("*.jsonl"))
    if not files:return []
    result=[]
    for line in max(files,key=lambda p:p.stat().st_mtime_ns).read_text().splitlines():
        try:result.append(json.loads(line))
        except ValueError:pass
    return result
def sample(page,editor,kind,i):
    name="SourceLink" if kind=="reference" else "ScalarObject"
    file=f.projects[0].parent/(name+".celem")
    if kind=="reference":
        old="TargetZero" if i%2==0 else "TargetNonzero"
        new="TargetNonzero" if i%2==0 else "TargetZero"
        ref=editor.get_by_role("button",name="Target 기본값 선택",exact=True)
        expect(ref).to_have_text(TARGETS[old])
        pick_start=time.monotonic()
        ref.click()
        dialog=page.get_by_role("dialog",name="기본값 선택",exact=True)
        expect(dialog).to_be_visible()
        dialog.locator(f'[data-reference-choice="{prefix}{new}"]').click()
        expect(ref).to_have_text(TARGETS[new])
        pick_ms=(time.monotonic()-pick_start)*1000
        marker=f"data Target = {prefix}{new}"
    else:
        field=editor.get_by_label("Count 기본값",exact=True)
        expect(field).to_have_value(str(10+i%2))
        new=11-i%2;field.fill(str(new));marker=f"data Count = {new};";pick_ms=None
    button=editor.locator('[data-element-action="confirm"]')
    expect(button).to_have_text("저장");expect(button).to_be_enabled()
    assert marker not in file.read_text()
    # Measure wall clock file persistence independently from browser polling.
    click=[];stop=threading.Event();persist=[]
    def watch():
        while not stop.is_set():
            if marker in file.read_text():
                persist.append(time.monotonic());return
            stop.wait(.002)
    thread=threading.Thread(target=watch,daemon=True)
    page.evaluate("()=>globalThis.confectoryWebUITrace=[]")
    before=len(rows());req_before=len(f.requests)
    log_path=f.root/"host-0.log";host_offset=log_path.stat().st_size
    trace_offset=trace.stat().st_size if trace.exists() else 0
    started=time.monotonic();thread.start()
    events=[];pending={}
    def on_request(req):
        try:
            a=req.post_data_json
            if req.method!="POST" or a.get("op") not in ("invoke","update","observe"):return
            key=req._impl_obj._guid
            event={"startMs":round((time.monotonic()-started)*1000,1),"op":a["op"],"endpoint":a.get("endpoint"),"action":a.get("input",{}).get("action"),"id":a.get("requestId"),"idsCount":len(a.get("input",{}).get("ids") or []),"view":bool(a.get("input",{}).get("view")),"savedOwner":a.get("input",{}).get("id")==prefix+("SourceLink" if kind=="reference" else "ScalarObject")}
            pending[key]=event;events.append(event)
        except Exception:pass
    def on_response(resp):
        try:
            key=resp.request._impl_obj._guid;event=pending.pop(key,None)
            if event is None:return
            event["endMs"]=round((time.monotonic()-started)*1000,1)
            body=resp.json()
            if event["op"]=="update":event["completed"]=[{"id":r.get("requestId"),"code":r.get("error",{}).get("code","ok")} for r in body.get("results",[])]
            else:event["code"]=body.get("error",{}).get("code",body.get("status","ok"))
        except Exception:pass
    if "--timeline" in flags:page.on("request",on_request);page.on("response",on_response)
    stale=[]
    def stale_status(route):
        try:a=route.request.post_data_json
        except Exception:a=None
        if not stale and isinstance(a,dict) and a.get("op")=="invoke" and a.get("endpoint")=="browserDrafts" and a.get("input",{}).get("view") and a.get("input",{}).get("ids")==[prefix+name] and marker in file.read_text():
            a["expectedRevision"]-=1
            stale.append(a["requestId"])
            route.continue_(post_data=json.dumps(a))
            return
        route.fallback()
    if "--stale-detached-status" in flags:page.route("**/api/request",stale_status)
    try:
        button.click()
        expect(page.locator("#status")).to_have_text("저장했습니다.")
        idle(page)
        thread.join(2);assert persist
        elapsed=(time.monotonic()-started)*1000
        expect(page.get_by_role("dialog",name="관련 변경 검토",exact=True)).to_be_hidden()
        expect(page.locator('.window[data-key="review"]')).to_be_hidden()
    finally:
        stop.set();thread.join(1)
        if "--timeline" in flags:page.remove_listener("request",on_request);page.remove_listener("response",on_response)
        if "--stale-detached-status" in flags:page.unroute("**/api/request",stale_status)
    records=rows()[before:]
    tool_trace=[];process_starts=[]
    if "--diagnostic" in flags or "--timeline" in flags:
        with log_path.open("rb") as stream:
            stream.seek(host_offset)
            for line in stream.read().decode(errors="replace").splitlines():
                if line.startswith("CONFECTORY_UI_TRACE "):
                    try:tool_trace.append(json.loads(line.split(" ",1)[1]))
                    except ValueError:pass
        if trace.exists():
          with trace.open("rb") as stream:
            stream.seek(trace_offset)
            process_starts=[line for line in stream.read().decode(errors="replace").splitlines() if "execve(" in line and ".dll" in line]

    invocations=[(r.get("endpoint"),r.get("input",{}).get("action")) for r in f.requests[req_before:]]
    browser=page.evaluate("()=>globalThis.confectoryWebUITrace||[]")
    sample={"kind":kind,"count":count,"surface":"detached" if "--detached" in flags else "primary","pickerMs":pick_ms,"diskMs":(persist[0]-started)*1000,"uiMs":elapsed,"operations":invocations,"host":records,"browser":browser,"toolTrace":tool_trace,"processStarts":len(process_starts),"timeline":events}
    print("SAMPLE",json.dumps(sample,separators=(",",":")),flush=True)
    if "--expect-single-detached-status" in flags:
        reads=[row for row in events if row["op"]=="invoke" and row["endpoint"]=="browserDrafts" and row["action"]=="status" and row["view"] and row["savedOwner"] and row["idsCount"]==1 and row["startMs"]>=sample["diskMs"]]
        assert len(reads)==1,reads
        print("PASS one status read for the confirmed detached owner, not its queued pre-confirm revision",flush=True)
    if "--stale-detached-status" in flags:
        assert len(stale)==1,stale
        results={row["id"]:row.get("code") for row in events if row["op"]=="invoke"}
        results.update({r["id"]:r["code"] for row in events for r in row.get("completed",[])})
        assert results.get(stale[0])=="stale_revision",results
        reads=[row for row in events if row["op"]=="invoke" and row["endpoint"]=="browserDrafts" and row["action"]=="status" and row["view"] and row["savedOwner"] and row["idsCount"]==1]
        assert len(reads)==2 and results.get(reads[-1]["id"])=="ok",reads
        print("PASS stale status admission rejected and freshly retried once; confirmed source retained",flush=True)
    f.before[str(file)]=file.read_bytes()
    editor.get_by_role("button",name="창 닫기",exact=True).click()
    expect(editor).to_be_hidden()
    idle(page)
    return sample
try:
    f.start(0)
    with sync_playwright() as p,p.chromium.launch(executable_path="/usr/bin/chromium",args=["--no-sandbox"]) as browser:
        page=f.setup(browser);page.set_viewport_size({"width":2000,"height":1200})
        samples=[]
        for i in range(1 if "--diagnostic" in flags or "--timeline" in flags else 3):
            order=["scalar","reference"] if (i+("--reverse" in flags))%2==0 else ["reference","scalar"]
            for kind in order:
                editor=owner(page,"SourceLink" if kind=="reference" else "ScalarObject")
                samples.append(sample(page,editor,kind,i))
        for kind in ("scalar","reference"):
            selected=[s for s in samples if s["kind"]==kind]
            print("MEDIAN",kind,statistics.median(s["diskMs"] for s in selected),statistics.median(s["uiMs"] for s in selected),flush=True)
        f.original();assert not f.errors and not f.external
        if "--trace-files" in flags:
            lines=trace.read_text(errors="replace").splitlines()
            compiler=sum("execve(" in line and ("csc.dll" in line or '"-noconfig"' in line) for line in lines)
            project_dll=sum("openat(" in line and any(str(project.parent) in line for project in f.projects) and '.dll"' in line for line in lines)
            assert (compiler,project_dll)==(0,0),(compiler,project_dll)
            print("PASS ordinary saves compiler 0, project DLL opens 0",flush=True)
finally:
    f.stop()
    print("evidence",f.root,flush=True)
