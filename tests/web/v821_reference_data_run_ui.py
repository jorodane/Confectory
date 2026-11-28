"""Actual direct reference save without build, followed by explicit Run consuming new data.
Usage: REPO BUILD_REPORT 40|400 [--detached] [--continuous] [--profile]. Requires SDK and strace (except --profile).
Synthetic FrameLoop copies only.
"""
import json,sys,time
from playwright.sync_api import expect,sync_playwright
import v666_workspace_finder_fixture as f
from v821_project_browser_search_labels import NS,browser_window,choose_tree_location
from save_timing import arm_save_timing,actual_save_timing
count=int(sys.argv[3]);assert count in (40,400)
continuous="--continuous" in sys.argv;tracing="--profile" not in sys.argv
assert tracing or continuous
if continuous:f.env["CONFECTORY_UI_TRACE"]="1"
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
if tracing:f.report["run"]=["strace","-f","-s","256","-e","trace=execve,openat","-o",str(trace),*f.report["run"]]
def counts():
 if not tracing:raise AssertionError("untraced performance run cannot assert compiler or DLL accesses")
 lines=trace.read_text(errors="replace").splitlines()
 return (sum("execve(" in x and "csc.dll" in x for x in lines),sum("openat(" in x and any(str(v.parent) in x for v in f.projects) and '.dll"' in x for x in lines))
def ordinary_counts(label):
 if tracing:
  print(label,count,"compiler and DLL",counts(),flush=True);assert counts()==(0,0)
 else:print(label,count,"untraced performance",flush=True)
def save_reference(page,editor,target):
 save=editor.locator('[data-element-action="confirm"]');expect(save).to_have_text("저장");expect(save).to_be_enabled()
 if continuous:arm_save_timing(save)
 started=time.monotonic();save.click()
 deadline=time.monotonic()+120
 while time.monotonic()<deadline and f'data Target = {NS}::{target};' not in source.read_text():page.wait_for_timeout(100)
 assert f'data Target = {NS}::{target};' in source.read_text()
 if continuous:print("save-file-ms",round((time.monotonic()-started)*1000,1),flush=True)
 expect(page.locator("#project-menu")).to_be_enabled()
 expect(page.get_by_role("dialog",name="관련 변경 검토",exact=True)).to_be_hidden()
 expect(page.locator('.window[data-key="review"]')).to_be_hidden()
 if continuous:
  timing=actual_save_timing(page);print("save-browser-success-ms",round(timing["success"],1),flush=True);print("save-browser-ready-ms",round(timing["ready"],1),flush=True)
 ordinary_counts("SAVE PASS")
def open_owner(page):
 w=browser_window(page);w.get_by_role("textbox",name="의미 객체 검색",exact=True).fill("SourceLink")
 w.get_by_role("button",name="검색 확정",exact=True).click()
 row=w.locator(f'[data-object="{NS}::SourceLink"]');expect(row).to_be_visible()
 expect(page.locator("#project-menu")).to_be_enabled()
 row.click(button="right");page.locator(".context-menu").get_by_role("button",name="새 창으로 열기" if "--detached" in sys.argv else "스키마 열기",exact=True).click()
 editor=page.locator(f'.window[data-element-owner="{NS}::SourceLink"][data-element-mode="properties"]:visible' if "--detached" in sys.argv else '.window[data-key="schema"]');expect(editor.locator(".object-title-name")).to_have_text("SourceLink");return editor
try:
 f.start(0)
 with sync_playwright() as p,p.chromium.launch(executable_path="/usr/bin/chromium",args=["--no-sandbox"]) as b:
  page=f.setup(b);page.set_default_timeout(120000);editor=open_owner(page)
  if "--verify-card-reference" in sys.argv:
   assert "--detached" not in sys.argv
   w=browser_window(page);choose_tree_location(w,f'[data-namespace="{NS}"]')
   w.get_by_role("textbox",name="의미 객체 검색",exact=True).fill("SourceLink");w.get_by_role("button",name="검색 확정",exact=True).click()
   card=w.locator(f'[data-object="{NS}::SourceLink"]');expect(card).to_be_visible()
   card.click(button="right");page.locator(".context-menu").get_by_role("button",name="스키마 열기",exact=True).click()
   card.evaluate("el=>globalThis.__referenceCard=el")
  ref=editor.get_by_role("button",name="Target 기본값 선택",exact=True);expect(ref).to_have_text("Zero label")
  ref.click();picker=page.get_by_role("dialog",name="기본값 선택",exact=True)
  expect(picker).to_be_visible()
  choices=picker.locator("[data-reference-choice]");expect(choices).to_have_count(3)
  for name,label in [("TargetZero","Zero label"),("TargetNonzero","Nonzero label"),("TargetAbsent","Absent label")]:
   expect(picker.locator(f'[data-reference-choice="{NS}::{name}"]')).to_contain_text(label)
  expect(picker.locator(f'[data-reference-choice="{NS}::WrongTarget"]')).to_have_count(0)
  picker.locator(f'[data-reference-choice="{NS}::TargetNonzero"]').click()
  expect(ref).to_have_text("Nonzero label");expect(editor.get_by_label("Note 기본값",exact=True)).to_have_value("Keep note")
  ordinary_counts("PICKER PASS")
  save_reference(page,editor,"TargetNonzero")
  if "--verify-card-reference" in sys.argv:
   assert card.evaluate("el=>el===globalThis.__referenceCard")
   browser_window(page);card.hover();tip=page.locator(".floating-object-ref")
   expect(tip).to_contain_text("직접 참조: Nonzero label");expect(tip).not_to_contain_text("Zero label")
   card.click(button="right");page.locator(".context-menu").get_by_role("button",name="스키마 열기",exact=True).click()
   print("PASS retained Browser card reads changed direct reference from current map",flush=True)
  if continuous:
   print("reference-repeated-begin",flush=True)
   for target,label in [("TargetZero","Zero label"),("TargetNonzero","Nonzero label"),("TargetAbsent","Absent label"),("TargetZero","Zero label"),("TargetNonzero","Nonzero label")]:
    ref.click();picker=page.get_by_role("dialog",name="기본값 선택",exact=True);expect(picker).to_be_visible();picker.locator(f'[data-reference-choice="{NS}::{target}"]').click();expect(ref).to_have_text(label)
    save_reference(page,editor,target)
   print("reference-repeated-end",flush=True)
  print("save status",page.locator("#status").inner_text(),flush=True)
  print("save error",editor.locator("[data-element-error]").inner_text(),flush=True)
  print("persisted",source.read_text(),flush=True)
  assert f'{NS}::TargetNonzero' in source.read_text()
  editor.get_by_role("button",name="창 닫기",exact=True).click();editor=open_owner(page);expect(editor.get_by_role("button",name="Target 기본값 선택",exact=True)).to_have_text("Nonzero label")
  ordinary_counts("REOPEN PASS")
  page.get_by_role("button",name="프로젝트 실행",exact=True).click()
  expect(page.locator(".run-window:visible [data-run-frame]")).to_have_text("종료 코드 0",timeout=120000)
  if tracing:
   print("RUN PASS actual linked data selected; compiler and DLL",counts(),flush=True);assert counts()[0]>0
  else:print("RUN PASS actual linked data selected; untraced performance",flush=True)
finally:f.stop();print("evidence",f.root,flush=True)
