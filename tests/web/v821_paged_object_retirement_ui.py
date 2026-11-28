"""Real browser ordinary object deletion across the original declaration boundary.

Usage: REPO BUILD_REPORT 255|256|257|400 [--conflict] [--always] [--permission] [--trace-files] [--object-count].
The count includes the owned manifest unless --object-count is given; all projects are disposable copies.
"""
import sys
from playwright.sync_api import expect, sync_playwright
import v666_workspace_finder_fixture as f
from v821_project_browser_search_labels import NS, browser_window

count=int(sys.argv[3]); assert count in (255,256,257,400)
flags=set(sys.argv[4:]); assert flags<={"--conflict","--always","--permission","--trace-files","--object-count"}
assert "--object-count" not in flags or count==400
orphan="OrphanDataValue"; protected="ProtectedDataValue"
for manifest in f.projects:
    text=manifest.read_text()
    sources={
      "DataInfo":("schema",f"schema {NS}::DataInfo {{ field Count single general long; }}"),
      orphan:("object",f"object {NS}::{orphan} {{ use schema {NS}::DataInfo; data Count = 4; }}"),
      protected:("object",f"object {NS}::{protected} {{ use schema {NS}::DataInfo; data Count = 7; }}"),
      "LinkInfo":("schema",f"schema {NS}::LinkInfo {{ field Target single reference {NS}::DataInfo; }}"),
      "Referrer":("object",f"object {NS}::Referrer {{ use schema {NS}::LinkInfo; data Target = {NS}::{protected}; }}"),
    }
    existing=text.count("element ")+1
    extra_count=count-existing-len(sources)
    if "--object-count" in flags:
        import re
        extra_count=count-len(re.findall(r"\belement\s+\S+\s+object\s+",text))-sum(kind=="object" for kind,_ in sources.values())
    for i in range(extra_count):
        name=f"Extra{i:04}"
        sources[name]=("object",f"object {NS}::{name} {{}}")
    entries=[]
    for name,(kind,body) in sources.items():
        path=manifest.parent/f"{name}.celem"
        path.write_text(body+"\n")
        f.before[str(path)]=path.read_bytes()
        entries.append(f'element {name} {kind} "{path.name}";')
    manifest.write_text(text.rstrip()[:-1]+"\n"+"\n".join(entries)+(f"\nalways {NS}::{orphan};" if "--always" in flags else "")+"\n}\n")
    if "--object-count" in flags:assert len(re.findall(r"\belement\s+\S+\s+object\s+",manifest.read_text()))==count
    else:assert manifest.read_text().count("element ")+1==count
    f.before[str(manifest)]=manifest.read_bytes()
manifest=f.projects[0];before=manifest.read_bytes()
source=manifest.parent/f"{orphan}.celem";retained=source.read_bytes()
traces=[];run=list(f.report["run"])
def start(index):
    if "--trace-files" in flags:
        trace=f.root/f"files-{index}.log";traces.append(trace)
        f.report["run"]=["strace","-f","-s","256","-e","trace=execve,openat","-o",str(trace),*run]
    f.start(index)
expect.set_options(timeout=120000)

def filter_row(b,name):
    b.get_by_role("textbox",name="의미 객체 검색",exact=True).fill(name)
    b.get_by_role("button",name="검색 확정",exact=True).click()
    expect(b.get_by_role("button",name="검색 확정",exact=True)).to_be_enabled()
    return b.locator(f'[data-object="{NS}::{name}"]')

def delete(page,b,name):
    row=filter_row(b,name);expect(row).to_be_visible();row.click(button="right")
    page.get_by_role("button",name="삭제",exact=True).click()
    dialog=page.get_by_role("dialog",name="의미 객체 삭제",exact=True)
    expect(dialog).to_be_visible();return dialog

def review(page,b):
    b.locator("[data-browser-confirm]").click()
    r=page.locator('.window[data-key="review"]');expect(r).to_be_visible()
    if r.locator("[data-review-advanced]").is_visible():r.locator("[data-review-advanced]").click()
    if r.locator("[data-advanced-reviewed]").count():r.locator("[data-advanced-reviewed]").check()
    expect(r.locator("#confirm")).to_be_enabled();return r

try:
    start(0)
    with sync_playwright() as p,p.chromium.launch(executable_path="/usr/bin/chromium",args=["--no-sandbox"]) as browser:
        page=f.setup(browser);page.set_viewport_size({"width":1800,"height":1200});b=browser_window(page)
        d=delete(page,b,protected)
        expect(d).to_contain_text("참조하는 항목")
        expect(d.locator("#delete-object")).to_have_count(0)
        d.get_by_role("button",name="닫기",exact=True).click();f.original()
        d=delete(page,b,orphan);expect(d.locator("#delete-object")).to_be_visible()
        d.get_by_role("button",name="닫기",exact=True).click();f.original()
        d=delete(page,b,orphan);d.locator("#delete-object").click();expect(d).to_be_hidden()
        expect(filter_row(b,orphan)).to_have_count(0);f.original()
        r=review(page,b);r.locator("[data-reject]").click();expect(r).to_be_hidden();f.original()
        r=review(page,b)
        if "--conflict" in flags:
            external=manifest.parent/"Extra0000.celem"
            changed=f"object {NS}::Extra0000 extends {NS}::{orphan} {{}}\n".encode()
            external.write_bytes(changed);f.before[str(external)]=changed
        mode=manifest.stat().st_mode&0o777
        if "--permission" in flags:manifest.chmod(0o400)
        try:
            r.locator("#confirm").click()
            if flags.intersection({"--conflict","--always","--permission"}):
                expect(page.locator("#status")).to_contain_text("최종 소스에 반영되지 않았습니다")
                f.original()
                if "--permission" in flags:assert manifest.stat().st_mode&0o222==0
                print("PASS",count,"late reference/always/permission refused; original registration retained",flush=True)
                refused=True
            else:refused=False
        finally:
            if "--permission" in flags:manifest.chmod(mode)
        if not refused:
            expect(r).to_be_hidden();assert f'element {orphan} object' not in manifest.read_text();assert source.read_bytes()==retained
            f.before[str(manifest)]=manifest.read_bytes();f.original()
            page.close();f.stop();start(1)
            page=f.setup(browser);page.set_viewport_size({"width":1800,"height":1200});b=browser_window(page)
            expect(filter_row(b,orphan)).to_have_count(0)
            b.locator('[data-browser-control="browser-actions"]').click()
            page.get_by_role("button",name="삭제 항목 복구",exact=True).click()
            page.locator(".context-menu").get_by_role("button",name=orphan,exact=True).click()
            expect(filter_row(b,orphan)).to_have_count(1);assert source.read_bytes()==retained
            assert f'element {orphan} object' not in manifest.read_text()
            r=review(page,b);r.locator("#confirm").click();expect(r).to_be_hidden()
            assert f'element {orphan} object' in manifest.read_text();assert source.read_bytes()==retained
            f.before[str(manifest)]=manifest.read_bytes();f.original()
            print("PASS",count,"reverse reference, cancel, delete confirm, restart/recover, same-ID peer unchanged",flush=True)
        assert not f.errors and not f.external,(f.errors,f.external)
finally:
    f.stop()
    print("evidence",f.root,flush=True)
    if traces:
        lines=[line for trace in traces for line in trace.read_text(errors="replace").splitlines()]
        compiler=sum("execve(" in line and ("csc.dll" in line or '"-noconfig"' in line) for line in lines)
        project_dll=sum("openat(" in line and any(str(project.parent) in line for project in f.projects) and '.dll"' in line for line in lines)
        assert (compiler,project_dll)==(0,0),(compiler,project_dll)
        print("PASS ordinary deletion/recovery compiler 0, project DLL opens 0",flush=True)
