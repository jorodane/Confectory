"""Direct requirement-name search via the actual owned read and authored finder."""
import json,sys,traceback
from playwright.sync_api import sync_playwright,expect
import v666_finder_modules_fixture as x
f=x.f;ns=x.ns;mode=sys.argv[3];page=None
panel=lambda:page.locator('#workspace-find-panel')
def open_find():
 page.get_by_role('tab',name='Workspace',exact=True).click();page.locator('#worker-finder-bubble').click();expect(panel()).to_be_visible();panel().locator('[data-find-mode=text]').click()
def search(query,names):
 panel().get_by_role('searchbox').fill(query);expect(panel().locator('[data-find-content-refresh]')).to_be_visible(timeout=120000);expect(panel().locator('.workspace-find-status')).not_to_contain_text('확인하고 있어요',timeout=120000);rows=panel().locator('.workspace-find-result');expect(rows).to_have_count(len(names),timeout=20000);assert sorted(rows.evaluate_all('els=>els.map(e=>e.dataset.findKey)'))==sorted('object:'+ns+n for n in names)
def definition(id):
 row=f.call('finderContent',{'ids':[id]})['rows'][0];assert row['status']=='available';return json.loads(next(v['valueJson']for v in row['fields']if v['name']=='정의'))
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser)
  try:
   page.locator('#chat-input').fill('모듈 찾기 중 보존할 개인 입력');selected=(f.state().get('draft')or{}).get('id');open_find()
   if mode=='baseline':
    assert'DirectModuleActionNeedle'not in definition(x.owner);search('DirectModuleActionNeedle',['DirectModuleActionNeedle']);search('같은 인터페이스',['InterfaceBox','EmptyBox']);panel().locator('[data-find-key="object:'+x.owner+'"]').click();expect(page.locator('[data-module-interface]')).to_contain_text('DirectModuleActionNeedle',timeout=60000);f.checked('published engine misses the direct requirement name although the same module opens with that required function in the existing interface editor')
   else:
    assert definition(x.owner)==['DirectModuleActionNeedle'];assert definition(ns+'EmptyBox')==[];assert definition(x.parent)==['InheritedModuleActionNeedle'];assert(f.state().get('draft')or{}).get('id')==selected
    for args in [{'ids':[]},{'ids':[x.owner]*2},{'ids':[x.owner]*65},{'ids':['Confectory.FrameControl::Open']},{'ids':[x.owner],'path':'/tmp/not-owned'}]:f.call('finderContent',args,False)
    search('DirectModuleActionNeedle',['DirectModuleActionNeedle','InterfaceBox']);search('InheritedModuleActionNeedle',['InheritedModuleActionNeedle','BaseRules']);search('ParentSecretMustNotJoin',['BaseRules']);search('UnregisteredSourceMustNeverBeRead',[]);expect(page.locator('#chat-input')).to_have_value('모듈 찾기 중 보존할 개인 입력');assert(f.state().get('draft')or{}).get('id')==selected;f.checked('direct requirement labels use the existing owned definition projection; includes/parent contents are not joined, empty/foreign/extra-path requests retain existing guards and private input/selection')
    if mode=='normal':
     original=(f.projects[0].parent/'InterfaceBox.celem').read_text();f.call('select',{'id':x.owner});f.call('editDraft',{'id':x.owner,'revision':f.state()['draft']['revision'],'text':original.replace('require '+ns+'DirectModuleActionNeedle','require '+ns+'ChangedModuleActionNeedle')});f.call('select',{'id':ns+'Tick'});search('ChangedModuleActionNeedle',['ChangedModuleActionNeedle','InterfaceBox']);search('DirectModuleActionNeedle',['DirectModuleActionNeedle']);h=f.call('draftHistory',{'action':'inspect'});f.call('draftHistory',{'action':'undo','token':h['undo']['token']});search('DirectModuleActionNeedle',['DirectModuleActionNeedle','InterfaceBox']);h=f.call('draftHistory',{'action':'inspect'});f.call('draftHistory',{'action':'redo','token':h['redo']['token']});search('ChangedModuleActionNeedle',['ChangedModuleActionNeedle','InterfaceBox']);panel().locator('[data-find-key="object:'+x.owner+'"]').click();expect(panel()).to_have_count(0);expect(page.locator('[data-declaration-id]')).to_have_text(x.owner,timeout=60000);f.checked('off-page shared draft changes and Undo/Redo refresh the open index; selecting the match opens exactly the existing owned module interface, preserving physical sources')
    elif mode=='lifecycle':
     search('ModuleQueryMustNotPersist',[]);page.evaluate('()=>globalThis.confectoryFlushPresentation()');assert'ModuleQueryMustNotPersist'not in json.dumps(f.state()['presentation']);page.close();f.stop();f.start(1);page=f.setup(browser);expect(panel()).to_have_count(0);open_find();expect(panel().get_by_role('searchbox')).to_have_value('');search('DirectModuleActionNeedle',['DirectModuleActionNeedle','InterfaceBox']);panel().get_by_role('searchbox').press('Escape');f.call('leaveProject',{});expect(page.locator('.home-grid')).to_be_visible();page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(2);page=f.setup(browser);open_find();search('DirectModuleActionNeedle',['DirectModuleActionNeedle']);search('OtherProjectModuleAction',['OtherProjectModuleAction','InterfaceBox']);f.checked('cold/home/new project never replays a query or adopts requirements from identical module IDs')
    else:raise AssertionError(mode)
   f.original();assert not f.errors and not f.external,(f.errors,f.external);assert not {'editDraft','saveDraft','reviewDraft','confirmDraft','runProject','nodeTask','startAI'}.intersection(v.get('endpoint')for v in f.requests);page.screenshot(path=str(f.root/('finder-modules-'+mode+'.png')));page.close();browser.close()
  except Exception:
   try:page.screenshot(path=str(f.root/'failure.png'));(f.root/'failure.html').write_text(page.content())
   except Exception:pass
   raise
except Exception as e:(f.root/'failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:f.save_evidence();f.stop()
print('FINDER_MODULE_FIXTURE',f.root,flush=True)
