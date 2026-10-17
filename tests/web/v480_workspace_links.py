"""Real private view forest, live DOM, bundle portal moves and durable deletion inverses."""
import copy,json,uuid
from playwright.sync_api import expect

def verify_workspace_links(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':2200,'height':1400});before={p:p.read_bytes() for p in project.iterdir() if p.is_file()}
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=180000)
 def window(key):return page.locator('.window[data-key="'+key+'"]')
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def saved():page.evaluate('()=>globalThis.confectoryFlushPresentation()');return state()['presentation']
 def invoke(endpoint,args,ok=True):
  v=mount();rid=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=rid,expectedRevision=v['revision'],input=args))['ok'];result,_=settle(v,rid);assert ok is None or result['ok']==ok,result;assert send(envelope(v,'dispose'))['ok'];return result
 def title(key):return window(key).locator('.window-title')
 def drag(key,x,y,escape=False):
  b=title(key).bounding_box();page.mouse.move(b['x']+120,b['y']+18);page.mouse.down();page.mouse.move(x,y,steps=15)
  if escape:page.keyboard.press('Escape')
  page.mouse.up();ready()
 def position(key,x,y):drag(key,x+120,y+18)
 def menu(key,label):title(key).click(button='right',position={'x':110,'y':18});page.locator('.context-menu').get_by_role('button',name=label,exact=True).click()
 def connect(parent,child):
  ready();menu(parent,'자식 창 연결…');expect(page.locator('.workspace-link-prompt')).to_be_visible();title(child).click(position={'x':100,'y':18});expect(page.locator('.workspace-link-prompt')).to_have_count(0)
 def edges(owner=None):return (owner or saved()).get('links',[])
 def geometry(value,keys):return {r['key']:(r['x'],r['y']) for r in value['layout'] if r['key'] in keys}
 def create(kind,x=1850,y=850):
  area=page.locator('#workspace').bounding_box();page.locator('#workspace').click(button='right',position={'x':x-area['x'],'y':y-area['y']});page.get_by_role('button',name={'portal':'하위 Workspace 만들기','note':'메모 만들기'}[kind],exact=True).click();return page.locator('.workspace-'+kind).last
 def root():page.locator('#workspace-home-tab').click();ready()
 ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='개념',exact=True).click();ready()
 if page.locator('.nav-menu').count():page.locator('#nav').click()
 page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(window('schema').locator('[data-description]')).to_be_visible(timeout=120000);window('schema').locator('[data-close]').click();page.locator('#browser-actions').click();page.locator('#keep-properties').click();ready();expect(window('editor-1').locator('[data-description]')).to_be_visible();window('editor-1').locator('[data-description]').fill('PRIVATE_LINK_PENDING');position('editor-1',1230,220);page.locator('#browser-actions').click();page.locator('#advanced-source').click();ready();source=window('source').locator('#source');expect(source).to_be_visible();pending=source.input_value()+'\n// PRIVATE_LINK_PENDING_SOURCE';source.fill(pending);source.evaluate('e=>globalThis.__linkedSource=e');window('editor-1').locator('[data-description]').evaluate('e=>globalThis.__linkedProperty=e')
 position('source',500,180);position('browser',240,750);position('editor-1',1230,220);keys=['source','editor-1','browser'];basis=copy.deepcopy(saved()['inputs']['source']);bindings=[(v['view'],v['id'],v['mode']) for v in state()['editorViews']]
 menu('source','자식 창 연결…');page.keyboard.press('Escape');expect(page.locator('.workspace-link-prompt')).to_have_count(0);assert not edges()
 connect('source','editor-1');connect('editor-1','browser');assert edges()==[{'parent':'source','child':'editor-1'},{'parent':'editor-1','child':'browser'}]
 menu('browser','자식 창 연결…');title('source').click(position={'x':100,'y':18});expect(page.locator('.workspace-link-prompt')).to_be_visible();page.keyboard.press('Escape');assert len(edges())==2
 connect('source','browser');assert sum(e['child']=='browser' for e in edges())==1;connect('editor-1','browser');menu('browser','부모 연결 해제');assert len(edges())==1;connect('editor-1','browser')
 # Backend validation keeps the previous private presentation and never mutates source.
 valid=saved()
 for edge in [{'parent':'browser','child':'source'},{'parent':'source','child':'missing-private-view'}]:
  bad=copy.deepcopy(valid);bad['links'].append(edge);invoke('savePresentation',{'presentation':bad},False);assert state()['presentation']==valid
 bad=copy.deepcopy(valid);bad['privateHistory']={'version':1,'undo':[{'changes':[{'kind':'inputs','key':'source','before':None,'after':{'text':'must not apply'}}]}],'redo':[]};invoke('savePresentation',{'presentation':bad},False);assert state()['presentation']==valid
 a=geometry(saved(),keys);b=title('source').bounding_box();drag('source',b['x']+200,b['y']+68);moved=geometry(saved(),keys);dx=moved['source'][0]-a['source'][0];dy=moved['source'][1]-a['source'][1];assert dx and dy
 for key in keys:assert abs((moved[key][0]-a[key][0])-dx)<2 and abs((moved[key][1]-a[key][1])-dy)<2,(a,moved)
 b=title('source').bounding_box();page.mouse.move(b['x']+120,b['y']+18);page.mouse.down();page.mouse.move(b['x']+250,b['y']+90,steps=10);assert geometry(saved(),keys)==moved,'an input checkpoint must not publish provisional drag geometry';page.keyboard.press('Escape');page.mouse.up();assert geometry(saved(),keys)==moved;
 b=title('source').bounding_box();drag('source',b['x']+250,b['y']+90,True);assert geometry(saved(),keys)==moved;expect(source).to_have_value(pending);assert source.evaluate('e=>e===globalThis.__linkedSource')
 portal=create('portal');child=portal.get_attribute('data-workspace-id');uncontested=saved();conflict=copy.deepcopy(uncontested);next(s for s in conflict['workspaces'] if s['id']==child)['layout'].append(copy.deepcopy(next(r for r in conflict['layout'] if r['key']=='source')));invoke('savePresentation',{'presentation':conflict});restart();ready();prior=geometry(saved(),keys);portal=page.locator('.workspace-portal[data-workspace-id="'+child+'"]');box=portal.bounding_box();drag('source',box['x']+box['width']/2,box['y']+box['height']/2);assert geometry(saved(),keys)==prior and len(edges())==2;expect(source).to_have_value(pending)
 invoke('savePresentation',{'presentation':uncontested});restart();ready();source.evaluate('e=>globalThis.__linkedSource=e');window('editor-1').locator('[data-description]').evaluate('e=>globalThis.__linkedProperty=e');portal=page.locator('.workspace-portal[data-workspace-id="'+child+'"]');box=portal.bounding_box();drag('source',box['x']+box['width']/2,box['y']+box['height']/2);p=saved();space=next(s for s in p['workspaces'] if s['id']==child);assert len(space['links'])==2 and all(k not in [r['key'] for r in p['layout']] for k in keys);relative=geometry({'layout':space['layout']},keys)
 for key in keys:assert abs((relative[key][0]-relative['source'][0])-(moved[key][0]-moved['source'][0]))<2
 portal.dblclick();ready();expect(source).to_have_value(pending);expect(window('editor-1').locator('[data-description]')).to_have_value('PRIVATE_LINK_PENDING');assert source.evaluate('e=>e===globalThis.__linkedSource');assert window('editor-1').locator('[data-description]').evaluate('e=>e===globalThis.__linkedProperty')
 # Moving a child alone cuts its incoming boundary edge; moving its parent carries its remaining descendant.
 parent=page.locator('.workspace-parent-node').bounding_box();drag('browser',parent['x']+parent['width']/2,parent['y']+parent['height']/2);assert len(next(s for s in saved()['workspaces'] if s['id']==child)['links'])==1
 parent=page.locator('.workspace-parent-node').bounding_box();drag('source',parent['x']+parent['width']/2,parent['y']+parent['height']/2);root();expect(source).to_have_value(pending);assert edges()==[{'parent':'source','child':'editor-1'}]
 # A selected parent deletion removes its placement and incident link, never its child or source.
 title('source').click(position={'x':110,'y':18});page.keyboard.press('Delete');expect(window('source')).to_be_hidden();expect(window('editor-1')).to_be_visible();assert not edges();assert saved()['privateHistory']['undo'];page.keyboard.press('Control+z');expect(source).to_be_visible();expect(source).to_have_value(pending);assert len(edges())==1;assert source.evaluate('e=>e===globalThis.__linkedSource');page.keyboard.press('Control+Shift+z');expect(window('source')).to_be_hidden();deleted=saved();assert deleted['inputs']['source']['draft']==basis['draft']
 # A new host and browser restore the deletion inverse and the original input/CAS basis.
 conflict=copy.deepcopy(deleted);next(r for r in conflict['layout'] if r['key']=='source')['x']+=17;invoke('savePresentation',{'presentation':conflict});restart();ready();page.locator('#workspace').focus();page.keyboard.press('Control+z');expect(window('source')).to_be_hidden();expect(page.locator('#status')).to_contain_text('배치가 바뀌어');assert saved()['privateHistory']['undo']==conflict['privateHistory']['undo'];expect(window('editor-1').locator('[data-description]')).to_have_value('PRIVATE_LINK_PENDING');invoke('savePresentation',{'presentation':deleted})
 restart();ready();page.locator('#workspace').focus();page.keyboard.press('Control+z');expect(source).to_be_visible(timeout=120000);expect(source).to_have_value(pending);expect(window('editor-1').locator('[data-description]')).to_have_value('PRIVATE_LINK_PENDING');assert saved()['inputs']['source']['draft']==basis['draft'];assert [(v['view'],v['id'],v['mode']) for v in state()['editorViews']]==bindings
 position('browser',240,750)
 # Reopened views retain their private identity and can join the same forest again.
 window('source').locator('[data-close]').click();page.locator('#browser-actions').click();page.locator('#advanced-source').click();ready();expect(source).to_have_value(pending);connect('source','editor-1')
 portal=page.locator('.workspace-portal[data-workspace-id="'+child+'"]');box=portal.bounding_box();drag('source',box['x']+box['width']/2,box['y']+box['height']/2);portal.dblclick();ready();nested=create('portal');nested_id=nested.get_attribute('data-workspace-id');nested.dblclick();ready();note=create('note',1700,900);note.locator('[data-note-editor],textarea').fill('PRIVATE_NESTED_NOTE');root();portal=page.locator('.workspace-portal[data-workspace-id="'+child+'"]');portal.locator('[data-remove]').click();page.locator('.modal [data-cancel]').click();assert len(saved()['workspaces'])==2;portal.locator('[data-remove]').click();page.locator('.modal [data-confirm]').click();assert not saved()['workspaces'];assert saved()['inputs']['source']['draft']==basis['draft']
 restart();ready();page.locator('#workspace').focus();page.keyboard.press('Control+z');expect(page.locator('.workspace-portal[data-workspace-id="'+child+'"]')).to_be_visible(timeout=120000);p=saved();assert len(p['workspaces'])==2;assert len(next(s for s in p['workspaces'] if s['id']==child)['links'])==1;page.locator('.workspace-portal[data-workspace-id="'+child+'"]').dblclick();ready();expect(source).to_have_value(pending);expect(window('editor-1').locator('[data-description]')).to_have_value('PRIVATE_LINK_PENDING');page.locator('.workspace-portal[data-workspace-id="'+nested_id+'"]').dblclick();expect(page.locator('.workspace-note [data-note-editor],.workspace-note textarea')).to_be_visible();assert page.locator('.workspace-note [data-note-editor],.workspace-note textarea').evaluate("e=>e.matches('textarea')?e.value:e.innerText")=='PRIVATE_NESTED_NOTE';assert saved()['inputs']['source']['draft']==basis['draft']
 # Docking cuts canvas links while retaining the exact private source document.
 page.locator('#workspace-tab-'+child).click();ready();expect(source).to_have_value(pending);page.screenshot(path='/tmp/confectory-v480-workspace-links.png',full_page=True);source.evaluate('e=>globalThis.__dockedLinkedSource=e');menu('source','탭으로 열기');expect(page.locator('[data-window-tab="source"]')).to_be_visible();assert not next(s for s in saved()['workspaces'] if s['id']==child).get('links',[]);expect(source).to_have_value(pending);assert source.evaluate('e=>e===globalThis.__dockedLinkedSource');window('source').locator('[data-document-return]').click();expect(source).to_have_value(pending);assert saved()['inputs']['source']['draft']==basis['draft']
 for file,data in before.items():assert file.read_bytes()==data,file
 assert not (project/'.confectory/project-activity').exists(),'private placement is not a source Save/Confirm event'
 # Existing source CAS refuses a real external modification; private history never rebases it.
 external=before[project/'Score.celem']+b'\n// EXTERNAL_SOURCE_EXPECTED_CAS\n';(project/'Score.celem').write_bytes(external);result=invoke('editDraft',{'id':'Example.ButtonGame::Score','text':pending,'revision':basis['draft']['revision']},None)
 if result['ok']:
  reviewed=invoke('reviewDraft',{'id':'Example.ButtonGame::Score','target':'linux'},None);assert not reviewed['ok'] or state().get('review',{}).get('status') in ['conflict','stale','invalid'],state().get('review')
 assert (project/'Score.celem').read_bytes()==external;expect(source).to_have_value(pending)
 page.screenshot(path='/tmp/confectory-v480-workspace-links-conflict.png',full_page=True)
 print('PASS actual v480 private Workspace links: one parent/cycle/cancel/validation, descendant movement and Escape, portal boundary/internal edges and relative offsets, selected-only deletion/Undo/redo, retained DOM and pending basis, nested portal cancel/delete, exact cold inverse, duplicate-target/changed-layout conflicts, retained docking and external source CAS refusal',flush=True)
