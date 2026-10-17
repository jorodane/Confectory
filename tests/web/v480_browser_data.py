"""The actual browser Data borrows versioned InstantTable cells; no source-write shortcut."""
import json,uuid
from playwright.sync_api import expect

def verify_browser_data(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1700,'height':1100});prefix='Example.ButtonGame::';score=prefix+'Score';twin=prefix+'TableTwin';amount='data:["amount"]';tags='data:["tags"]';meta='value:"description"';fields=['description',meta,'initial',amount,tags]
 reference=project.parent/'browser-reference'/'External.celem';reference_bytes=reference.read_bytes()
 originals={name:(project/name).read_bytes() for name in ['Score.celem','TableTwin.celem','TableStats.celem','project.cpack']}
 def state():
  view=mount();result=view['state'];assert send(envelope(view,'dispose'))['ok'];return result
 def invoke(endpoint,args,ok=True):
  view=mount();request='browser-data-'+uuid.uuid4().hex;accepted=send(envelope(view,'invoke',endpoint=endpoint,requestId=request,expectedRevision=view['revision'],input=args));assert accepted['ok'],accepted;result,_=settle(view,request);assert result['ok']==ok,result;assert send(envelope(view,'dispose'))['ok'];return result
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=60000)
 w=page.locator('.window[data-key="browser"]');builder=page.locator('.window[data-key="custom"]')
 def cell(id,field):return w.locator('[data-table-cell="'+id+'"][data-column=\''+field+'\']')
 def action(id,field,kind='apply'):return w.locator('[data-table-'+kind+'="'+id+'"][data-column=\''+field+'\']')
 def record():return state()['tables'][0]
 def row(id):return next(r for r in record()['snapshot']['rows'] if r['id']==id)
 def configure(ids,columns,commit=True):
  w.locator('[data-browser-fields]').click();expect(builder.locator('[data-table-object]')).to_have_count(3,timeout=60000);ready()
  builder.locator('[data-table-probe]').select_option(score);ready()
  for check in builder.locator('[data-table-object]').all():check.uncheck()
  for id in ids:builder.locator('[data-table-object="'+id+'"]').check()
  for check in builder.locator('[data-table-field]').all():check.uncheck()
  for field in columns:builder.locator('[data-table-field=\''+field+'\']').check()
  if commit:builder.locator('[data-table-create]').click();ready();expect(w.locator('[data-table-cell]')).not_to_have_count(0,timeout=60000)
  builder.locator('[data-close]').click();ready()
 def density(value):w.locator('input[type=range][aria-label="객체 표시 밀도 Compact Preview Data"]').evaluate('(e,n)=>{e.value=String(n);e.dispatchEvent(new Event("input",{bubbles:true}));}',value)
 ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='개념',exact=True).click();ready();page.locator('#nav').click()
 density(100);expect(w.locator('[data-browser-fields]')).to_be_visible();expect(w.locator('thead th')).to_have_count(3)
 configure([score,twin],fields);expect(cell(score,amount)).to_have_value('9223372036854775807');expect(cell(twin,amount)).to_have_value('9223372036854775806');expect(cell(score,meta)).to_have_value('Separate metadata');expect(w.locator('thead th')).to_have_count(9)
 first=record();invoke('configureTable',{**{k:first[k] for k in ['table','ids','columns','request']},'definitionHash':'0'*64},False);assert record()['definitionHash']==first['definitionHash']
 # Cancelling configuration has no effect on the actual selected columns/rows.
 configure([twin],[amount],False);assert set(record()['ids'])=={score,twin} and record()['columns']==fields
 cell(score,amount).fill('5');cell(score,tags).fill('[1,"wrong"]');before=row(score);action(score,tags).click();ready();expect(cell(score,tags)).to_have_value('[1,"wrong"]');assert row(score)==before
 # Same document preserves its live input; navigating and changing density retains private values.
 cell(score,amount).evaluate('e=>globalThis.browserDataInput=e');page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='개념',exact=True).click();assert cell(score,amount).evaluate('e=>e===globalThis.browserDataInput');page.locator('#nav').click()
 w.locator('[data-close]').click();expect(w).to_be_hidden();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='개념',exact=True).click();ready();page.locator('#nav').click();expect(cell(score,amount)).to_have_value('5')
 density(50);expect(w.locator('[data-table-cell]')).to_have_count(0);density(100);expect(cell(score,amount)).to_have_value('5')
 query=w.locator('[data-browser-control="object-query"]');query.fill('NoSuchObject');w.locator('[data-browser-control="object-search"]').click();ready();expect(w.locator('[data-object]')).to_have_count(0);expect(w.locator('[data-browser-fields]')).to_be_visible();expect(w.locator('[data-browser-pending]')).to_contain_text('2개 미적용');query.fill('TableTwin');w.locator('[data-browser-control="object-search"]').click();ready();expect(cell(score,amount)).to_have_count(0);expect(cell(twin,amount)).to_be_visible();query.fill('');w.locator('[data-browser-control="object-search"]').click();ready();expect(cell(score,amount)).to_have_value('5');expect(cell(score,tags)).to_have_value('[1,"wrong"]')
 # Editing controls never select a different source. Ordinary row selection does.
 selected=state()['draft']['id'];cell(twin,amount).fill('12');cell(twin,amount).press('Home');cell(twin,amount).press('Delete');cell(twin,amount).press('Enter');expect(cell(twin,amount)).to_have_value('2');assert state()['draft']['id']==selected;expect(page.locator('.context-menu')).to_have_count(0);action(twin,amount,'cancel').click()
 w.locator('[data-object="'+twin+'"] td').nth(1).click();expect(page.locator('.window[data-key="schema"] [data-schema-field="initial"]')).to_be_visible(timeout=60000);ready();expect(cell(score,amount)).to_have_value('5');page.locator('.window[data-key="schema"] [data-close]').click()
 # A new comparison definition may hide inputs, but may not drop or rebase them.
 configure([twin],[amount]);expect(cell(score,amount)).to_have_count(0);expect(w.locator('[data-browser-pending]')).to_contain_text('2개 미적용')
 w.locator('[data-browser-fields-review]').click();expect(page.locator('#status')).to_contain_text('미적용');assert state()['review'] is None
 configure([score,twin],fields);expect(cell(score,amount)).to_have_value('5');expect(cell(score,tags)).to_have_value('[1,"wrong"]');action(score,tags,'cancel').click();expect(cell(score,tags)).to_have_value('[1,2]');action(score,amount,'cancel').click();expect(cell(score,amount)).to_have_value('9223372036854775807')
 # Both source and resolved schema version changes refuse stale pending edits.
 cell(score,amount).fill('5');invoke('select',{'id':score});invoke('inspectDeclaration',{'id':score});d=state()['declaration'];invoke('editDeclaration',{'id':score,'revision':d['revision'],'hash':d['textHash'],'edit':{'action':'properties','values':{'displayName':'Browser score'}}})
 w.locator('[data-browser-fields-refresh]').click();ready();expect(cell(score,amount)).to_have_value('5');expect(cell(score,amount).locator('..').locator('[data-table-origin]')).to_contain_text('원본 또는 스키마');action(score,amount).click();ready();expect(cell(score,amount)).to_have_value('5');assert row(score)['cellInfo'][amount]['valueJson']=='9223372036854775807';action(score,amount,'cancel').click()
 cell(score,amount).fill('6');invoke('select',{'id':prefix+'TableStats'});d=state()['draft'];schema_text=d['text'];invoke('editDraft',{'id':d['id'],'revision':d['revision'],'text':schema_text[:-1]+'field bonus single general long;}'})
 w.locator('[data-browser-fields-refresh]').click();ready();action(score,amount).click();ready();expect(cell(score,amount)).to_have_value('6');assert row(score)['cellInfo'][amount]['valueJson']=='9223372036854775807';action(score,amount,'cancel').click();d=state()['draft'];invoke('editDraft',{'id':prefix+'TableStats','revision':d['revision'],'text':schema_text});w.locator('[data-browser-fields-refresh]').click();ready()
 cell(score,amount).fill('9223372036854775805');action(score,amount).click();ready();assert row(score)['cellInfo'][amount]['valueJson']=='9223372036854775805'
 # Registry entries stay read-only and never acquire table field controls.
 cell(score,tags).fill('[8,9]');invoke('localInventory',{});expect(w.locator('[data-namespace="BrowserReference"]')).to_be_visible(timeout=60000);w.locator('[data-namespace="BrowserReference"]').click();expect(w.locator('[data-object="BrowserReference::External"]')).to_be_visible();expect(w.locator('[data-table-cell]')).to_have_count(0);expect(w.locator('[data-browser-field-readonly]')).to_have_count(5);expect(w.locator('[data-browser-field-readonly]').first).to_contain_text('읽기 전용')
 current=record();invoke('configureTable',{**{k:current[k] for k in ['table','ids','columns','request']},'ids':['BrowserReference::External'],'definitionHash':current['definitionHash']},False);assert set(record()['ids'])=={score,twin}
 w.locator('[data-catalog-root]').click();ready();expect(cell(score,tags)).to_have_value('[8,9]');w.locator('[data-browser-fields-release]').click();ready();expect(cell(score,tags)).to_have_value('[8,9]');assert len(state()['tables'])==1
 # Repeated header controls keep pending inputs and current DOM in other cells.
 heading=w.locator('th[data-table-column=\''+amount+'\']');heading.locator('summary').click();heading.locator('[data-table-width]').evaluate("e=>{e.value='280';e.dispatchEvent(new Event('input',{bubbles:true}));}");heading.locator('[data-direction="-1"]').click();heading.locator('[data-direction="-1"]').click();expect(cell(score,tags)).to_have_value('[8,9]');expected_order=['description',amount,meta,'initial',tags];assert w.locator('thead [data-table-column]').evaluate_all('es=>es.map(e=>e.dataset.tableColumn)')==expected_order
 w.locator('[data-browser-fields-save]').click();ready();query=w.locator('[data-browser-control="object-query"]');query.fill('query draft');handle=w.locator('[data-resize="se"]').bounding_box();page.mouse.move(handle['x']+handle['width']/2,handle['y']+handle['height']/2);page.mouse.down();page.mouse.move(1620,810,steps=12);page.mouse.up();w.locator('[data-browser-data-scroll]').evaluate('e=>{e.scrollLeft=0;e.scrollTop=0;}');expect(cell(score,tags)).to_have_value('[8,9]');page.evaluate('()=>globalThis.confectoryFlushPresentation()');page.screenshot(path='/tmp/confectory-v480-browser-data.png',full_page=True)
 for name,original in originals.items():assert (project/name).read_bytes()==original,name
 restart();w=page.locator('.window[data-key="browser"]');ready();expect(cell(score,tags)).to_have_value('[8,9]',timeout=60000);expect(cell(score,amount)).to_have_value('9223372036854775805');expect(w.locator('[data-browser-control="object-query"]')).to_have_value('query draft');assert w.locator('thead [data-table-column]').evaluate_all('es=>es.map(e=>e.dataset.tableColumn)')==expected_order;assert w.locator('th[data-table-column=\''+amount+'\']').evaluate('e=>e.style.width')=='280px';action(score,tags,'cancel').click();expect(cell(score,tags)).to_have_value('[1,2]')
 for name,original in originals.items():assert (project/name).read_bytes()==original,name
 # Browser Review still invokes the ordinary compiler and explicit Confirm.
 w.locator('[data-browser-fields-review]').click();expect(page.locator('#confirm')).to_be_enabled(timeout=120000);change=page.locator('[data-review-unit="'+score+'"] [data-semantic-change]').filter(has_text='amount');expect(change.locator('[data-semantic-before]')).to_have_text('9223372036854775807');expect(change.locator('[data-semantic-after]')).to_have_text('9223372036854775805');page.locator('#confirm').click();ready();expect(page.locator('#status')).to_contain_text('Source confirmed',timeout=120000);assert '9223372036854775805' in (project/'Score.celem').read_text();assert (project/'TableStats.celem').read_bytes()==originals['TableStats.celem'] and (project/'project.cpack').read_bytes()==originals['project.cpack']
 w.locator('[data-browser-fields-release]').click();ready();expect(w.locator('thead th')).to_have_count(3);assert state()['tables']==[];assert reference.read_bytes()==reference_bytes;expect(w.locator('[data-browser-fields]')).to_be_visible()
 print('PASS actual v480 browser Data fields: shared versioned cells/exact int64/typed refusal/cancel/selection/reconfigure/readonly/source+schema CAS/cold/Save/compiler Confirm',flush=True)
