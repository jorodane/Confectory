"""Actual project finder navigation; no source/runtime/permission writes."""
import json,pathlib,sys,time,traceback
from playwright.sync_api import sync_playwright,expect
import v666_workspace_finder_fixture as f
mode=sys.argv[3];page=None
def panel():return page.locator('#workspace-find-panel')
def open_find():
 page.locator('#worker-finder-bubble').click();expect(panel()).to_be_visible();return panel()
def results():return panel().locator('.workspace-find-result')
def search(text,minimum=1):
 field=panel().get_by_role('searchbox');field.fill(text)
 if minimum:expect(results()).not_to_have_count(0)
 else:expect(results()).to_have_count(0)
 return field
def workspace():page.get_by_role('tab',name='Workspace',exact=True).click()
def blank():
 area=page.locator('#workspace').bounding_box()
 for fx in [.75,.45,.2,.9]:
  for fy in [.35,.65,.8,.2]:
   x,y=area['x']+area['width']*fx,area['y']+area['height']*fy
   if page.evaluate('p=>{const e=document.elementFromPoint(p.x,p.y);return e?.closest("#workspace")&&!e.closest(".window,.workspace-decoration,.bubble-dock,.workspace-tabs,.pack-manager-view");}',dict(x=x,y=y)):return dict(x=x-area['x'],y=y-area['y'])
 raise AssertionError('no empty current workspace point')
def add(kind):
 page.locator('#workspace').click(button='right',position=blank());page.locator('[data-workspace-create-menu]').click();page.locator('[data-workspace-tool-create="'+kind+'"]').click()
def note(text):
 add('note');n=page.locator('.workspace-note').last;n.locator('[data-note-editor],textarea').fill(text);return n.get_attribute('data-workspace-item')
def basic():
 workspace();page.locator('#chat-input').fill('검색 뒤에도 보존할 실제 개인 입력');first=note('FinderNeedle 한글 <img src=x onerror=alert(1)>');second=note('FinderNeedle 두 번째 메모')
 open_find();expect(panel().locator('[data-find-mode="elements"]')).to_have_attribute('aria-pressed','true');expect(results()).not_to_have_count(0);panel().locator('[data-find-mode="text"]').click();search('fInDeRnEeDlE');expect(results()).to_have_count(2);expect(panel().locator('img')).to_have_count(0);expect(results().first).to_contain_text('<img src=x');f.checked('authored bubble and elements/text panel search actual placed private notes case-insensitively; user text is literal and source remains untouched')
 field=panel().get_by_role('searchbox');expect(results().nth(1)).to_be_enabled();field.press('ArrowDown');expect(results().nth(1)).to_have_attribute('data-active','true');field.press('Enter');expect(panel()).to_have_count(0);expect(page.locator('[data-workspace-item="'+second+'"]')).to_have_class(__import__('re').compile(r'\bactive\b'));expect(page.locator('#chat-input')).to_have_value('검색 뒤에도 보존할 실제 개인 입력')
 open_find();panel().locator('[data-find-mode="text"]').click();search('FinderNeedle');page.locator('[data-workspace-item="'+first+'"] [data-note-editor], [data-workspace-item="'+first+'"] textarea').fill('LiveChangedNote');search('LiveChangedNote');expect(results()).to_have_count(1);field=panel().get_by_role('searchbox')
 for key,code,composing in [('Enter',13,True),('Escape',27,True),('Enter',229,False),('Escape',229,False)]:
  prevented=field.evaluate('(el,args)=>{const e=new KeyboardEvent("keydown",{key:args[0],keyCode:args[1],isComposing:args[2],bubbles:true,cancelable:true});el.dispatchEvent(e);return e.defaultPrevented}',[key,code,composing]);assert not prevented;expect(panel()).to_be_visible();expect(field).to_have_value('LiveChangedNote')
 field.press('Escape');expect(panel()).to_have_count(0);expect(page.locator('#worker-finder-bubble')).to_be_focused();f.checked('keyboard selection uses the exact current placed node; live note changes refresh results and IME Enter/Escape never navigates or discards the query')
 # Existing Ctrl+F remains the original placed-text feature.
 page.locator('[data-workspace-item="'+first+'"] [data-note-editor], [data-workspace-item="'+first+'"] textarea').press('Control+f');old=page.locator('.placed-text-find');expect(old).to_be_visible();old.get_by_role('searchbox').fill('LiveChangedNote');expect(old.locator('[data-find-count]')).to_have_text('1 / 1');old.get_by_role('searchbox').press('Escape');expect(old).to_have_count(0)
 open_find();search('Main');row=results().filter(has=page.locator('strong',has_text='Main')).first;target=row.get_attribute('data-find-key');assert target;row.click();expect(panel()).to_have_count(0);expect(page.locator('.window:visible')).not_to_have_count(0);assert not f.state().get('review');f.checked('existing placed Ctrl+F remains intact; permitted declaration result uses the existing native opening path and never Save/Review/Confirm or executes a source')
 for _ in range(5):open_find().get_by_role('searchbox').press('Escape')
 page.set_viewport_size(dict(width=390,height=844));open_find();box=panel().bounding_box();assert box['x']>=0 and box['x']+box['width']<=391,box;page.screenshot(path=str(f.root/'finder-mobile-viewport.png'));panel().locator('[data-find-close]').click();page.set_viewport_size(dict(width=1440,height=1000));f.checked('repeat open/close leaves a single panel and the authored layout fits a 390px browser viewport; this is not mobile device execution')
def scope(browser):
 global page
 workspace();note('OnlyProjectA 私有 입력');page.locator('#chat-input').fill('Project A finder input');listing=f.state()['listingId'];add('portal');portal=page.locator('.workspace-portal').last;child_id=portal.get_attribute('data-workspace-item');portal.dblclick();note('ChildOnlyFinderNote');page.locator('#workspace-home-tab').click();open_find();panel().locator('[data-find-mode="text"]').click();search('OnlyProjectA');old=panel();page.evaluate('()=>globalThis.confectoryFlushPresentation()');page.locator('#workspace-tab-'+child_id).click();expect(old).to_have_count(0);open_find();panel().locator('[data-find-mode="text"]').click();search('OnlyProjectA',0);search('ChildOnlyFinderNote');page.locator('#workspace-home-tab').click();expect(panel()).to_have_count(0);open_find();panel().locator('[data-find-mode="text"]').click();search('OnlyProjectA');f.checked('private child Workspace scope searches only its currently placed nodes; switching disposes the old query and callbacks')
 page.evaluate('()=>globalThis.confectoryFlushPresentation()');serialized=json.dumps(f.state()['presentation']);assert 'OnlyProjectA'in serialized and 'ChildOnlyFinderNote'in serialized;search('NeverPersistFinderQuery',0);page.evaluate('()=>globalThis.confectoryFlushPresentation()');assert 'NeverPersistFinderQuery'not in json.dumps(f.state()['presentation']);page.close();f.stop();f.start(1);page=f.setup(browser);expect(panel()).to_have_count(0);expect(page.locator('#chat-input')).to_have_value('Project A finder input');open_find();expect(panel().get_by_role('searchbox')).to_have_value('');panel().locator('[data-find-mode="text"]').click();search('OnlyProjectA');page.evaluate('()=>globalThis.confectoryFlushPresentation()');f.call('leaveProject',{});expect(page.locator('.home-grid')).to_be_visible(timeout=60000);expect(panel()).to_have_count(0);f.checked('cold restart restores original notes/input, never the query/panel; leaving the real ProjectContext disposes search without replaying a navigation')
 f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);page.close();f.stop();f.start(2);page=f.setup(browser);workspace();open_find();panel().locator('[data-find-mode="text"]').click();search('OnlyProjectA',0);expect(page.locator('#chat-input')).not_to_have_value('Project A finder input');panel().locator('[data-find-close]').click();f.checked('same-named project B cannot expose A private note/input through the finder')
def load():
 workspace();note('MetadataFailurePrivateNote');page.locator('#chat-input').fill('목록 조회 실패 뒤에도 보존할 입력')
 page.evaluate('''()=>{const base=fetch;globalThis.__metadataReads=0;globalThis.__rejectMetadata=null;globalThis.fetch=async(...args)=>{let body;try{body=JSON.parse(args[1]?.body||'{}')}catch{}if(body?.op==='invoke'&&body.endpoint==='relationsMap'){__metadataReads++;if(__metadataReads===1)return new Promise((resolve,reject)=>{__rejectMetadata=()=>reject(Error('isolated-read-transport-interrupted'));});}return base(...args);};}''')
 open_find();field=panel().get_by_role('searchbox');field.fill('Main');page.wait_for_function('()=>!!__rejectMetadata');expect(panel().locator('.workspace-find-status')).to_contain_text('확인하고 있습니다');field.press('Enter');expect(panel()).to_be_visible();expect(field).to_have_value('Main');page.evaluate('()=>__rejectMetadata()');expect(panel().locator('[data-find-retry]')).to_be_visible();expect(field).to_have_value('Main');expect(page.locator('#chat-input')).to_have_value('목록 조회 실패 뒤에도 보존할 입력');f.checked('held metadata read never routes or replays Enter while unavailable; injected pre-admission transport failure retains the exact query and private note/chat input')
 panel().locator('[data-find-retry]').click();expect(panel().locator('[data-find-retry]')).to_have_count(0);expect(results()).not_to_have_count(0);expect(results().first).to_be_enabled();assert page.evaluate('__metadataReads')==2;expect(field).to_have_value('Main');assert page.locator('.workspace-note [data-note-editor],.workspace-note textarea').evaluate('el=>el.value??el.textContent')=='MetadataFailurePrivateNote';field.press('Escape');expect(panel()).to_have_count(0);open_find();expect(panel().get_by_role('searchbox')).to_have_value('');panel().locator('[data-find-close]').click();f.checked('only explicit retry performs the existing metadata read, restores results without source writes and never reuses an old query on reentry')
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser)
  try:
   {'basic':basic,'scope':lambda:scope(browser),'load':load}[mode]();f.original();assert not f.errors and not f.external,(f.errors,f.external)
   forbidden={'editDraft','editField','editMetadata','editDeclaration','editViewDeclaration','saveDraft','saveDrafts','reviewDraft','confirmDraft','reviewGroup','confirmGroup','runProject','startAI','prepareAI','nodeTask','startBuild'};assert not forbidden.intersection(row.get('endpoint')for row in f.requests),f.requests
   page.screenshot(path=str(f.root/('finder-'+mode+'-final.png')));page.close();browser.close()
  except Exception:
   try:page.screenshot(path=str(f.root/'failure.png'));(f.root/'failure.html').write_text(page.content())
   except Exception:pass
   raise
except Exception as error:
 (f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:f.save_evidence();f.stop()
print('WORKSPACE_FINDER_FIXTURE',f.root,flush=True)
