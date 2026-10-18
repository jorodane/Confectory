"""Real declared hierarchy to owned/registered definitions, Variation, atomic fill and cold independent contexts."""
import copy,json,uuid
from playwright.sync_api import expect

def verify_declaration_navigation(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':2200,'height':1400});p='Example.ButtonGame::';root=p+'GameRoot';leaf=p+'GameChild';party=p+'Party';score=p+'Score';twin=p+'TableTwin';variant=p+'HierarchyVariant';foreign='BrowserReference::External';amount='data:["amount"]';tags='data:["tags"]'
 originals={f:f.read_bytes() for f in project.iterdir() if f.is_file()};registered=project.parent/'browser-reference'/'External.celem';registered_bytes=registered.read_bytes()
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,args,ok=True):
  v=mount();rid=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=rid,expectedRevision=v['revision'],input=args))['ok'];result,_=settle(v,rid);assert result['ok']==ok,result;assert send(envelope(v,'dispose'))['ok'];return result
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=180000)
 def window(key):return page.locator('.window[data-key="'+key+'"]')
 def nav(name):
  ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name=name,exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def close(key):
  w=window(key)
  if w.count() and w.is_visible():w.locator('[data-close]').click()
 def saved():page.evaluate('()=>globalThis.confectoryFlushPresentation()');return state()['presentation']
 nav('개념');main=window('browser');expect(main.locator('[data-parent="'+root+'"]')).to_be_visible(timeout=180000);ready();main.locator('[data-namespace="Example.ButtonGame"]').click();expect(main.locator('[data-id="'+root+'"]')).to_be_visible();expect(main.locator('[data-id="'+party+'"]')).to_be_visible();expect(main.locator('[data-browser-enter="'+party+'"]')).to_have_count(0)
 main.locator('[data-browser-enter="'+root+'"]').click();expect(main.locator('[data-id="'+leaf+'"]')).to_be_visible();expect(main.locator('[data-id="'+score+'"]')).to_have_count(0);expect(main.locator('[data-ancestor="'+root+'"]')).to_be_visible()
 main.locator('[data-browser-definition="'+leaf+'"]').click();ready();declaration=state()['declaration'];assert declaration['id']==leaf and declaration['kind']=='category';assert any(e['role']=='contain' and e['target']==score for e in declaration['relations']['edges']);close('declaration')
 main.locator('[data-namespace="Example.ButtonGame"]').click()
 main.locator('[data-id="'+party+'"] [data-browser-schema]').click();ready();assert state()['draft']['id']==p+'TableStats';close('schema')
 main.locator('[data-namespace="BrowserReference"]').click();expect(main.locator('[data-new]')).to_be_disabled();main.locator('[data-browser-definition="'+foreign+'"]').click();ready();definition=window('definition');expect(definition.locator('[data-reference-text]')).to_have_attribute('readonly','');assert 'Registered parent definition' in definition.locator('[data-reference-text]').input_value();assert registered.read_bytes()==registered_bytes;close('definition')
 # A stale direct reference source is rejected by the existing gate, never a registry-list authority.
 invoke('relationsMap',{});old=next(n for n in state()['relationsMap']['nodes'] if n['id']==score)
 invoke('readReferenceDefinition',{'sourceId':score,'id':foreign,'revision':old['revision'],'hash':'0'*64},False)
 main.locator('[data-parent="'+foreign+'"]').click();expect(main.locator('[data-id="'+score+'"]')).to_be_visible();main.locator('[data-browser-definition="'+score+'"]').click();ready();expect(window('schema').locator('[data-schema-field="initial"]')).to_have_value('0');close('schema')
 main.locator('[data-id="'+score+'"]').click(button='right');page.get_by_role('button',name='바리에이션 생성',exact=True).click();ready();modal=page.locator('.modal').filter(has=page.locator('[data-variation-parent]'));modal.locator('#new-declaration-name').fill('HierarchyVariant');modal.locator('#new-declaration').click();ready();expect(window('schema').locator('[data-schema-id]')).to_have_text(variant);assert 'extends '+score in state()['draft']['text'];assert not (project/'elements/HierarchyVariant.celem').exists()
 initial=window('schema').locator('[data-schema-field="initial"]');initial.fill('3');initial.locator('..').get_by_role('button',name='Apply field',exact=True).click();ready();window('schema').locator('#semantic-save').click();ready();window('schema').locator('#semantic-review').click();ready();page.locator('#review-creation').click();expect(page.locator('#confirm')).to_be_enabled(timeout=180000)
 review=window('review');review.locator('[data-review-advanced]').click();ack=review.locator('[data-advanced-reviewed]')
 if ack.count():ack.check()
 page.locator('#confirm').click();ready();expect(page.locator('#status')).to_contain_text('Source confirmed',timeout=180000);assert (project/'elements/HierarchyVariant.celem').exists();assert (project/'Score.celem').read_bytes()==originals[project/'Score.celem'];close('schema');close('declaration')
 # Workspace's real parent callbacks create a distinct instance, not the primary browser.
 page.locator('#workspace').click(button='right',position={'x':1800,'y':450});search=page.locator('.workspace-search-menu');search.locator('input').fill(root);search.locator('.workspace-search-entry').filter(has_text='GameRoot').click();other=page.locator('.window[data-key^="browser-tree:"]');expect(other).to_have_count(1);ready();expect(other.locator('[data-id="'+leaf+'"]')).to_be_visible();key=other.get_attribute('data-key');assert key!='browser';assert next(row for row in saved()['layout'] if row['key']==key)['meta']['parent']==root
 box=other.locator('.window-title').bounding_box();page.mouse.move(box['x']+70,box['y']+20);page.mouse.down();page.mouse.move(1090,170,steps=12);page.mouse.up()
 other.locator('[data-tree-query]').fill(score);expect(other.locator('[data-parent="'+score+'"]')).to_be_visible();other.locator('[data-parent="'+score+'"]').click();expect(other.locator('[data-id="'+variant+'"]')).to_be_visible();expect(other.locator('[data-id="'+twin+'"]')).to_be_visible();other.locator('[aria-label="객체 표시 밀도 Compact Preview Data"]').evaluate('e=>{e.value="100";e.dispatchEvent(new Event("input",{bubbles:true}));}')
 other.locator('[data-browser-fields]').click();builder=window('custom');expect(builder.locator('[data-table-object]')).to_have_count(4,timeout=120000);ready();builder.locator('[data-table-probe]').select_option(score);ready()
 for c in builder.locator('[data-table-object]').all():c.uncheck()
 for id in [variant,twin]:builder.locator('[data-table-object="'+id+'"]').check()
 for c in builder.locator('[data-table-field]').all():c.uncheck()
 for field in [amount,tags,'description']:builder.locator('[data-table-field=\''+field+'\']').check()
 builder.locator('[data-table-create]').click();ready();builder.locator('[data-close]').click();handle=other.locator('[data-resize="se"]').bounding_box();page.mouse.move(handle['x']+4,handle['y']+4);page.mouse.down();page.mouse.move(2170,1050,steps=12);page.mouse.up()
 def cell(id,field):return other.locator('[data-table-cell="'+id+'"][data-column=\''+field+'\']')
 for id in [variant,twin]:other.locator('[data-table-select="'+id+'"]').check()
 cell(variant,'description').fill('Independent unapplied description');other.locator('[data-table-fill-field]').select_option(amount);other.locator('[data-table-fill-value]').fill('9223372036854775805');other.locator('[data-table-fill]').click();ready();expect(cell(variant,'description')).to_have_value('Independent unapplied description');expect(cell(twin,amount)).to_have_value('9223372036854775805');other.locator('[data-browser-fields-review]').click();expect(page.locator('#status')).to_contain_text('미적용');other.locator('[data-table-cancel="'+variant+'"][data-column="description"]').click()
 other.locator('[data-browser-fields-save]').click();ready();other.locator('[data-browser-fields-review]').click();expect(page.locator('#confirm')).to_be_enabled(timeout=180000);page.locator('#confirm').click();ready();expect(page.locator('#status')).to_contain_text('Source confirmed',timeout=180000);assert '9223372036854775805' in (project/'elements/HierarchyVariant.celem').read_text() and '9223372036854775805' in (project/'TableTwin.celem').read_text()
 # Distinct applied locations and private drafts are restored from IDs; relation snapshots are reread.
 main.locator('[data-parent="'+root+'"]').click();main.locator('[data-browser-control="object-query"]').fill('MAIN_PENDING');other.locator('[data-browser-control="object-query"]').fill('INDEPENDENT_PENDING');cell(variant,tags).fill('[8,9]');other.locator('[data-table-fill-field]').select_option(amount);other.locator('[data-table-fill-value]').fill('23');presentation=saved();meta=copy.deepcopy(next(row['meta'] for row in presentation['layout'] if row['key']==key));assert meta['parent']==score;assert next(row['meta'] for row in presentation['layout'] if row['key']=='browser')['parent']==root;assert 'objects' not in presentation and 'relationsMap' not in presentation
 after={f:f.read_bytes() for f in project.rglob('*') if f.is_file() and '.confectory' not in f.parts};page.screenshot(path='/tmp/confectory-v480-declaration-navigation.png',full_page=True);restart();ready();main=window('browser');other=window(key);expect(main.locator('[data-id="'+leaf+'"]')).to_be_visible(timeout=180000);expect(main.locator('[data-browser-control="object-query"]')).to_have_value('MAIN_PENDING');expect(other.locator('[data-browser-control="object-query"]')).to_have_value('INDEPENDENT_PENDING');expect(cell(variant,tags)).to_have_value('[8,9]');expect(other.locator('[data-table-fill-value]')).to_have_value('23');restored=next(row['meta'] for row in saved()['layout'] if row['key']==key);assert restored['tableFill']==meta['tableFill'] and restored['tableInputs']==meta['tableInputs'] and restored['tableSelected']==meta['tableSelected'];assert restored['parent']==score
 for f,blob in after.items():assert f.read_bytes()==blob,f
 assert registered.read_bytes()==registered_bytes
 for f,blob in originals.items():
  if f.name not in ['project.cpack','TableTwin.celem']:assert f.read_bytes()==blob,f
 print('PASS actual v480 declaration hierarchy: exact declared parent/category/concept/schema, owned and gated registered definitions, Variation/compiler registration, independent Workspace browser/typed atomic fill/Confirm, distinct cold contexts and original pending bases; sources preserved',flush=True)
