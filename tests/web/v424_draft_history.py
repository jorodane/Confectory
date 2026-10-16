"""Actual shared-draft history through public transport, UI and ordinary compiler Confirm."""
import hashlib,uuid
from playwright.sync_api import expect

def verify_draft_history(page,project,mount,send,envelope,settle,restart):
 id='Example.ButtonGame::Score';path=project/'Score.celem';original=path.read_text();files={p:p.read_bytes() for p in project.glob('*') if p.is_file()}
 def state():
  view=mount();result=view['state'];assert send(envelope(view,'dispose'))['ok'];return result
 def invoke(endpoint,args):
  view=mount();request='history-'+uuid.uuid4().hex;assert send(envelope(view,'invoke',endpoint=endpoint,requestId=request,expectedRevision=view['revision'],input=args))['ok'];out,_=settle(view,request);assert out['ok'],out;assert send(envelope(view,'dispose'))['ok'];return out.get('result')
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=60000)
 def nav(name):
  if not page.locator('.nav-menu').count():page.locator('#nav').click()
  page.locator('.nav-menu').get_by_role('button',name=name,exact=True).click();ready()
 def raw():
  nav('개념')
  if page.locator('.nav-menu').count():page.locator('#nav').click()
  page.locator('#browser-actions').click();page.locator('#advanced-source').click();ready();expect(page.locator('#source')).to_be_visible()
 def panel():return page.locator('.window[data-key="history"]')
 def edit(number):
  current=state()['draft'];invoke('editMetadata',{'id':id,'field':'initial','valueJson':str(number),'revision':current['revision'],'hash':hashlib.sha256(current['text'].encode()).hexdigest()})
 raw();edit(1);text1=state()['draft']['text'];expect(page.locator('#source')).to_have_value(text1);invoke('reviewGroup',{'ids':[id],'target':'linux'});token=state()['review']['token']
 nav('의미 편집 이력');expect(panel().locator('[data-history-move="undo"]')).to_be_enabled();assert state()['review']['token']==token
 panel().locator('[data-close]').click();nav('의미 편집 이력');expect(panel().locator('[data-history-status]')).to_contain_text('되돌리기 1');assert state()['review']['token']==token
 for button in panel().locator('[data-history-move],[data-history-read]').all():
  box=button.bounding_box();dock=page.locator('#dock').bounding_box();assert box and (box['x']+box['width']<=dock['x'] or box['y']+box['height']<=dock['y']),(box,dock)
 edit(2);text2=state()['draft']['text'];expect(page.locator('#source')).to_have_value(text2)
 panel().locator('[data-history-move="undo"]').click();ready();expect(page.locator('#status')).to_contain_text('이력이나 소스가 바뀌었');assert state()['draft']['text']==text2 and path.read_text()==original
 invoke('reviewGroup',{'ids':[id],'target':'linux'});ready_token=state()['review']['token'];panel().locator('[data-history-read]').click();ready();assert state()['review']['token']==ready_token;before=state()['draft']['revision'];panel().locator('[data-history-move="undo"]').click();ready();assert state()['draft']['text']==text1 and state()['draft']['revision']>before and state()['review'] is None
 panel().locator('[data-history-move="redo"]').click();ready();assert state()['draft']['text']==text2
 # Schema and Table inputs are separate user intents, not implicit inverse edits.
 nav('스키마');schema=page.locator('.window[data-key="schema"]');description=schema.locator('[data-description]');baseline_description=description.input_value();description.fill('Pending history description');nav('의미 편집 이력');panel().locator('[data-history-move="undo"]').click();ready();expect(page.locator('#status')).to_contain_text('미적용 입력');expect(description).to_have_value('Pending history description');assert state()['draft']['text']==text2
 nav('스키마');schema.get_by_role('button',name='설명을 현재 값으로 되돌리기',exact=True).click();expect(description).to_have_value(baseline_description)
 nav('즉석 테이블');builder=page.locator('.window[data-key="custom"]');expect(builder.locator('[data-table-field="initial"]')).to_be_visible(timeout=60000);ready()
 for checkbox in builder.locator('[data-table-object]').all():checkbox.set_checked(checkbox.get_attribute('data-table-object')==id)
 for checkbox in builder.locator('[data-table-field]').all():checkbox.set_checked(checkbox.get_attribute('data-table-field')=='initial')
 builder.locator('[data-table-create]').click();table=page.locator('.window[data-key^="table:"]');cell=table.locator('[data-table-cell="'+id+'"][data-column="initial"]');expect(cell).to_have_value('2',timeout=60000);ready();cell.fill('9');nav('의미 편집 이력');panel().locator('[data-history-move="undo"]').click();ready();expect(page.locator('#status')).to_contain_text('미적용 입력');expect(cell).to_have_value('9');assert state()['draft']['text']==text2
 table.locator('.caption').click();table.locator('[data-table-cancel="'+id+'"][data-column="initial"]').click();expect(cell).to_have_value('2')
 # Unsent raw text is never consumed or silently included in a history action.
 raw();text3=text2.replace('initial = 2','initial = 3');page.locator('#source').fill(text3);nav('의미 편집 이력');panel().locator('[data-history-move="undo"]').click();ready();expect(page.locator('#status')).to_contain_text('미적용 입력');expect(page.locator('#source')).to_have_value(text3);assert state()['draft']['text']==text2
 raw();page.locator('#apply').click();ready();assert state()['draft']['text']==text3;nav('의미 편집 이력');panel().locator('[data-history-move="undo"]').click();ready();assert state()['draft']['text']==text2;panel().locator('[data-history-move="redo"]').click();ready();assert state()['draft']['text']==text3
 invoke('saveDraft',{});old=invoke('draftHistory',{'action':'inspect'})['undo']['token'];page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();expect(panel()).to_be_visible(timeout=30000);expect(panel().locator('[data-history-move="undo"]')).to_be_disabled();expect(panel().locator('[data-history-status]')).to_contain_text('다시 읽')
 assert not invoke('draftHistory',{'action':'undo','token':old})['accepted'];nav('의미 편집 이력');expect(panel().locator('[data-history-status]')).to_contain_text('되돌리기 3');panel().locator('[data-history-move="undo"]').click();ready();assert state()['draft']['text']==text2 and path.read_text()==original
 page.screenshot(path='/tmp/confectory-v424-draft-history.png',full_page=True)
 # Confirm remains the actual compiler workflow. Undoing a confirmed edit creates a new draft.
 invoke('reviewGroup',{'ids':[id],'target':'linux'});before_confirm=invoke('draftHistory',{'action':'inspect'})['undo']['token'];nav('변경 검토');review=page.locator('.window[data-key="review"]');advanced=review.locator('[data-review-advanced]')
 if advanced.count():advanced.click()
 ack=review.locator('[data-advanced-reviewed]')
 if ack.count():ack.check()
 expect(review.locator('#confirm')).to_be_enabled();review.locator('#confirm').click();expect(page.locator('#status')).to_have_text('Source confirmed',timeout=180000);ready();assert path.read_text()==text2
 assert not invoke('draftHistory',{'action':'undo','token':before_confirm})['accepted'];assert state()['draft']['text']==text2 and path.read_text()==text2
 nav('의미 편집 이력');panel().locator('[data-history-move="undo"]').click();ready();assert state()['draft']['text']==text1 and path.read_text()==text2 and state()['draft']['dirty'];expect(cell).to_have_value('1')
 for p,content in files.items():
  if p!=path:assert p.read_bytes()==content,p.name
 print('PASS actual draft history: shared owner transactions, stale token refusal, pending input retention, new revisions, Save/cold history, real compiler Confirm and inverse as new unconfirmed draft',flush=True)
