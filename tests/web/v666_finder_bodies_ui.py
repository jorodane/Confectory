"""Body search reads bounded owned drafts and opens one explicit observed target."""
import hashlib,json,sys,time,traceback
from playwright.sync_api import sync_playwright,expect
import v666_finder_bodies_fixture as bodies
f=bodies.f;ns=bodies.ns;owner=ns+'MainBody';mode=sys.argv[3];page=None
panel=lambda:page.locator('#workspace-find-panel')
def open_find():
 page.get_by_role('tab',name='Workspace',exact=True).click();page.locator('#worker-finder-bubble').click();expect(panel()).to_be_visible();panel().locator('[data-find-mode="text"]').click()
def search(text,targets):
 field=panel().get_by_role('searchbox');field.fill(text);expect(panel().locator('[data-find-content-refresh]')).to_be_visible(timeout=120000);expect(panel().locator('.workspace-find-status')).not_to_contain_text('확인하고 있어요',timeout=120000);rows=panel().locator('.workspace-find-result');expect(rows).to_have_count(len(targets),timeout=10000);assert sorted(rows.evaluate_all('els=>els.map(e=>e.dataset.findKey)'))==sorted('body:'+owner+'/body:'+t for t in targets);return field
def content():return f.call('finderContent',{'ids':[owner]})['rows'][0]
def receipt(row):return {key:row[key]for key in ['target','ownerRevision','ownerHash','revision','textHash']}|{'id':owner}
def selected():return (f.state().get('draft')or{}).get('id')
def normal():
 before=selected();data=content();found={b['target']:b for b in data['bodies']};assert set(found)=={'common','linux','preview'}and data['incomplete']is True;assert len(found['preview']['text'])>20000 and'TruncatedTailMustNotIndex'in found['preview']['text'];assert found['linux']['text']=='// BodyLinuxNeedle\r\nreturn 42;\r\n';assert selected()==before and'OutsideBodyMustNeverIndex'not in json.dumps(data)
 for args in [receipt(found['common'])|{'ownerHash':'f'*64},receipt(found['common'])|{'revision':'999999'},receipt(found['common'])|{'target':'missing'},receipt(found['common'])|{'path':str(f.outside)},receipt(found['common'])|{'id':'Confectory.FrameControl::OpenBody'}]:f.call('finderBody',args,False);assert selected()==before
 f.checked('one bounded owned read returns explicit common/linux targets and full bounded text/oversize partial status; stale/foreign/unknown/extra-path opens are rejected before cursor changes')
 f.call('objects',{'kind':'object','query':''});f.call('select',{'id':ns+'Tick'});assert not any(u['kind']=='body'for u in f.state()['units'])
 open_find();search('BodyCommonNeedle',['common']);search('BodyLinuxNeedle',['linux']);search('TruncatedBodyPrefixNeedle',['preview']);search('TruncatedTailMustNotIndex',['preview']);search('OversizeBodyMustNotIndex',[]);search('OutsideBodyMustNeverIndex',[]);expect(panel().locator('.workspace-find-status')).to_contain_text('미지원/확인 불가');f.checked('actual authored finder presents a separate target result, never an implicit default target or outside file')
 original=(f.projects[0].parent/'Main.csbody').read_text();f.call('select',{'id':found['common']['id']});f.call('editDraft',{'id':found['common']['id'],'revision':f.state()['draft']['revision'],'text':original+'\n// BodyDraftChangedNeedle\n'});f.call('select',{'id':ns+'Tick'});mark=selected();f.call('finderBody',receipt(found['common']),False);assert selected()==mark
 search('BodyDraftChangedNeedle',['common']);history=f.call('draftHistory',{'action':'inspect'});assert history['undo']['available'];f.call('draftHistory',{'action':'undo','token':history['undo']['token']});search('BodyDraftChangedNeedle',[]);f.call('finderBody',receipt(found['common']),False);history=f.call('draftHistory',{'action':'inspect'});assert history['redo']['available'];f.call('draftHistory',{'action':'redo','token':history['redo']['token']});search('BodyDraftChangedNeedle',['common']);f.checked('off-page edits, Undo/Redo and same-text ABA update the open index while stale revision receipts remain rejected');panel().locator('.workspace-find-result').click();expect(panel()).to_have_count(0);expect(page.locator('#source')).to_be_visible(timeout=60000);expect(page.locator('#source')).to_have_value(original+'\n// BodyDraftChangedNeedle\n');assert selected()==found['common']['id'];expect(page.locator('#chat-input')).to_have_value('본문 검색 중에도 보존할 개인 입력');f.checked('real body draft revision invalidates the old receipt/index and explicit selection opens exactly that current C# source without Save/Confirm')
 page.locator('#source').fill(original+'\n// UnappliedBodyPrivateInput\n');mark=len(f.requests);open_find();search('BodyLinuxNeedle',['linux']);panel().locator('.workspace-find-result').click();expect(panel()).to_have_count(0);expect(page.locator('#source')).to_have_value(original+'\n// UnappliedBodyPrivateInput\n');assert not any(r.get('endpoint')=='finderBody'for r in f.requests[mark:]);assert selected()==found['common']['id'];f.checked('unapplied source input is never silently applied, replaced or navigated away by another body match')
def guards():
 data=content();body=next(b for b in data['bodies']if b['target']=='common');linux=next(b for b in data['bodies']if b['target']=='linux');f.call('finderBody',receipt(linux));file=f.projects[0].parent/'LinuxSearch.csbody';raw=file.read_bytes();baseline=f.call('inspectSourceConflict',{'id':linux['id']});assert baseline['status']=='current'and baseline['baselineHash']==hashlib.sha256(raw).hexdigest()and baseline['baseText']==linux['text']
 try:
  file.write_bytes(raw+b'// ExternalBodyChange\r\n');conflict=f.call('inspectSourceConflict',{'id':linux['id']});assert conflict['status']=='conflict'and conflict['baselineHash']==baseline['baselineHash']and conflict['draftText']==linux['text']and conflict['fileHash']!=baseline['fileHash']
 finally:file.write_bytes(raw)
 f.checked('bounded UTF-8 BOM/CRLF capture retains exact raw baseline and the existing source conflict guard observes later file changes without changing the draft')
 mark=selected();file=f.projects[0].parent/'Main.csbody';raw=file.read_bytes()
 try:
  file.unlink();file.symlink_to(f.outside);f.call('finderBody',receipt(body),False);assert selected()==mark;result=content();assert result['incomplete']is True and not result['bodies'];assert'OutsideBodyMustNeverIndex'not in json.dumps(result)
 finally:
  file.unlink();file.write_bytes(raw)
 assert f.outside.read_bytes()==f.outside_bytes;result=f.call('finderBody',receipt(body));assert result['accepted']and result['id']==body['id'];f.call('finderBody',receipt(body));assert selected()==body['id'];f.checked('replaced symlink is refused even with a loaded draft/receipt; original bytes restore safely and repeated explicit opens remain source-free')
 # A newly authored locator cannot retarget an already loaded unit implicitly.
 declaration=(f.projects[0].parent/'MainBody.celem').read_text();f.call('select',{'id':owner});f.call('editDraft',{'id':owner,'revision':f.state()['draft']['revision'],'text':declaration.replace('"Main.csbody"','"LinuxSearch.csbody"')});mark=selected();f.call('finderBody',receipt(body),False);assert selected()==mark;new=content();assert new['incomplete']is True and not any(b['target']=='common'for b in new['bodies']);f.checked('changed owner/loaded locator rejects stale opens and never aliases the old code unit to a new file')
def lifecycle(browser):
 global page
 open_find();search('BodyCommonNeedle',['common']);search('BodyQueryMustNotPersist',[]);page.evaluate('()=>globalThis.confectoryFlushPresentation()');assert'BodyQueryMustNotPersist'not in json.dumps(f.state()['presentation']);page.close();f.stop();f.start(1);page=f.setup(browser);expect(panel()).to_have_count(0);expect(page.locator('#chat-input')).to_have_value('본문 검색 중에도 보존할 개인 입력');open_find();expect(panel().get_by_role('searchbox')).to_have_value('');search('BodyCommonNeedle',['common']);panel().get_by_role('searchbox').press('Escape');f.call('leaveProject',{});expect(page.locator('.home-grid')).to_be_visible();page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(2);page=f.setup(browser);open_find();search('BodyCommonNeedle',[]);search('OtherProjectBodyOnly',['common']);f.checked('cold/home/new project preserves private input only in its owner and cannot adopt code/query from identical namespace/body IDs')
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser);page.locator('#chat-input').fill('본문 검색 중에도 보존할 개인 입력')
  try:
   if mode=='baseline':
    open_find();panel().get_by_role('searchbox').fill('BodyCommonNeedle');expect(panel().locator('[data-find-content-refresh]')).to_be_visible(timeout=120000);expect(panel().locator('.workspace-find-result')).to_have_count(0);assert not content().get('bodies');f.checked('published baseline cannot search a declared owned C# body even though the body locator already exists')
   else:{'normal':normal,'guards':guards,'lifecycle':lambda:lifecycle(browser)}[mode]()
   f.original();assert f.outside.read_bytes()==f.outside_bytes;assert not f.errors and not f.external,(f.errors,f.external);assert not {'editDraft','saveDraft','reviewDraft','confirmDraft','editField','runProject','nodeTask','startAI'}.intersection(r.get('endpoint')for r in f.requests);page.screenshot(path=str(f.root/('finder-bodies-'+mode+'.png')));page.close();browser.close()
  except Exception:
   try:page.screenshot(path=str(f.root/'failure.png'));(f.root/'failure.html').write_text(page.content())
   except Exception:pass
   raise
except Exception as error:(f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:f.save_evidence();f.stop()
print('FINDER_BODIES_FIXTURE',f.root,flush=True)
