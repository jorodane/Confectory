"""Real declaration creation through the ordinary web consumer and compiler-backed publication."""
from pathlib import Path
import uuid
from playwright.sync_api import expect

def verify_declaration_kinds(page,project,mount,send,envelope,settle,browser,browser_action,restart):
 page.set_viewport_size({'width':1440,'height':1000})
 prefix='Example.ButtonGame::';created=[];initial=(project/'Score.celem').read_bytes()
 choices=[('object','개념 생성','V424Object'),('schema','스키마 생성','V424Schema'),('category','카테고리 생성','V424Category'),('concept','개념 선언 생성','V424Concept'),('function','기능 생성','V424Function'),('module','모듈 생성','V424Module')]
 for kind,label,name in choices:
  browser();page.locator('[data-new]').click();page.get_by_role('button',name=label,exact=True).click();page.locator('#new-declaration-name').fill(name);page.locator('#new-declaration').click();expect(page.locator('#selection')).to_have_text(prefix+name)
  before=mount();assert before['state']['draft']['kind']==kind;assert before['state']['draft']['id']==prefix+name;assert before['state']['draft']['creationReviewIds']==[prefix+name,prefix+'ProjectManifest'];assert send(envelope(before,'dispose'))['ok']
  destination=project/'elements'/(name+'.celem');assert not destination.exists();browser();browser_action('#advanced-source');expect(page.locator('#source')).to_be_visible()
  assert page.locator('#source').input_value().startswith(kind+' '+prefix+name)
  page.locator('#save').click();expect(page.locator('#status')).to_have_text('Draft saved; final sources unchanged');assert not destination.exists();page.locator('#review').click();expect(page.locator('#review-creation')).to_be_visible();page.locator('#review-creation').click();expect(page.locator('#confirm')).to_be_enabled()
  reviewed=mount();review=reviewed['state']['review'];assert {unit['id'] for unit in review['units']}=={prefix+name,prefix+'ProjectManifest'};token=review['token'];assert token;assert send(envelope(reviewed,'dispose'))['ok'];assert not destination.exists()
  page.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000);assert destination.read_text().startswith(kind+' '+prefix+name);assert 'element '+name+' '+kind+' ' in (project/'project.cpack').read_text();created.append(prefix+name)
  review_close=page.locator('.window[data-key="review"] [data-close]')
  if review_close.count():review_close.click()
  for key in ['schema','source']:
   close=page.locator('.window[data-key="'+key+'"]:visible [data-close]')
   if close.count():close.click()
  assert (project/'Score.celem').read_bytes()==initial
 # A forbidden kind and a foreign namespace are rejected without changing source or draft registrations.
 for kind,id in [('implementation',prefix+'Forbidden'),('object','Other.Project::Foreign')]:
  view=mount();before_manifest=(project/'project.cpack').read_bytes();request='v424-denied-'+uuid.uuid4().hex;assert send(envelope(view,'invoke',endpoint='createDeclaration',requestId=request,expectedRevision=view['revision'],input={'kind':kind,'id':id}))['ok'];result,_=settle(view,request);assert not result['ok'];assert (project/'project.cpack').read_bytes()==before_manifest;assert send(envelope(view,'dispose'))['ok']
 restart();browser();browser_action('#advanced-source');expect(page.locator('#status')).to_have_text('고급 소스 탐색',timeout=30000)
 for id in created:
  view=mount();request='v424-restored-'+uuid.uuid4().hex;assert send(envelope(view,'invoke',endpoint='select',requestId=request,expectedRevision=view['revision'],input={'id':id}))['ok'];result,reply=settle(view,request);assert result['ok'],result;assert reply['state']['draft']['id']==id;assert not reply['state']['draft']['dirty'];assert send(envelope(view,'dispose'))['ok']
 assert (project/'Score.celem').read_bytes()==initial
 page.screenshot(path='/tmp/confectory-v424-declaration-kinds.png',full_page=True)
 print('PASS v424 six declaration kinds: actual draft/save/grouped compiler Review/Confirm/restart; no pre-confirm source writes; foreign kind/namespace rejected',flush=True)
