"""Actual local overrides, whole data values, array order and schema definition edits."""
import json,uuid,time
from playwright.sync_api import expect

def verify_schema_actions(page,project,mount,send,envelope,settle,restart):
 prefix='Example.ButtonGame::';score=prefix+'Score';twin=prefix+'TableTwin';stats=prefix+'TableStats';originals={name:(project/name).read_bytes() for name in ['Score.celem','TableTwin.celem','TableStats.celem','TableLeaf.celem','project.cpack']}
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,args,ok=True):
  v=mount();request='schema-action-'+uuid.uuid4().hex;accepted=send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args));assert accepted['ok'],accepted;result,_=finish(v,request,endpoint=='confirmGroup');assert result['ok']==ok,result;assert send(envelope(v,'dispose'))['ok'];return result
 def finish(v,request,compiler=False):
  if not compiler:return settle(v,request)
  deadline=time.monotonic()+180
  while time.monotonic()<deadline:
   reply=send(envelope(v,'update'));assert reply.get('ok'),reply
   for result in reply.get('results',[]):
    if result['requestId']==request:return result,reply
   time.sleep(.05)
  raise AssertionError('owned compiler confirmation remained pending')
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=60000)
 def select(id):
  page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='개념',exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
  page.locator('.window[data-key="browser"] [data-id="'+id+'"]').first.click();ready()
 def window():return page.locator('.window[data-key="schema"]')
 def field(path,metadata=False):return window().locator('.data-value-field[data-field-path=\''+json.dumps(path,separators=(',',':'))+'\'][data-field-metadata="'+str(metadata).lower()+'"]')
 def control(path,metadata=False):return field(path,metadata).locator('[data-schema-field]').first
 def apply(path,value=None,metadata=False):
  if value is not None:control(path,metadata).fill(value)
  field(path,metadata).get_by_role('button',name='Apply field',exact=True).click();ready()
 def remove(path,metadata=False):field(path,metadata).locator('[data-override-remove]').click();ready()
 select(twin);expect(control(['huge'],True)).to_have_value('9223372036854775807');expect(field(['huge'],True).locator('[data-override-remove]')).to_be_disabled();expect(control(['tags',0])).to_be_disabled()
 # A root inherited value is copied only by an explicit whole-value apply.
 apply(['tags']);expect(control(['tags',0])).to_be_enabled();expect(control(['tags',0])).to_have_value('9223372036854775807');array=field(['tags']);array.locator('[data-array-index]').select_option('1');array.locator('[data-array-move="-1"]').click();ready();expect(control(['tags',0])).to_have_value('9223372036854775806');expect(control(['tags',1])).to_have_value('9223372036854775807');remove(['tags']);expect(control(['tags',0])).to_be_disabled();expect(control(['tags',0])).to_have_value('9223372036854775807')
 apply(['huge'],'4',True);expect(field(['huge'],True).locator('[data-override-remove]')).to_be_enabled();remove(['huge'],True);expect(control(['huge'],True)).to_have_value('9223372036854775807')
 description=window().locator('[data-description]');description.fill('Local child description');window().locator('#semantic-save').click();ready();expect(window().locator('[data-override-description]')).to_be_enabled();window().locator('[data-override-description]').click();ready();expect(window().locator('[data-description]')).to_have_value('Game-owned score; buttons contain no editor/model semantics.');expect(window().locator('[data-override-description]')).to_be_disabled()
 # Whole compound JSON never passes its long value through Number/stringify.
 expect(control(['profile','n'])).to_be_disabled();apply(['profile'],'{"n":9223372036854775805,"flag":false}');expect(control(['profile','n'])).to_have_value('9223372036854775805');expect(control(['profile','flag'])).not_to_be_checked();remove(['profile']);expect(control(['profile','n'])).to_be_disabled();expect(control(['profile','n'])).to_have_value('9223372036854775807')
 # Syntax failure and stale structural commands preserve both input and source.
 before=state()['draft']['text'];control(['tags']).fill('[invalid');field(['tags']).get_by_role('button',name='Apply field',exact=True).click();ready();expect(control(['tags'])).to_have_value('[invalid');assert state()['draft']['text']==before;field(['tags']).get_by_role('button',name='현재 값으로 되돌리기',exact=True).click()
 current=state()['schema'];invoke('editDeclaration',{'id':twin,'revision':current['revision'],'hash':'0'*64,'edit':{'action':'unset-data','path':['amount']}},False);assert state()['draft']['text']==before;window().locator('[data-schema-refresh]').click();ready()
 # Removing an inherited schema definition is disabled. Local ordering/removal
 # uses its exact declaration order, not the alphabetically projected row order.
 window().locator('[data-schema-origin="'+stats+'"]').click();ready();expect(window().locator('[data-schema-id]')).to_have_text(stats);assert state()['schema']['localFieldOrder']==['amount','tags','profile'];window().locator('[data-definition-move="amount"][data-direction="1"]').click();ready();assert state()['schema']['localFieldOrder']==['tags','amount','profile']
 bounds=window().bounding_box()
 for button in window().locator('[data-definition-move]').all():
  box=button.bounding_box();assert box and box['x']>=bounds['x'] and box['x']+box['width']<=bounds['x']+bounds['width']-8,(box,bounds,button.evaluate("e=>{const row=e.closest('.schema-row');return {columns:getComputedStyle(row).gridTemplateColumns,row:row.getBoundingClientRect().toJSON(),actions:e.parentElement.getBoundingClientRect().toJSON()}}"))
 for actions in window().locator('.schema-row:not([hidden]) .schema-row-actions').all():
  layout=actions.evaluate("e=>({width:e.getBoundingClientRect().width,tops:[...e.children].map(b=>b.getBoundingClientRect().top)})");assert layout['width']>=120 and max(layout['tops'])-min(layout['tops'])<2,layout
 window().locator('h2').scroll_into_view_if_needed();page.screenshot(path='/tmp/confectory-v424-schema-fields.png',full_page=True)
 window().locator('[data-add]').click();new=window().locator('[data-definition-row="new"]');new.locator('[data-definition="name"]').fill('temp');new.locator('[data-definition="type"]').fill('bool');new.locator('[data-operation="definition-apply"]').click();ready();expect(window().locator('[data-definition-row="temp"]')).to_have_count(1);window().locator('[data-definition-remove="temp"]').click();ready();expect(window().locator('[data-definition-row="temp"]')).to_have_count(0);assert state()['schema']['localFieldOrder']==['tags','amount','profile']
 for name,original in originals.items():assert (project/name).read_bytes()==original,name
 # The real shared sources are reviewed together; final publication still uses
 # the ordinary compiler and reviewed IDs.
 invoke('reviewGroup',{'ids':[twin,stats],'target':'linux'});review=state()['review'];assert review['status']=='ready';definition=next(unit for unit in review['units'] if unit['id']==stats);assert definition['semantic']['additionalChanges'] or definition['semantic']['changes'],'schema order must remain reviewable'
 invoke('confirmGroup',{'token':review['token'],'ids':[twin,stats]});assert state()['review'] is None,state()['logs'][-3:];schema_source=(project/'TableStats.celem').read_text();assert schema_source.index('field tags')<schema_source.index('field amount')<schema_source.index('field profile');assert 'temp' not in schema_source
 for name in ['Score.celem','TableLeaf.celem','project.cpack']:assert (project/name).read_bytes()==originals[name],name
 print('PASS actual schema local unset/inherited reveal/exact compound JSON/array order/local field order and removal/negative input/ordinary compiler Confirm',flush=True)
