"""Real current workspace Browser action, synthetic local projects only.
Run with the normal EditorHome build report and current authoring host:
  python tests/web/editor_menu_current_route_ui.py REPO BUILD_REPORT
Pass base as an optional third argument only to reproduce the old stale admission failure.
Pass candidate 40|257|400 to exercise real registered menus after a bounded scan page.
"""
import json,sys,shutil,re
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import v821_property_window_reopen_ui as r
from editor_navigation import goto_editor
f,d=r.fixture,r.fallback
r.seed();mode=sys.argv[3] if len(sys.argv)>3 else "candidate";library=f.root/'schema-editing';shutil.copytree(f.repo/'packs/schema-editing',library)
for manifest in f.projects:
 action=manifest.parent/'Menu.celem';action.write_text((f.repo/'examples/editor-context-actions/MetadataProposal.celem').read_text().replace('Example.EditorContextActions::MetadataProposal',d.NS+'::Menu'))
 manifest.write_text(manifest.read_text().rstrip()[:-1]+' registry Confectory.SchemaEditing '+json.dumps(str(library/'pack.cpack'))+'; dependency Confectory.SchemaEditing version "0.1.0"; element Menu object "Menu.celem"; }\n')
 # Sort filler objects before Menu so a 400-object declaration is genuinely
 # beyond the first 256-object page (not a lucky early match).
 if len(sys.argv)>4:
  count=int(sys.argv[4]);assert count in (40,255,256,257,400)
  current=len(re.findall(r'\belement\s+\S+\s+object\s+',manifest.read_text()))
  entries=[]
  for i in range(count-current):
   name=f"AAAA{i:04}";path=manifest.parent/(name+".celem")
   path.write_text(f"object {d.NS}::{name} {{}}\n")
   f.before[str(path)]=path.read_bytes();entries.append(f'element {name} object "{path.name}";')
  assert len(entries)==count-current
  manifest.write_text(manifest.read_text().rstrip()[:-1]+"\n"+"\n".join(entries)+"\n}\n")
 for file in (manifest,action):f.before[str(file)]=file.read_bytes()
expect.set_options(timeout=90000)
try:
 with sync_playwright() as p,p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']) as b:
  f.start(0);page=b.new_page(viewport={'width':2000,'height':1200});page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(f.origin+'/') else route.abort());goto_editor(page,f.url)
  browser=r.browser_window(page);r.choose_tree_location(browser,f'[data-tree-id="{d.NS}::StockFolder"]');r.search(browser,d.LABEL,d.TARGET)
  item=browser.locator(f'[data-object="{d.NS}::{d.TARGET}"]');item.click(button='right');page.locator('.context-menu').get_by_role('button',name='스키마 열기',exact=True).click();expect(page.locator('.window[data-key="schema"] [data-property-value]').first).to_be_editable(timeout=30000);page.locator('.window[data-key="schema"] [data-close]').click();expect(page.locator('#project-menu')).to_be_enabled(timeout=30000)
  saved=f.state()['draft'];assert saved['id']==d.NS+'::'+d.TARGET,saved['id']
  list_requests=[];result_codes=[];forced=[];held=[];hold_next=[False];invocations=[];invoke_results={};first_project=f.state()["projectId"]
  def race(route):
   if not route.request.url.startswith(f.origin+'/'):route.abort();return
   if route.request.method=='POST':
    req=route.request.post_data_json
    if req.get('endpoint')=='contextActions' and req.get('input',{}).get('operation')=='invoke':invocations.append(req['requestId'])
    if req.get('endpoint')=='contextActions' and req.get('input',{}).get('operation')=='list':
     list_requests.append(req['expectedRevision'])
     if hold_next[0]:hold_next[0]=False;held.append(route);return
     if not forced:
      prior=f.mount();before=prior['revision'];f.raw({'op':'dispose','view':prior['view']})
      f.call('objects',{'kind':'object','query':''})
      after=f.mount();revision=after['revision'];f.raw({'op':'dispose','view':after['view']})
      assert revision>req['expectedRevision'],(req['expectedRevision'],before,revision)
      forced.append((req['expectedRevision'],before,revision));print('race revision request/before/after',forced,flush=True)
   route.continue_()
  def response(reply):
   try:
    req=reply.request.post_data_json
    if req.get('op')=='update':
     for row in reply.json().get('results',[]):
      if row.get('error',{}).get('code')=='stale_revision':result_codes.append('stale_revision')
      if row.get('requestId') in invocations and row.get('result'):invoke_results[row['requestId']]=row['result']
   except Exception:pass
  page.unroute('**/*');page.route('**/*',race);page.on('response',response)
  def menu(label):
   expect(page.locator('#project-menu')).to_be_enabled(timeout=30000)
   item.click(button='right');button=page.locator('.context-menu').get_by_role('button',name=label,exact=True);expect(button).to_be_visible(timeout=30000);return button
  if mode=='base':
   menu('등록 기능 조회 실패 · 다시 여세요').click();expect(page.locator('#status')).to_have_text('stale_revision');assert len(list_requests)==1 and forced and result_codes;print('PASS baseline actual stale rejected',list_requests,flush=True)
  else:
   menu('등록 기능 · 메타데이터 변경안').click();assert len(list_requests)==2 and list_requests[1]>list_requests[0] and forced and result_codes,(list_requests,forced,result_codes);print('PASS first menu automatic retry',list_requests,flush=True);dialog=page.get_by_role('dialog',name='메타데이터 변경안');expect(dialog).to_be_visible();dialog.locator('[data-action-field]').fill('editorName');dialog.locator('[data-action-value]').fill('"Fixture proposal"');dialog.locator('[data-action-invoke]').click();expect(dialog).to_have_attribute('data-action-status','completed',timeout=30000);expect(dialog.locator('[data-action-result]')).to_contain_text('Fixture proposal');assert f.state()['draft']==saved;dialog.locator('[data-close]').click(); print('PASS current menu actual typed result, draft and source unchanged',flush=True)
   assert len(invocations)==1
   # A real declaration edit after discovery invalidates the prepared token.
   menu('등록 기능 · 메타데이터 변경안').click();dialog=page.get_by_role('dialog',name='메타데이터 변경안');expect(dialog).to_be_visible();dialog.locator('[data-action-field]').fill('editorName');dialog.locator('[data-action-value]').fill('"Must not apply"')
   declaration=f.projects[0].parent/'Menu.celem';original=declaration.read_bytes();declaration.write_bytes(original+b'\n// Changed registration after discovery\n')
   dialog.locator('[data-action-invoke]').click();expect(dialog).to_have_attribute('data-action-status','failed',timeout=30000);assert 'Must not apply' not in dialog.locator('[data-action-result]').inner_text();assert len(invocations)==2 and invoke_results[invocations[-1]]['executed'] is False and f.state()['draft']==saved;declaration.write_bytes(original);dialog.locator('[data-close]').click();print('PASS stale declaration prevents prepared invocation',flush=True)
   body=library/'Call.csbody';raw=body.read_bytes();body.write_bytes(raw+b'\n// Synthetic changed exact body\n');menu('등록 기능 · 메타데이터 변경안 · 미지원');body.write_bytes(raw);print('PASS modified body remains unavailable',flush=True);page.keyboard.press('Escape')
   # Close the actual menu while a request is held; advance a real host revision,
   # then release the original request. It must neither reopen nor retry.
   hold_next[0]=True;item.click(button='right');expect(page.locator('.context-menu').get_by_role('button',name='등록 기능 조회 중…')).to_be_visible();page.wait_for_function('()=>!!document.querySelector(".context-menu")');assert held
   count=len(list_requests);page.keyboard.press('Escape');expect(page.locator('.context-menu')).to_have_count(0);f.call('objects',{'kind':'object','query':''});held.pop().continue_();page.wait_for_timeout(500);assert len(list_requests)==count and page.locator('.context-menu').count()==0;print('PASS closed menu ignores stale response and never retries',flush=True)
   # Same semantic IDs in the second project: old menu reply must not create UI.
   hold_next[0]=True;item.click(button='right');expect(page.locator('.context-menu').get_by_role('button',name='등록 기능 조회 중…')).to_be_visible();assert held;count=len(list_requests);page.keyboard.press('Escape');page.locator('.brand').click();expect(page.locator('.home-grid')).to_be_visible();page.locator('.project-card').filter(has=page.get_by_role('heading',name=d.SECOND,exact=True)).locator('[data-enter]').click();expect(page.locator('.work-body')).to_be_visible();expect(page.locator('#title')).to_contain_text(d.SECOND);held.pop().continue_();page.wait_for_timeout(500);assert len(list_requests)==count and page.locator('.context-menu').count()==0;print('PASS same-ID project switch rejects late menu response',flush=True)
   assert f.state()['projectId']!=first_project
   browser=r.browser_window(page);r.choose_tree_location(browser,f'[data-tree-id="{d.NS}::StockFolder"]');r.search(browser,d.LABEL,d.TARGET);item=browser.locator(f'[data-object="{d.NS}::{d.TARGET}"]');menu('등록 기능 · 메타데이터 변경안').click();dialog=page.get_by_role('dialog',name='메타데이터 변경안');expect(dialog).to_be_visible();dialog.locator('[data-action-cancel]').click();assert len(invocations)==2;print('PASS same-ID second project menu independently available',flush=True)
  f.original()
finally:f.stop();print('evidence',f.root,flush=True)
