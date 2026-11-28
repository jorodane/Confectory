"""Disposable Chromium detached long/string save guards.

Usage: python tests/web/detached_long_data_save_guards.py OVERLAY BUILD_REPORT MODE [400] [--string]
MODE: invalid | dirty | guard-schema | guard-permission | guard-object | lost | lost-final.
Uses the existing performance sample and workspace finder host fixture.
"""
import sys,shutil
from pathlib import Path
import v666_workspace_finder_fixture as f
import v821_direct_property_save_ui as d
from v821_project_browser_search_labels import browser_window
from editor_navigation import goto_editor
from playwright.sync_api import sync_playwright,expect
mode=sys.argv[3]
flags=set(sys.argv[4:]);assert flags<={"400","--string"}
string="--string" in flags;assert not(string and mode=="invalid")
field_name="Note" if string else "Count"
old_value="Synthetic sample C" if string else "10"
new_value="Local string save" if string else "11"
old_marker=b'data Note = "Synthetic sample C";' if string else b"data Count = 10;"
new_marker=b'data Note = "Local string save";' if string else b"data Count = 11;"
external_marker=b'data Note = "External string";' if string else b"data Count = 12;"
checkpoint_marker=new_value.encode() if string else new_marker
sample=f.root/'performance-sample';shutil.copytree(Path(__file__).resolve().parents[2]/'examples/performance-sample',sample)
if "400" in flags:
 manifest=sample/'project.cpack';entries=[]
 for i in range(400):
  name=f"Extra{i:04}";source=sample/f"{name}.celem"
  source.write_text(f"object Confectory.PerformanceSample::{name} {{}}\n")
  entries.append(f'element {name} object "{source.name}";')
 manifest.write_text(manifest.read_text().rstrip()[:-1]+"\n"+"\n".join(entries)+"\n}\n")
f.env['CONFECTORY_WEB_PROJECT']=str(sample/'project.cpack');expect.set_options(timeout=60000)
source=sample/'SampleC.celem';schema=sample/'SampleInfo.celem';original=source.read_bytes();schema_original=schema.read_bytes()
def open_window(page):
 bw=browser_window(page);bw.get_by_role('textbox',name='의미 객체 검색',exact=True).fill('Sample C');bw.get_by_role('button',name='검색 확정',exact=True).click()
 owner='Confectory.PerformanceSample::SampleC';row=bw.locator(f'[data-object="{owner}"]');expect(row).to_be_visible();expect(page.locator('#project-menu')).to_be_enabled()
 row.click(button='right');page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click()
 w=page.locator(f'.window[data-element-owner="{owner}"]:visible');expect(d.value(w,field_name)).to_have_value(old_value);expect(d.value(w,field_name)).to_be_editable()
 page.evaluate('()=>confectoryFlushPresentation()');expect(page.locator('#project-menu')).to_be_enabled();return w
try:
 with sync_playwright() as p,p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as browser:
  f.start(0);page=f.setup(browser);page.set_viewport_size({'width':2000,'height':1200});w=open_window(page);field=d.value(w,field_name);button=w.locator('[data-element-action=confirm]')
  if mode=='dirty':
   peer_source=sample/'SampleB.celem';peer_original=peer_source.read_bytes()
   bw=browser_window(page);bw.get_by_role('textbox',name='의미 객체 검색',exact=True).fill('Sample B');bw.get_by_role('button',name='검색 확정',exact=True).click()
   bw.locator('[data-object="Confectory.PerformanceSample::SampleB"]').click(button='right')
   page.locator('.context-menu').get_by_role('button',name='새 창으로 열기',exact=True).click()
   other=page.locator('.window[data-element-owner="Confectory.PerformanceSample::SampleB"]:visible')
   expect(d.value(other,'Count')).to_have_value('10')
   d.value(other,'Count').fill('12')
   title=other.locator('.window-title');box=title.bounding_box()
   page.mouse.move(box['x']+min(180,box['width']/2),box['y']+box['height']/2);page.mouse.down()
   page.mouse.move(1600,260,steps=12);page.mouse.up()
   w.locator('.window-title').click()
   field.fill(new_value);expect(button).to_have_text('저장')
   button.click();expect(page.locator('#status')).to_have_text('저장했습니다.')
   expect(page.locator('#project-menu')).to_be_enabled()
   assert source.read_bytes()==original.replace(old_marker,new_marker)
   expect(d.value(other,'Count')).to_have_value('12')
   assert peer_source.read_bytes()==peer_original
   print('PASS detached direct save retained independent unsaved input and peer source',flush=True)
  elif mode=='invalid':
   field.fill('1.5');mark=len(f.requests)
   if button.is_enabled():button.click();expect(page.locator('#project-menu')).to_be_enabled()
   assert source.read_bytes()==original and not any(x['endpoint']=='confirmGroup' for x in f.requests[mark:])
   print('PASS fractional long input not persisted',flush=True)
  else:
   field.fill(new_value);expect(button).to_have_text('저장');seen=[];applies=[];masked=[];settled=[];finals=[]
   def route_guard(route):
    q=route.request.post_data_json if route.request.method=='POST' else {}
    if q.get('op')=='invoke' and q.get('endpoint')=='blueprint':
     action=q.get('input',{}).get('action')
     if action=='applySlots':applies.append(q['requestId'])
     if action=='settledSlots':settled.append(q['requestId'])
    if mode.startswith('guard') and q.get('op')=='invoke' and q.get('endpoint')=='confirmGroup' and not seen:
     assert source.read_bytes()==original
     if mode=='guard-schema':schema.write_bytes(schema_original.replace(b'Note single general string',b'Note single general bool') if string else schema_original.replace(b'Count single general long',b'Count single general bool'))
     elif mode=='guard-permission':source.chmod(0o400)
     elif mode=='guard-object':source.write_bytes(original.replace(old_marker,external_marker))
     seen.append(True)
    if mode=='lost-final' and q.get('op')=='invoke' and q.get('endpoint')=='confirmGroup':
     finals.append(q['requestId'])
    if mode in ('lost','lost-final'):
     response=route.fetch();payload=response.json()
     for row in payload.get('results',[]):
      rid=row.get('requestId')
      if mode=='lost-final' and rid in finals:
       assert row.get('ok') and row.get('result',{}).get('sourceConfirmed') is True,row
       assert new_marker in source.read_bytes()
       masked.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport_lost'})
      if mode=='lost' and rid in applies+settled:
       if rid in applies:
        assert row.get('ok') and row.get('result',{}).get('checkpointSaved' if string else 'ownerSettled') is True,row
       masked.append(rid);row.clear();row.update(requestId=rid,ok=False,error={'code':'transport_lost'})
     route.fulfill(response=response,json=payload)
    else:route.fallback()
   page.route('**/api/request',route_guard)
   try:
    button.click()
    if mode=='lost-final':
     expect(page.locator('#status')).to_have_text('transport_lost',timeout=120000)
     expect(page.locator('#project-menu')).to_be_enabled(timeout=120000)
     assert len(finals)==len(set(masked))==1
     assert source.read_bytes()==original.replace(old_marker,new_marker)
    elif mode=='lost':
     expect(page.locator('#status')).to_have_text('transport_lost',timeout=120000)
     assert len(applies)==1 and settled and len(masked)>=2,(applies,settled,masked)
     assert source.read_bytes()==original
    else:
     expect(page.locator('#project-menu')).to_be_enabled(timeout=120000)
     assert seen
     assert source.read_bytes()==(original.replace(old_marker,external_marker) if mode=='guard-object' else original)
     assert mode!='guard-schema' or schema.read_bytes()!=schema_original
     assert mode!='guard-permission' or source.stat().st_mode&0o222==0
    if mode!='lost-final':
     assert any(checkpoint_marker in p.read_bytes() for p in (sample/'.confectory/edit-workspaces').glob('*/draft.json'))
     print('PASS',mode,'unchanged confirmed source and retained attempted checkpoint',flush=True)
   finally:
    if mode=='guard-permission':source.chmod(0o600)
    page.unroute_all(behavior='wait')
   if mode in ('lost','lost-final'):
    page.close();f.stop();f.env.pop('CONFECTORY_WEB_PROJECT',None);f.start(1);page=browser.new_page(viewport={'width':2000,'height':1200});goto_editor(page,f.url)
    page.locator('.project-card').filter(has=page.get_by_role('heading',name='Confectory.PerformanceSample',exact=True)).locator('[data-enter]').click()
    w=page.locator('.window[data-element-owner="Confectory.PerformanceSample::SampleC"]:visible');expect(d.value(w,field_name)).to_have_value(new_value)
    if mode=='lost-final':
     expect(w.locator('[data-element-action=confirm]')).to_be_disabled()
     assert source.read_bytes()==original.replace(old_marker,new_marker)
     print('PASS final reply lost; source committed once and clean on restart',flush=True)
    else:
     assert source.read_bytes()==original
     print('PASS lost reply restart retains draft without committing source',flush=True)
finally:f.stop();print('evidence',f.root,flush=True)
