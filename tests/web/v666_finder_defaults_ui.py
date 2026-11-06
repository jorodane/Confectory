"""Actual owned defaults projection and authored finder, no writes from search."""
import json,sys,time,traceback
from playwright.sync_api import sync_playwright,expect
import v666_finder_defaults_fixture as defaults
f=defaults.f;ns=defaults.ns;mode=sys.argv[3];page=None
panel=lambda:page.locator('#workspace-find-panel')
def open_find():
 page.get_by_role('tab',name='Workspace',exact=True).click();page.locator('#worker-finder-bubble').click();expect(panel()).to_be_visible();panel().locator('[data-find-mode="text"]').click()
def search(text,ids):
 panel().get_by_role('searchbox').fill(text);expect(panel().locator('[data-find-content-refresh]')).to_be_visible(timeout=120000);expect(panel().locator('.workspace-find-status')).not_to_contain_text('확인하고 있어요',timeout=120000);rows=panel().locator('.workspace-find-result');expect(rows).to_have_count(len(ids),timeout=15000);assert sorted(rows.evaluate_all('els=>els.map(e=>e.dataset.findKey)'))==sorted('object:'+ns+x for x in ids)
def native():return f.call('finderContent',{'ids':[ns+x for x in ['DefaultInfo','UnknownDefaults','InvalidDefaults','OrphanDefaults','UnmarkedDefaults','BudgetDefaults','CountDefaults','LargeDefaults']]})['rows']
def normal():
 before=f.state().get('draft');rows=native();good=rows[0];fields=good['fields'];assert not any(x['name'].startswith('editorFieldDefault_')or x['name']=='editorInformationDefaults'for x in fields);value={x['name']:x['valueJson']for x in fields};assert value['기본값 · Greeting']=='"\\uae30\\ubcf8\\uc778\\uc0ac\\ud83d\\ude00"';assert value['기본값 · Huge']=='9223372036854775806';assert f.state().get('draft')==before;generic=f.call('browserElements',{'ids':[ns+'DefaultInfo']})['rows'][0];assert any(x['name']=='editorFieldDefault_Greeting'for x in generic['fields'])
 for row in rows[1:7]:assert row['status']=='available'and row['incomplete']is True and any(x['name']=='설명'for x in row['fields'])
 f.checked('marked directly declared defaults are projected as original JSON lexemes; bad/unmarked/unknown records remain partial without raw fallback or selection changes')
 open_find()
 for query in ['기본인사😀','雪🚀','복합기본값😀','9223372036854775806']:search(query,['DefaultInfo']+(['Record','ChildRecord']if query=='9223372036854775806'else[]))
 for query in ['NestedDefaultPayloadMustNotIndex','DefaultImagePayloadMustNotIndex','UnknownDefaultMustNotIndex','OrphanDefaultMustNotIndex','UnmarkedDefaultMustNotIndex','BudgetDefaultMustNotIndex','CountDefaultMustNotIndex']:search(query,[])
 search('LargeDefaultPrefixNeedle',['LargeDefaults']);search('LargeDefaultTailMustBePartial',[]);expect(panel().locator('.workspace-find-status')).to_contain_text('미지원/확인 불가');f.checked('actual finder decodes scalar/list/compound Unicode defaults, keeps int64 exact, omits nested payloads and invalid records, reports bounded text partial')
 search('기본인사😀',['DefaultInfo']);panel().locator('.workspace-find-result').click();expect(panel()).to_have_count(0);end=time.monotonic()+25
 while time.monotonic()<end:
  if f.states[-1].get('draft',{}).get('id')==ns+'DefaultInfo'and (f.states[-1].get('schema')or{}).get('id')==ns+'DefaultInfo':break
  page.wait_for_timeout(50)
 else:raise AssertionError('exact information owner did not open')
 expect(page.locator('#chat-input')).to_have_value('기본값 검색 중 보존할 개인 입력');f.checked('match enters the existing owned information definition while original bytes and private input survive')
def lifecycle(browser):
 global page
 open_find();search('기본인사😀',['DefaultInfo']);panel().get_by_role('searchbox').press('Escape');f.call('select',{'id':ns+'DefaultInfo'});draft=f.state()['draft'];old=draft['text'];f.call('objects',{'kind':'object','query':''});f.call('editDraft',{'id':ns+'DefaultInfo','revision':draft['revision'],'text':old.replace('ude00','ude80',1)});f.call('select',{'id':ns+'Tick'});open_find();search('기본인사🚀',['DefaultInfo']);search('기본인사😀',[]);history=f.call('draftHistory',{'action':'inspect'});f.call('draftHistory',{'action':'undo','token':history['undo']['token']});search('기본인사😀',['DefaultInfo']);search('기본인사🚀',[]);history=f.call('draftHistory',{'action':'inspect'});f.call('draftHistory',{'action':'redo','token':history['redo']['token']});search('기본인사🚀',['DefaultInfo']);history=f.call('draftHistory',{'action':'inspect'});f.call('draftHistory',{'action':'undo','token':history['undo']['token']});search('기본인사😀',['DefaultInfo']);panel().get_by_role('searchbox').fill('DefaultQueryMustNotPersist');page.evaluate('()=>globalThis.confectoryFlushPresentation()');assert 'DefaultQueryMustNotPersist'not in json.dumps(f.state()['presentation']);page.close();f.stop();f.start(1);page=f.setup(browser);expect(panel()).to_have_count(0);open_find();expect(panel().get_by_role('searchbox')).to_have_value('');search('기본인사😀',['DefaultInfo']);panel().get_by_role('searchbox').press('Escape');f.call('leaveProject',{});expect(page.locator('.home-grid')).to_be_visible();page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(2);page=f.setup(browser);open_find();search('기본인사😀',[]);search('다른프로젝트🚀',['DefaultInfo']);f.checked('off-page draft/Undo invalidates typed defaults; cold/home/new project never adopts prior query or same-ID values')
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser);page.locator('#chat-input').fill('기본값 검색 중 보존할 개인 입력')
  try:
   if mode=='baseline':
    open_find();search('기본인사😀',[]);search('NestedDefaultPayloadMustNotIndex',['DefaultInfo']);f.checked('published baseline misses Unicode defaults and indexes nested encoded payload text because it searches internal storage strings')
   else:{'normal':normal,'lifecycle':lambda:lifecycle(browser)}[mode]()
   f.original();assert not f.errors and not f.external,(f.errors,f.external);assert not {'editDraft','saveDraft','reviewDraft','confirmDraft','editField','startAI','runProject'}.intersection(r.get('endpoint')for r in f.requests);page.screenshot(path=str(f.root/('finder-defaults-'+mode+'.png')));page.close();browser.close()
  except Exception:
   try:page.screenshot(path=str(f.root/'failure.png'));(f.root/'failure.html').write_text(page.content())
   except Exception:pass
   raise
except Exception as error:(f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:f.save_evidence();f.stop()
print('FINDER_DEFAULTS_FIXTURE',f.root,flush=True)
