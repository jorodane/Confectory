"""Actual owned definition/Data search, preserving source and existing read/CAS gates."""
import json,sys,time,traceback
from playwright.sync_api import sync_playwright,expect
import v666_finder_content_fixture as f
mode=sys.argv[3];page=None;ns='Example.FrameLoop::'
def panel():return page.locator('#workspace-find-panel')
def matches():return panel().locator('.workspace-find-result')
def open_find():page.locator('#worker-finder-bubble').click();expect(panel()).to_be_visible();return panel()
def search(text,ids):
 field=panel().get_by_role('searchbox');field.fill(text);expect(panel().locator('[data-find-content-refresh]')).to_be_visible(timeout=120000);expect(panel().locator('.workspace-find-status')).not_to_contain_text('확인하고 있어요',timeout=120000)
 expect(matches()).to_have_count(len(ids));assert sorted(matches().evaluate_all('els=>els.map(el=>el.dataset.findKey)'))==sorted('object:'+ns+id for id in ids);return field
def basic():
 page.get_by_role('tab',name='Workspace',exact=True).click();page.locator('#chat-input').fill('내용 조회 중에도 유지할 개인 입력');selected=(f.states[-1].get('draft')or{}).get('id');open_find();panel().locator('[data-find-mode="text"]').click();search('ContentNeedleAlpha',['Record']);expect(matches().first).to_contain_text('같은 표시명');expect(matches().first).to_contain_text('ContentNeedleAlpha');assert (f.states[-1].get('draft')or{}).get('id')==selected;expect(page.locator('#chat-input')).to_have_value('내용 조회 중에도 유지할 개인 입력');f.checked('unplaced owned Data is searchable through the existing read while exact display-name identity and selected source/private input remain intact')
 search('9223372036854775806',['Record','ChildRecord']);search('-9223372036854775805',['OtherRecord']);search('복합 값 😀',['Record','ChildRecord']);search('FunctionDescriptionNeedle',['Main']);search('ObjectDescriptionNeedle',['Record']);search('UnregisteredSourceMustNeverBeRead',[]);f.checked('exact int64 and inherited/compound Unicode values plus owned descriptions match; arbitrary unregistered file contents are never indexed')
 # The existing native boundary continues rejecting a registered dependency ID.
 f.call('browserElements',{'ids':['Confectory.FrameControl::Open']},False)
 before=f.call('browserElements',{'ids':[ns+'Record']})['rows'][0];version={k:before[k]for k in ['revision','textHash','viewHash']};caption=next(row for row in before['fields']if row['name']=='Caption');assert caption['writable'];args={'id':ns+'Record','column':caption['column'],'valueJson':'"NewDataNeedleAfterCAS"','version':version};out=f.call('editBrowserElement',args);assert out['accepted']and out['sourceWritten']is False;stale=f.call('editBrowserElement',args);assert stale['accepted']is False and stale['code']=='element-value-stale'
 search('NewDataNeedleAfterCAS',['Record']);search('ContentNeedleAlpha',[]);f.checked('a real fixture-only staged Data edit invalidates the snapshot; native stale CAS and external-owner rejection remain enforced without Confirm/source writes')
 search('NewDataNeedleAfterCAS',['Record']);expect(matches().first).to_be_enabled();matches().first.click();expect(panel()).to_have_count(0);end=time.monotonic()+12
 while time.monotonic()<end:
  state=f.states[-1]
  if (state.get('draft')or{}).get('id')==ns+'Record'or any(row.get('id')==ns+'Record'for row in state.get('editorViews',[])):break
  page.wait_for_timeout(50) # Pump the routed renderer transport while observing its state.
 else:raise AssertionError(dict(state={k:state.get(k)for k in ['draft','schema','declaration','editorViews']},outcomes=f.outcomes[-6:]))
 f.checked('content match opens the original qualified object through the existing definition/property owner path')


def lifecycle(browser):
 global page
 page.get_by_role('tab',name='Workspace',exact=True).click();page.locator('#chat-input').fill('중단·재시작 후 보존할 내용 검색 입력')
 page.evaluate('''()=>{const base=fetch;globalThis.__contentCalls=0;globalThis.__holdContent=true;globalThis.__failContent=false;globalThis.__releaseContent=null;globalThis.fetch=async(...args)=>{let body;try{body=JSON.parse(args[1]?.body||'{}')}catch{}if(body?.op==='invoke'&&body.endpoint==='browserElements'){__contentCalls++;if(__failContent){__failContent=false;throw Error('isolated-content-read-interrupted');}if(__holdContent){__holdContent=false;return new Promise(resolve=>__releaseContent=()=>resolve(base(...args)));}}return base(...args);};}''')
 open_find();panel().locator('[data-find-mode="text"]').click();field=panel().get_by_role('searchbox');field.fill('ContentNeedleAlpha');page.wait_for_function('()=>!!__releaseContent');field.fill('ContentNeedleBeta');field.press('Enter');expect(panel()).to_be_visible();page.evaluate('()=>__releaseContent()');search('ContentNeedleBeta',['OtherRecord']);assert page.evaluate('__contentCalls')==1;f.checked('delayed all-fields snapshot uses the latest query, never the old word or an Enter pressed while loading')
 page.evaluate('()=>{__holdContent=true;__releaseContent=null;}');panel().locator('[data-find-content-refresh]').click();page.wait_for_function('()=>!!__releaseContent');field.press('Escape');expect(panel()).to_have_count(0);page.evaluate('()=>__releaseContent()');page.wait_for_timeout(200);expect(panel()).to_have_count(0);open_find();expect(panel().get_by_role('searchbox')).to_have_value('');panel().locator('[data-find-mode="text"]').click();page.evaluate('()=>__failContent=true');field=panel().get_by_role('searchbox');field.fill('ContentNeedleAlpha');expect(panel().locator('.workspace-find-status')).to_contain_text('확인하지 못했어요');expect(field).to_have_value('ContentNeedleAlpha');expect(page.locator('#chat-input')).to_have_value('중단·재시작 후 보존할 내용 검색 입력');panel().locator('[data-find-content-refresh]').click();search('ContentNeedleAlpha',['Record']);f.checked('close retires delayed content and query; pre-admission read failure preserves input and requires explicit retry')
 field.fill('NeverPersistContentQuery');expect(matches()).to_have_count(0);page.evaluate('()=>globalThis.confectoryFlushPresentation()');assert 'NeverPersistContentQuery'not in json.dumps(f.state()['presentation']);page.close();f.stop();f.start(1);page=f.setup(browser);expect(panel()).to_have_count(0);expect(page.locator('#chat-input')).to_have_value('중단·재시작 후 보존할 내용 검색 입력');open_find();expect(panel().get_by_role('searchbox')).to_have_value('');panel().locator('[data-find-mode="text"]').click();search('ContentNeedleAlpha',['Record']);field=panel().get_by_role('searchbox');field.press('Escape');page.evaluate('()=>globalThis.confectoryFlushPresentation()');f.call('leaveProject',{});expect(page.locator('.home-grid')).to_be_visible(timeout=60000);page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(2);page=f.setup(browser);open_find();panel().locator('[data-find-mode="text"]').click();search('ContentNeedleAlpha',[]);search('OtherProjectOnlyValue',['Record']);f.checked('cold restores only private input; identical namespace/IDs in project B cannot adopt A content or replay its query')
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser)
  try:
   {'basic':basic,'lifecycle':lambda:lifecycle(browser)}[mode]();f.original();assert not f.errors and not f.external,(f.errors,f.external);forbidden={'editDraft','editField','editMetadata','editDeclaration','editViewDeclaration','editBrowserElement','saveDraft','saveDrafts','reviewDraft','confirmDraft','reviewGroup','confirmGroup','runProject','startAI','prepareAI','nodeTask','startBuild'};assert not forbidden.intersection(row.get('endpoint')for row in f.requests),f.requests
   reads=[r for r in f.requests if r.get('endpoint')=='browserElements'];assert reads and all(1<=len(r['input']['ids'])<=64 and len(set(r['input']['ids']))==len(r['input']['ids']) and all(id.startswith(ns)for id in r['input']['ids'])for r in reads);page.screenshot(path=str(f.root/('finder-content-'+mode+'-final.png')));page.close();browser.close()
  except Exception:
   try:page.screenshot(path=str(f.root/'failure.png'));(f.root/'failure.html').write_text(page.content())
   except Exception:pass
   raise
except Exception as error:(f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:f.save_evidence();f.stop()
print('FINDER_CONTENT_FIXTURE',f.root,flush=True)
