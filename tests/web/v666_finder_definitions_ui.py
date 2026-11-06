"""Native definition projection and authored search; no source/contract writes."""
import json,sys,time,traceback
from playwright.sync_api import sync_playwright,expect
import v666_finder_definitions_fixture as definitions
f=definitions.f;ns=definitions.ns;mode=sys.argv[3];page=None
panel=lambda:page.locator('#workspace-find-panel')
def open_find():
 page.locator('#worker-finder-bubble').click();expect(panel()).to_be_visible();panel().locator('[data-find-mode="text"]').click()
def search(query,ids):
 field=panel().get_by_role('searchbox');field.fill(query);expect(panel().locator('[data-find-content-refresh]')).to_be_visible(timeout=120000);expect(panel().locator('.workspace-find-status')).not_to_contain_text('확인하고 있어요',timeout=120000);rows=panel().locator('.workspace-find-result');expect(rows).to_have_count(len(ids));assert sorted(rows.evaluate_all('els=>els.map(e=>e.dataset.findKey)'))==sorted('object:'+ns+id for id in ids);return field
try:
 f.start(0)
 with sync_playwright()as p:
  expect.set_options(timeout=60000);browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=f.setup(browser)
  try:
   page.get_by_role('tab',name='Workspace',exact=True).click();page.locator('#chat-input').fill('정의 검색 중 보존할 개인 입력');selected=f.states[-1].get('draft',{}).get('id')
   if mode=='baseline':
    open_find();panel().get_by_role('searchbox').fill('EnumDefinitionNeedle');expect(panel().locator('[data-find-content-refresh]')).to_be_visible(timeout=120000);expect(panel().locator('.workspace-find-result')).to_have_count(0);f.call('browserElements',{'ids':[ns+'Choice']},False);f.checked('baseline misses unplaced definition/member names and the existing generic Data API intentionally rejects enum')
   else:
    response=f.call('finderContent',{'ids':[ns+'UnusedInfo',ns+'Signature',ns+'Choice']});assert response['projectId']==f.states[-1]['projectId'];rows={row['id']:row for row in response['rows']};assert all(row['status']=='available'for row in rows.values());values={id:json.loads(next(field['valueJson']for field in row['fields']if field['name']=='정의'))for id,row in rows.items()};assert all(term in values[ns+'UnusedInfo']for term in ['UnplacedDefinitionNeedle','ExactDefinitionType','long']);assert all(term in values[ns+'Signature']for term in ['InputDefinitionNeedle','int','string']);assert values[ns+'Choice']==['EnumDefinitionNeedle 😀','완료 항목'];assert not any(key in json.dumps(values)for key in ['Origin','Loc','Path','editorEnumValues','data:image']);assert f.states[-1].get('draft',{}).get('id')==selected
    for args in [{'ids':[]},{'ids':[ns+'Choice']*2},{'ids':[ns+'Choice']*65},{'ids':['Confectory.FrameControl::Open']},{'ids':[ns+'NotRegistered']},{'ids':[ns+'Choice'],'path':'/tmp/not-owned'}]:f.call('finderContent',args,False)
    unavailable=f.call('finderContent',{'ids':[ns+'Choice',ns+'InvalidChoice']})['rows'];assert unavailable[0]['status']=='available'and unavailable[1]['status']=='unavailable'and unavailable[1]['code']=='finder-content-unavailable'and'fields'not in unavailable[1]
    f.call('browserElements',{'ids':[ns+'Choice']},False);f.call('editBrowserElement',{'id':ns+'Choice','column':'description','valueJson':'"forbidden"','version':{key:rows[ns+'Choice'][key]for key in ['revision','textHash','viewHash']}},False);f.checked('native owned read projects structure/member names without locations/bodies/icons; bounded/foreign/unknown/extra-field rejection and generic enum edit rejection remain intact')
    open_find();search('UnplacedDefinitionNeedle',['UnusedInfo']);search('InputDefinitionNeedle',['Signature']);search('EnumDefinitionNeedle',['Choice']);search('EnumDescriptionNeedle',['Choice']);expect(panel().locator('.workspace-find-status')).to_contain_text('미지원/확인 불가');expect(page.locator('#chat-input')).to_have_value('정의 검색 중 보존할 개인 입력');assert f.states[-1].get('draft',{}).get('id')==selected;f.checked('unplaced information field, function parameter, enum member/description search uses exact owners while preserving selection and private input')
    if mode=='normal':
     search('EnumDefinitionNeedle',['Choice']);panel().locator('.workspace-find-result').click();expect(panel()).to_have_count(0);end=time.monotonic()+20
     while time.monotonic()<end:
      if f.states[-1].get('draft',{}).get('id')==ns+'Choice':break
      page.wait_for_timeout(50)
     else:raise AssertionError('exact enum owner did not open')
     f.checked('member match opens its existing owned enum definition, preserving opaque member IDs and the execution contract')
    elif mode=='lifecycle':
     search('DefinitionQueryMustNotPersist',[]);page.evaluate('()=>globalThis.confectoryFlushPresentation()');assert 'DefinitionQueryMustNotPersist'not in json.dumps(f.state()['presentation']);page.close();f.stop();f.start(1);page=f.setup(browser);expect(panel()).to_have_count(0);open_find();expect(panel().get_by_role('searchbox')).to_have_value('');search('EnumDefinitionNeedle',['Choice']);panel().get_by_role('searchbox').press('Escape');f.call('leaveProject',{});expect(page.locator('.home-grid')).to_be_visible();page.close();f.stop();f.env['CONFECTORY_WEB_PROJECT']=str(f.projects[1]);f.start(2);page=f.setup(browser);open_find();search('EnumDefinitionNeedle',[]);search('OtherProjectEnumOnly',['Choice']);f.checked('cold/new project with identical owner/member IDs never replays the old query or adopts prior member content')
    else:raise AssertionError(mode)
   f.original();assert not f.errors and not f.external,(f.errors,f.external);assert not {'editDraft','editField','editMetadata','editDeclaration','saveDraft','reviewDraft','confirmDraft','runProject','startAI','nodeTask'}.intersection(row.get('endpoint')for row in f.requests);page.screenshot(path=str(f.root/('finder-definitions-'+mode+'.png')));page.close();browser.close()
  except Exception:
   try:page.screenshot(path=str(f.root/'failure.png'));(f.root/'failure.html').write_text(page.content())
   except Exception:pass
   raise
except Exception as error:(f.root/'failure.json').write_text(json.dumps(dict(error=repr(error),traceback=traceback.format_exc()),ensure_ascii=False));raise
finally:f.save_evidence();f.stop()
print('FINDER_DEFINITIONS_FIXTURE',f.root,flush=True)
