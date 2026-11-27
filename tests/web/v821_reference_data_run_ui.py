"""Actual reviewed reference save without build, followed by explicit Run consuming new data.
Usage: REPO BUILD_REPORT 40|400. Requires SDK and strace.
Synthetic FrameLoop copies only.
"""
import json,sys,time
from playwright.sync_api import expect,sync_playwright
import v666_workspace_finder_fixture as f
from v821_project_browser_search_labels import NS,browser_window
count=int(sys.argv[3]);assert count in (40,400)
semantics={
 "TargetInfo":("schema","field Count single general long;"),
 "LinkInfo":("schema",f"field Target single reference {NS}::TargetInfo; field Note single general string;"),
 "TargetZero":("object",f'use schema {NS}::TargetInfo; data Count = 0; value editorName = "Zero label";'),
 "TargetNonzero":("object",f'use schema {NS}::TargetInfo; data Count = 7; value editorName = "Nonzero label";'),
 "TargetAbsent":("object",f'use schema {NS}::TargetInfo; value editorName = "Absent label";'),
 "WrongTarget":("object",'value editorName = "Wrong label";'),
 "SourceLink":("object",f'use schema {NS}::LinkInfo; data Target = {NS}::TargetZero; data Note = "Keep note";'),
}
for i in range(count-5):semantics[f"Extra{i:04}"]=("object",f'value editorName = "Extra {i:04}";')
for manifest in f.projects:
 entries=[]
 for name,(kind,body) in semantics.items():
  p=manifest.parent/f"{name}.celem";p.write_text(f"{kind} {NS}::{name} {{ {body} }}\n")
  f.before[str(p)]=p.read_bytes();entries.append(f'element {name} {kind} "{p.name}";')
 manifest.write_text(manifest.read_text().rstrip()[:-1]+"\n"+"\n".join(entries)+f"\nalways {NS}::SourceLink;\n}}\n")
 main=manifest.parent/"Main.csbody"
 main.write_text('var assembly=System.Reflection.Assembly.GetEntryAssembly()!; using var linked=assembly.GetManifestResourceStream("public-linkage.json")??System.IO.File.OpenRead(System.IO.Path.Combine(System.IO.Path.GetDirectoryName(assembly.Location)!,"public-linkage.json")); using var reader=new System.IO.StreamReader(linked); var data=System.Text.Json.Nodes.JsonNode.Parse(reader.ReadToEnd())!; string selected=""; foreach(var element in data["elements"]!.AsArray()) if(element?["id"]?.ToString()=="Example.FrameLoop::SourceLink") selected=element["typedData"]!["Target"]!["reference"]!.ToString(); Console.WriteLine("SELECTED "+selected); return selected=="Example.FrameLoop::TargetNonzero"?0:19;\n')
 f.before[str(main)]=main.read_bytes()
 f.before[str(manifest)]=manifest.read_bytes()
profile=f.root/"profile";profile.mkdir(exist_ok=True);(profile/"projects.json").write_text(json.dumps([{"path":str(p),"title":t,"description":""} for p,t in zip(f.projects,("Reference First","Reference Second"))]))
source=f.projects[0].parent/"SourceLink.celem";expect.set_options(timeout=120000)
trace=f.root/"files.log"
f.report["run"]=["strace","-f","-s","256","-e","trace=execve,openat","-o",str(trace),*f.report["run"]]
def counts():
 lines=trace.read_text(errors="replace").splitlines()
 return (sum("execve(" in x and "csc.dll" in x for x in lines),sum("openat(" in x and any(str(v.parent) in x for v in f.projects) and '.dll"' in x for x in lines))
def open_owner(page):
 w=browser_window(page);w.get_by_role("textbox",name="의미 객체 검색",exact=True).fill("SourceLink")
 w.get_by_role("button",name="검색 확정",exact=True).click()
 row=w.locator(f'[data-object="{NS}::SourceLink"]');expect(row).to_be_visible()
 expect(page.locator("#project-menu")).to_be_enabled()
 row.click(button="right");page.locator(".context-menu").get_by_role("button",name="스키마 열기",exact=True).click()
 editor=page.locator('.window[data-key="schema"]');expect(editor.locator(".object-title-name")).to_have_text("SourceLink");return editor
try:
 f.start(0)
 with sync_playwright() as p,p.chromium.launch(executable_path="/usr/bin/chromium",args=["--no-sandbox"]) as b:
  page=f.setup(b);page.set_default_timeout(120000);editor=open_owner(page)
  ref=editor.get_by_role("button",name="Target 기본값 선택",exact=True);expect(ref).to_have_text("Zero label")
  ref.click();picker=page.get_by_role("dialog",name="기본값 선택",exact=True)
  expect(picker).to_be_visible()
  choices=picker.locator("[data-reference-choice]");expect(choices).to_have_count(3)
  for name,label in [("TargetZero","Zero label"),("TargetNonzero","Nonzero label"),("TargetAbsent","Absent label")]:
   expect(picker.locator(f'[data-reference-choice="{NS}::{name}"]')).to_contain_text(label)
  expect(picker.locator(f'[data-reference-choice="{NS}::WrongTarget"]')).to_have_count(0)
  picker.locator(f'[data-reference-choice="{NS}::TargetNonzero"]').click()
  expect(ref).to_have_text("Nonzero label");expect(editor.get_by_label("Note 기본값",exact=True)).to_have_value("Keep note")
  print("PICKER PASS",count,"compiler and DLL",counts(),flush=True);assert counts()==(0,0)
  save=editor.locator('[data-element-action="confirm"]');expect(save).to_be_enabled();print("save label",save.inner_text(),flush=True);save.click()
  expect(page.locator("#project-menu")).to_be_enabled()
  group=page.get_by_role("dialog",name="관련 변경 검토",exact=True)
  if group.is_visible():
   assert f'{NS}::TargetZero' in source.read_text()
   group.locator("#review-creation").click()
   review=page.locator('.window[data-key="review"]');expect(review).to_be_visible()
   if review.locator('[data-review-advanced]').count():
    review.locator('[data-review-advanced]').click()
    if review.locator('[data-advanced-reviewed]').count():review.locator('[data-advanced-reviewed]').check()
   review.locator("#confirm").click();expect(review).to_be_hidden(timeout=120000)
   expect(page.locator("#project-menu")).to_be_enabled()
  print("save status",page.locator("#status").inner_text(),flush=True)
  print("save error",editor.locator("[data-element-error]").inner_text(),flush=True)
  print("persisted",source.read_text(),flush=True)
  assert f'{NS}::TargetNonzero' in source.read_text()
  editor.get_by_role("button",name="창 닫기",exact=True).click();editor=open_owner(page);expect(editor.get_by_role("button",name="Target 기본값 선택",exact=True)).to_have_text("Nonzero label")
  print("SAVE PASS",count,"compiler and DLL",counts(),flush=True);assert counts()==(0,0)
  page.get_by_role("button",name="프로젝트 실행",exact=True).click()
  expect(page.locator(".run-window:visible [data-run-frame]")).to_have_text("종료 코드 0",timeout=120000)
  print("RUN PASS actual linked data selected; compiler and DLL",counts(),flush=True);assert counts()[0]>0
finally:f.stop();print("evidence",f.root,flush=True)
