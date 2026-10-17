"""Browser batch fill uses explicit IDs and one existing atomic versioned edit."""
import copy,json,uuid
from playwright.sync_api import expect

def verify_browser_fill(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1700,'height':1100});prefix='Example.ButtonGame::';score=prefix+'Score';twin=prefix+'TableTwin';third=prefix+'TableThird';amount='data:["amount"]';tags='data:["tags"]';fields=[amount,tags,'description']
 original={p:p.read_bytes() for p in project.iterdir() if p.is_file()};reference=project.parent/'browser-reference'/'External.celem';reference_bytes=reference.read_bytes()
 def state():
  view=mount();s=view['state'];assert send(envelope(view,'dispose'))['ok'];return s
 def invoke(endpoint,args):
  view=mount();rid='fill-'+uuid.uuid4().hex;assert send(envelope(view,'invoke',endpoint=endpoint,requestId=rid,expectedRevision=view['revision'],input=args))['ok'];result,_=settle(view,rid);assert result['ok'],result;assert send(envelope(view,'dispose'))['ok'];return result
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=120000)
 def meta():
  page.evaluate('()=>globalThis.confectoryFlushPresentation()');return next(row['meta'] for row in state()['presentation']['layout'] if row['key']=='browser')
 def snapshot():return copy.deepcopy(state()['tables'][0]['snapshot']['rows'])
 def row(id):return next(r for r in snapshot() if r['id']==id)
 w=page.locator('.window[data-key="browser"]');builder=page.locator('.window[data-key="custom"]')
 def cell(id,field):return w.locator('[data-table-cell="'+id+'"][data-column=\''+field+'\']')
 def check(id):return w.locator('[data-table-select="'+id+'"]')
 def fillfield(field):w.locator('[data-table-fill-field]').select_option(field)
 def fill(text):w.locator('[data-table-fill-value]').fill(text)
 def apply():w.locator('[data-table-fill]').click();ready()
 def cancel():w.locator('[data-table-fill-cancel]').click();ready()
 def navigate(name):
  ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name=name,exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def density(n):w.locator('[aria-label="객체 표시 밀도 Compact Preview Data"]').evaluate('(e,n)=>{e.value=String(n);e.dispatchEvent(new Event("input",{bubbles:true}));}',n)
 navigate('개념');density(100)
 w.locator('[data-browser-fields]').click();expect(builder.locator('[data-table-object]')).to_have_count(4,timeout=60000);ready();builder.locator('[data-table-probe]').select_option(score);ready()
 for c in builder.locator('[data-table-object]').all():c.uncheck()
 for id in [score,twin,third]:builder.locator('[data-table-object="'+id+'"]').check()
 for c in builder.locator('[data-table-field]').all():c.uncheck()
 for field in fields:builder.locator('[data-table-field=\''+field+'\']').check()
 builder.locator('[data-table-create]').click();ready();builder.locator('[data-close]').click();handle=w.locator('[data-resize="se"]').bounding_box();page.mouse.move(handle['x']+3,handle['y']+3);page.mouse.down();page.mouse.move(1620,810,steps=12);page.mouse.up();expect(w.locator('[data-table-select]')).to_have_count(3);expect(w.locator('[data-table-count]')).to_contain_text('0개 명시적 선택')
 # The fill value never chooses rows. Exact JSON goes to the two checked sources.
 fillfield(amount);fill('9223372036854775806');before=snapshot();apply();assert snapshot()==before;expect(w.locator('[data-table-fill-value]')).to_have_value('9223372036854775806');check(score).check();check(twin).check();apply();expect(cell(score,amount)).to_have_value('9223372036854775806');expect(cell(twin,amount)).to_have_value('9223372036854775806');expect(cell(third,amount)).to_have_value('9223372036854775804');assert row(third)['dirty'] is False;expect(w.locator('[data-table-fill-value]')).to_have_value('')
 # Invalid later candidates refuse the entire batch, without disturbing a separate cell draft.
 cell(score,'description').fill('Independent pending cell');fillfield(tags);fill('[1,"wrong"]');basis=meta()['tableFill'];before=snapshot();apply();assert snapshot()==before;expect(w.locator('[data-table-fill-value]')).to_have_value('[1,"wrong"]');expect(cell(score,'description')).to_have_value('Independent pending cell');assert meta()['tableFill']==basis
 fillfield(amount);expect(w.locator('[data-table-fill-field]')).to_have_value(tags);assert meta()['tableFill']==basis
 w.locator('[data-browser-fields]').click();expect(builder).to_have_count(0);w.locator('[data-browser-fields-review]').click();expect(page.locator('#status')).to_contain_text('미적용');w.locator('[data-browser-fields-release]').click();ready();assert len(state()['tables'])==1
 # Filtering and explicit selection changes do not expand selection or rebase fill versions.
 query=w.locator('[data-browser-control="object-query"]');query.fill('TableThird');w.locator('[data-browser-control="object-search"]').click();ready();expect(check(third)).not_to_be_checked();expect(w.locator('[data-table-count]')).to_contain_text('현재 목록 밖 2개');assert meta()['tableSelected']==[score,twin] and meta()['tableFill']==basis
 w.locator('[data-table-select-clear]').click();expect(w.locator('[data-table-count]')).to_contain_text('0개 명시적 선택');assert meta()['tableFill']==basis
 query.fill('');w.locator('[data-browser-control="object-search"]').click();ready();check(score).check();check(twin).check();assert meta()['tableFill']==basis;cancel();expect(cell(score,'description')).to_have_value('Independent pending cell');assert meta()['tableSelected']==[score,twin];w.locator('[data-table-cancel="'+score+'"][data-column="description"]').click()
 # Only the second selected source changes; the first must never be partly written.
 fillfield(amount);fill('17');basis=meta()['tableFill'];invoke('select',{'id':twin});invoke('inspectDeclaration',{'id':twin});d=state()['declaration'];invoke('editDeclaration',{'id':twin,'revision':d['revision'],'hash':d['textHash'],'edit':{'action':'properties','values':{'displayName':'External editor changed second row'}}});w.locator('[data-browser-fields-refresh]').click();ready();before=snapshot();apply();assert snapshot()==before and meta()['tableFill']==basis;expect(w.locator('[data-table-fill-value]')).to_have_value('17');assert meta()['tableSelected']==[score,twin];cancel()
 # A resolved schema change fences the whole fill at the original view hash.
 fillfield(amount);fill('19');basis=meta()['tableFill'];invoke('select',{'id':prefix+'TableStats'});d=state()['draft'];schema=d['text'];invoke('editDraft',{'id':d['id'],'revision':d['revision'],'text':schema[:-1]+'field bonus single general long;}' });w.locator('[data-browser-fields-refresh]').click();ready();before=snapshot();apply();assert snapshot()==before and meta()['tableFill']==basis;cancel();d=state()['draft'];invoke('editDraft',{'id':d['id'],'revision':d['revision'],'text':schema});w.locator('[data-browser-fields-refresh]').click();ready()
 # Foreign rows have neither a fill checkbox nor writable cells; no filter implicitly selects them.
 fillfield(amount);fill('21');basis=meta()['tableFill'];invoke('localInventory',{});w.locator('[data-namespace="BrowserReference"]').click();expect(w.locator('[data-object="BrowserReference::External"]')).to_be_visible();expect(w.locator('[data-table-select]')).to_have_count(0);expect(w.locator('[data-table-cell]')).to_have_count(0);expect(w.locator('[data-table-count]')).to_contain_text('현재 목록 밖 2개');assert meta()['tableFill']==basis
 w.locator('[data-table-select-clear]').click();before=snapshot();apply();assert snapshot()==before and meta()['tableFill']==basis;w.locator('[data-catalog-root]').click();ready();expect(check(score)).not_to_be_checked();expect(check(twin)).not_to_be_checked();check(score).check();check(twin).check();cancel()
 # Text is encoded as JSON text; inheritance may change effective projections without writing an unselected source.
 text='Quoted "fill" \\ text';fillfield('description');fill(text);apply();expect(cell(score,'description')).to_have_value(text);expect(cell(twin,'description')).to_have_value(text);assert row(third)['dirty'] is False and row(third)['revision']==0
 w.locator('[data-browser-fields-save]').click();ready();cell(score,tags).fill('[8,9]');fillfield(amount);fill('23');saved=meta();basis=saved['tableFill'];navigate('개념');expect(w.locator('[data-table-fill-value]')).to_have_value('23');w.locator('[data-close]').click();navigate('개념');expect(w.locator('[data-table-fill-value]')).to_have_value('23');density(50);density(100);assert meta()['tableFill']==basis and meta()['tableSelected']==[score,twin]
 page.screenshot(path='/tmp/confectory-v480-browser-fill.png',full_page=True)
 for p,blob in original.items():assert p.read_bytes()==blob,p
 restart();w=page.locator('.window[data-key="browser"]');ready();expect(w.locator('[data-table-fill-value]')).to_have_value('23',timeout=60000);expect(check(score)).to_be_checked();expect(check(twin)).to_be_checked();expect(check(third)).not_to_be_checked();expect(cell(score,tags)).to_have_value('[8,9]');restored=meta();assert restored['tableFill']==basis and restored['tableInputs']==saved['tableInputs']
 # Refusing the cold draft preserves all old bases. Explicit Cancel discards only this fill.
 invoke('select',{'id':twin});invoke('inspectDeclaration',{'id':twin});d=state()['declaration'];invoke('editDeclaration',{'id':twin,'revision':d['revision'],'hash':d['textHash'],'edit':{'action':'properties','values':{'displayName':'Second edit after cold'}}});w.locator('[data-browser-fields-refresh]').click();ready();before=snapshot();apply();assert snapshot()==before and meta()['tableFill']==basis;cancel();expect(cell(score,tags)).to_have_value('[8,9]');w.locator('[data-table-cancel="'+score+'"][data-column=\''+tags+'\']').click();expect(cell(score,tags)).to_have_value('[1,2]')
 fillfield(amount);fill('9223372036854775805');apply();expect(cell(score,amount)).to_have_value('9223372036854775805');expect(cell(twin,amount)).to_have_value('9223372036854775805');expect(cell(third,amount)).to_have_value('9223372036854775804');assert row(third)['dirty'] is False
 for p,blob in original.items():assert p.read_bytes()==blob,p
 w.locator('[data-browser-fields-review]').click();expect(page.locator('#confirm')).to_be_enabled(timeout=120000);expect(page.locator('[data-review-unit="'+score+'"] [data-semantic-change]').filter(has_text='amount').locator('[data-semantic-after]')).to_have_text('9223372036854775805');page.locator('#confirm').click();ready();expect(page.locator('#status')).to_contain_text('Source confirmed',timeout=120000)
 for id in ['Score','TableTwin']:assert '9223372036854775805' in (project/(id+'.celem')).read_text()
 assert (project/'TableThird.celem').read_bytes()==original[project/'TableThird.celem'];assert (project/'TableStats.celem').read_bytes()==original[project/'TableStats.celem'];assert (project/'project.cpack').read_bytes()==original[project/'project.cpack'];assert reference.read_bytes()==reference_bytes
 w.locator('[data-browser-fields-release]').click();ready();assert state()['tables']==[] and meta()['tableSelected']==[]
 print('PASS actual v480 browser atomic fill: explicit IDs/no expansion/exact JSON/atomic type+second-row+schema refusal/original bases/cancel/private cell retention/read-only/cold/Save/compiler Confirm',flush=True)
