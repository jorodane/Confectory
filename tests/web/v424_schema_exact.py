"""General schema scalar editors preserve exact JSON and displayed source hashes."""
import uuid
from playwright.sync_api import expect

def verify_schema_exact(page,project,mount,send,envelope,settle,restart):
 prefix='Example.ButtonGame::';score=prefix+'Score';twin=prefix+'TableTwin'
 originals={name:(project/name).read_bytes() for name in ['Score.celem','TableTwin.celem','TableStats.celem','ZBroken.celem','project.cpack']}
 def state():
  v=mount();result=v['state'];assert send(envelope(v,'dispose'))['ok'];return result
 def invoke(endpoint,args,ok=True):
  v=mount();request='schema-exact-'+uuid.uuid4().hex;reply=send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args));assert reply['ok'],reply;result,_=settle(v,request);assert result['ok']==ok,result;assert send(envelope(v,'dispose'))['ok'];return result
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=60000)
 def browser():
  page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='개념',exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def select(id):
  browser();page.locator('.window[data-key="browser"] [data-id="'+id+'"]').first.click();expect(page.locator('.window[data-key="schema"] [data-schema-id]')).to_have_text(id,timeout=60000);ready()
 def input(field,slot='schema'):return page.locator('.window[data-key="'+slot+'"] [data-schema-field="'+field+'"]')
 def apply(field,value):
  control=input(field);control.fill(value);control.locator('..').get_by_role('button',name='Apply field',exact=True).click();ready()
 def exact(field):return next(row for row in state()['schema']['rows'] if row['name']==field)['valueJson']
 select(score);expect(input('amount')).to_have_value('9223372036854775807');expect(input('huge')).to_have_value('9223372036854775807');expect(input('tags[0]')).to_have_value('9223372036854775807')
 apply('amount','9223372036854775806');assert exact('amount')=='9223372036854775806'
 apply('huge','9223372036854775806');assert next(row for row in state()['schema']['metadata'] if row['name']=='huge')['valueJson']=='9223372036854775806'
 apply('tags[0]','9223372036854775805');assert exact('tags[0]')=='9223372036854775805' and exact('tags[1]')=='9223372036854775806'
 shown=state()['schema'];before=state()['draft']['text'];invoke('editField',{'id':score,'path':['amount'],'valueJson':'4','revision':shown['revision'],'hash':'0'*64},False);assert state()['draft']['text']==before
 invoke('editField',{'id':score,'path':['amount'],'valueJson':'4','revision':shown['revision']},False);assert state()['draft']['text']==before
 # Previous callers still use their existing JSON-value/revision path.
 invoke('editMetadata',{'id':score,'field':'legacyProbe','value':5,'revision':shown['revision']});select(score);assert state()['schema']['values']['legacyProbe']==5
 # A sibling edit cannot silently rebase the pending scalar input.
 input('amount').fill('5');shown=state()['schema'];invoke('editMetadata',{'id':score,'field':'externalEdit','value':7,'revision':shown['revision']})
 input('amount').locator('..').get_by_role('button',name='Apply field',exact=True).click();ready();expect(input('amount')).to_have_value('5');assert 'data amount = 9223372036854775806' in state()['draft']['text']
 input('amount').locator('..').get_by_role('button',name='현재 값으로 되돌리기',exact=True).click();select(score)
 page.locator('.window[data-key="schema"] #semantic-save').click();ready();input('amount').fill('9223372036854775804');page.evaluate('()=>globalThis.confectoryFlushPresentation()')
 for name,original in originals.items():assert (project/name).read_bytes()==original,name
 restart();expect(input('amount')).to_have_value('9223372036854775804',timeout=60000);ready();input('amount').locator('..').get_by_role('button',name='Apply field',exact=True).click();ready();expect(input('amount')).to_have_value('9223372036854775804');page.locator('.window[data-key="schema"] [data-schema-refresh]').click();ready();expect(input('amount')).to_have_value('9223372036854775804');assert exact('amount')=='9223372036854775806'
 input('amount').locator('..').get_by_role('button',name='현재 값으로 되돌리기',exact=True).click();select(score);apply('amount','9223372036854775805');assert exact('amount')=='9223372036854775805'
 # Exact inherited metadata is displayed; an independent View still owns Score
 # while the primary View selects another object.
 invoke('openEditorView',{'view':'1','id':score,'viewMode':'properties'});select(twin);expect(input('huge')).to_have_value('9223372036854775806');metadata=next(row for row in state()['schema']['metadata'] if row['name']=='huge');assert metadata['origin']==score and metadata['localOverride'] is False
 detached=next(row for row in state()['editorViews'] if row['view']=='1')['schema'];invoke('editViewField',{'view':'1','id':score,'path':['amount'],'valueJson':'9223372036854775804','revision':detached['revision'],'hash':detached['textHash']});assert state()['draft']['id']==twin;expect(input('amount','editor-1')).to_have_value('9223372036854775804',timeout=60000)
 select(score);expect(input('amount')).to_have_value('9223372036854775804');page.locator('.window[data-key="schema"] #semantic-review').click();expect(page.locator('#confirm')).to_be_enabled(timeout=120000);delta=page.locator('[data-review-unit="'+score+'"] [data-semantic-change]').filter(has_text='amount');expect(delta.locator('[data-semantic-before]')).to_have_text('9223372036854775807');expect(delta.locator('[data-semantic-after]')).to_have_text('9223372036854775804');page.locator('#confirm').click();ready();assert state()['review'] is None,state()['logs'][-3:]
 assert '9223372036854775804' in (project/'Score.celem').read_text()
 for name in ['TableTwin.celem','TableStats.celem','ZBroken.celem','project.cpack']:assert (project/name).read_bytes()==originals[name],name
 print('PASS exact schema scalar/metadata/array child/inherited values/hash conflict/legacy caller/pending cold input/independent View/compiler Confirm',flush=True)
