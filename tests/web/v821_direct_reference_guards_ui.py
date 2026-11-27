"""Actual direct reference guard scenarios on disposable project profiles.
Usage: REPO BUILD_REPORT 40|400 fallback|mixed|rename|retype|permission|missing|owner|lost-final|lost-owner|mixed-recovered|dirty|stale.
"""
import json,sys,time
from playwright.sync_api import expect,sync_playwright
import v666_workspace_finder_fixture as f
from v821_project_browser_search_labels import NS,browser_window
count=int(sys.argv[3]);assert count in (40,400)
mode=sys.argv[4];assert mode in ("fallback","mixed","rename","retype","permission","missing","owner","lost-final","lost-owner","mixed-recovered","dirty","stale")
semantics={
 "TargetInfo":("schema","field Count single general long;"),
 "LinkInfo":("schema",f"field Target single reference {NS}::TargetInfo; field Note single general string;"),
 "TargetZero":("object",f'use schema {NS}::TargetInfo; data Count = 0; value editorName = "Zero label";'),
 "TargetNonzero":("object",f'use schema {NS}::TargetInfo; data Count = 7; value editorName = "Nonzero label";'),
 "TargetAbsent":("object",f'use schema {NS}::TargetInfo; value editorName = "Absent label";'),
 "WrongTarget":("object",'value editorName = "Wrong label";'),
 "SourceLink":("object",f'use schema {NS}::LinkInfo; data Target = {NS}::TargetZero; data Note = "Keep note";'),
}
if mode=="fallback":
 kind,body=semantics["TargetNonzero"];semantics["TargetNonzero"]=(kind,body+f" use implementation {NS}::TickBody;")
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

def open_owner(page):
 w=browser_window(page);w.get_by_role("textbox",name="의미 객체 검색",exact=True).fill("SourceLink")
 w.get_by_role("button",name="검색 확정",exact=True).click()
 row=w.locator(f'[data-object="{NS}::SourceLink"]');expect(row).to_be_visible()
 expect(page.locator("#project-menu")).to_be_enabled()
 row.click(button="right");page.locator(".context-menu").get_by_role("button",name="스키마 열기",exact=True).click()
 editor=page.locator('.window[data-key="schema"]');expect(editor.locator(".object-title-name")).to_have_text("SourceLink");return editor

target=f.projects[0].parent/"TargetNonzero.celem"
original=source.read_bytes()
original_target=target.read_bytes()
mode_before=target.stat().st_mode
try:
 f.start(0)
 with sync_playwright() as p,p.chromium.launch(executable_path="/usr/bin/chromium",args=["--no-sandbox"]) as b:
  page=f.setup(b);page.set_viewport_size({"width":2200,"height":1200});page.set_default_timeout(30000);editor=open_owner(page)
  ref=editor.get_by_role("button",name="Target 기본값 선택",exact=True)
  expect(ref).to_have_text("Zero label")
  if mode=="dirty":
   w=browser_window(page);w.get_by_role("textbox",name="의미 객체 검색",exact=True).fill("TargetZero")
   w.get_by_role("button",name="검색 확정",exact=True).click()
   w.locator(f'[data-object="{NS}::TargetZero"]').click(button="right")
   page.locator(".context-menu").get_by_role("button",name="새 창으로 열기",exact=True).click()
   other=page.locator(f'.window[data-element-owner="{NS}::TargetZero"]')
   expect(other.get_by_label("Count 기본값",exact=True)).to_have_value("0")
   other.get_by_label("Count 기본값",exact=True).fill("12")
   title=other.locator(".window-title");box=title.bounding_box()
   page.mouse.move(box["x"]+min(180,box["width"]/2),box["y"]+box["height"]/2);page.mouse.down()
   page.mouse.move(1650,260,steps=12);page.mouse.up()
   print("dirty peer moved",other.bounding_box(),"primary",editor.bounding_box(),flush=True)
   editor=open_owner(page)
   ref=editor.get_by_role("button",name="Target 기본값 선택",exact=True)
  ref.click();picker=page.get_by_role("dialog",name="기본값 선택",exact=True);expect(picker).to_be_visible()
  picker.locator(f'[data-reference-choice="{NS}::TargetNonzero"]').click()
  expect(ref).to_have_text("Nonzero label")
  if mode=="mixed":editor.get_by_label("Note 기본값",exact=True).fill("Mixed change")
  save=editor.locator('[data-element-action="confirm"]');expect(save).to_be_enabled()
  hits=[];applies=[];masked=[]
  def intervene(route):
   try:body=route.request.post_data_json
   except Exception:body=None
   if isinstance(body,dict) and body.get("op")=="invoke":
    endpoint=body.get("endpoint");rid=body.get("requestId")
    if endpoint=="directPropertyConfirm":
     hits.append(rid)
     if len(hits)==1:
      if mode=="stale":
       assert source.read_bytes()==original
       body["expectedRevision"]=max(0,int(body["expectedRevision"])-1)
       response=route.fetch(post_data=json.dumps(body))
       route.fulfill(response=response);return
      if mode=="rename":target.write_text(original_target.decode().replace("Nonzero label","External renamed"))
      elif mode=="retype":target.write_text(original_target.decode().replace("TargetInfo","LinkInfo"))
      elif mode=="permission":target.chmod(0)
      elif mode=="missing":target.unlink()
      elif mode=="owner":source.write_bytes(original+b"\n// external owner change\n")
    if endpoint=="blueprint" and body.get("input",{}).get("action")=="applySlots":applies.append(rid)
   if mode not in ("lost-final","lost-owner","mixed-recovered"):
    route.fallback();return
   response=route.fetch();payload=response.json()
   for row in payload.get("results",[]):
    rid=row.get("requestId")
    if (mode=="lost-final" and rid in hits or mode in ("lost-owner","mixed-recovered") and rid in applies) and rid not in masked:
     assert row.get("ok"),row
     if mode=="lost-final":
      assert row.get("result",{}).get("sourceConfirmed") is True,row
      assert b"TargetNonzero" in source.read_bytes()
     masked.append(rid);row.clear();row.update(requestId=rid,ok=False,error={"code":"transport_lost"})
   route.fulfill(response=response,json=payload)
  page.route("**/api/request",intervene)
  save.click()
  expect(page.locator("#project-menu")).to_be_enabled()
  group=page.get_by_role("dialog",name="관련 변경 검토",exact=True)
  review=page.locator('.window[data-key="review"]')
  if mode in ("fallback","mixed"):
   expect(group).to_be_visible();assert source.read_bytes()==original
   assert not hits
   print("PASS unproved or mixed reference requires explicit Review",mode,flush=True)
  elif mode in ("rename","retype","permission","missing","owner"):
   expected=original+b"\n// external owner change\n" if mode=="owner" else original
   assert len(hits)==1 and source.read_bytes()==expected,(hits,source.read_text())
   assert ref.inner_text()=="Nonzero label" or review.is_visible()
   print("PASS late target change refuses direct final commit and retains draft",mode,flush=True)
  elif mode=="lost-final":
   assert len(hits)==len(masked)==1 and b"TargetNonzero" in source.read_bytes()
   final_bytes=source.read_bytes()
   page.unroute_all(behavior="wait");page.close();f.stop();f.start(1)
   page=f.setup(b);editor=open_owner(page)
   expect(editor.get_by_role("button",name="Target 기본값 선택",exact=True)).to_have_text("Nonzero label")
   assert source.read_bytes()==final_bytes
   print("PASS final response loss commits once; restart reads exact saved value",flush=True)
  elif mode in ("lost-owner","mixed-recovered"):
   assert len(applies)==len(masked)==1 and not hits and source.read_bytes()==original
   # The recovered staged receipt is not authorization to reissue Confirm.
   assert any("TargetNonzero" in saved.read_text() for saved in f.projects[0].parent.glob(".confectory/edit-workspaces/*/draft.json"))
   print("PASS lost staging response retained unconfirmed draft",flush=True)
   if mode=="mixed-recovered":
    # Actual UI staged both values. Use the normal explicit host Review
    # request to exercise a recovered receipt in a multi-owner selection.
    page.unroute_all(behavior="wait")
    if group.is_visible():group.get_by_role("button",name="닫기",exact=True).click()
    editor.get_by_role("button",name="창 닫기",exact=True).click()
    w=browser_window(page);w.get_by_role("textbox",name="의미 객체 검색",exact=True).fill("TargetZero")
    w.get_by_role("button",name="검색 확정",exact=True).click()
    w.locator(f'[data-object="{NS}::TargetZero"]').click(button="right")
    page.locator(".context-menu").get_by_role("button",name="스키마 열기",exact=True).click()
    peer=page.locator('.window[data-key="schema"]')
    peer.get_by_label("Count 기본값",exact=True).fill("12")
    peer.locator('[data-element-action="save"]').click()
    expect(page.locator("#project-menu")).to_be_enabled()
    assert source.read_bytes()==original
    ids=[f"{NS}::SourceLink",f"{NS}::TargetZero",f"{NS}::ProjectManifest"]
    f.call("reviewGroup",{"ids":ids,"target":"linux"})
    reviewed=f.state()["review"];assert reviewed["status"]=="ready",reviewed
    result=f.call("confirmGroup",{"ids":ids,"token":reviewed["token"]})
    assert result.get("sourceConfirmed") is True,result
    assert b"TargetNonzero" in source.read_bytes()
    assert b"data Count = 12;" in (f.projects[0].parent/"TargetZero.celem").read_bytes()
    print("PASS recovered reference and separately staged scalar use explicit mixed Review and Confirm",flush=True)

  elif mode=="stale":
   assert len(hits)==2 and len(applies)==1 and b"TargetNonzero" in source.read_bytes(),(hits,applies)
   assert not group.is_visible() and not review.is_visible()
   print("PASS actual stale admission refused before bounded retry; one staged save",flush=True)
  else:
   assert len(hits)==1 and b"TargetNonzero" in source.read_bytes()
   expect(other.get_by_label("Count 기본값",exact=True)).to_have_value("12")
   assert b"data Count = 0;" in (f.projects[0].parent/"TargetZero.celem").read_bytes()
   print("PASS other window unsaved input retained",flush=True)
finally:
 if target.exists():target.chmod(mode_before)
 target.write_bytes(original_target);target.chmod(mode_before)
 f.stop();print("evidence",f.root,flush=True)
