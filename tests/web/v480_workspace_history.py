"""IMP7 completed private moves/links through the real editor and durable presentation."""
import copy,json,shutil,uuid
from playwright.sync_api import expect

def prepare_history(project,root):
 second=root/'second-project';shutil.copytree(project,second,ignore=shutil.ignore_patterns('.confectory'))
 storage=root/'storage';storage.mkdir(exist_ok=True)
 (storage/'projects.json').write_text(json.dumps([{'path':str(folder/'project.cpack'),'title':title,'description':'Owned layout history fixture'} for folder,title in [(project,'History A'),(second,'History B')]]))

def verify_history(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':2200,'height':1400});original={p:p.read_bytes() for folder in [project,project.parent/'second-project'] for p in folder.rglob('*') if p.is_file() and '.confectory' not in p.parts}
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=180000);expect(page.locator('#workspace-save-state')).not_to_contain_text('편집창 복원 중',timeout=180000)
 def window(key):return page.locator('.window[data-key="'+key+'"]')
 def title(key):return window(key).locator('.window-title')
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def saved():page.evaluate('()=>globalThis.confectoryFlushPresentation()');return state()['presentation']
 def invoke(endpoint,args,ok=True):
  v=mount();rid=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=rid,expectedRevision=v['revision'],input=args))['ok'];result,_=settle(v,rid);assert ok is None or result['ok']==ok,result;assert send(envelope(v,'dispose'))['ok'];return result
 def history():return copy.deepcopy(saved().get('privateHistory',{'version':1,'undo':[],'redo':[]}))
 def step(undo=True):page.locator('#workspace').focus();page.keyboard.press('Control+z' if undo else 'Control+Shift+z');ready()
 def drag(key,x,y,cancel=None):
  b=title(key).bounding_box();page.mouse.move(b['x']+120,b['y']+18);page.mouse.down();page.mouse.move(x,y,steps=15)
  if cancel=='Escape':page.keyboard.press('Escape')
  elif cancel:title(key).evaluate('(e,type)=>e.dispatchEvent(new PointerEvent(type,{pointerId:1,bubbles:true}))',cancel)
  page.mouse.up();ready()
 def position(key,x,y):drag(key,x+120,y+18)
 def menu(key,label):title(key).click(button='right',position={'x':110,'y':18});page.locator('.context-menu').get_by_role('button',name=label,exact=True).click()
 def connect(parent,child):menu(parent,'자식 창 연결…');title(child).click(position={'x':100,'y':18});expect(page.locator('.workspace-link-prompt')).to_have_count(0)
 def geometry(value,owner='root'):
  rows=value['layout'] if owner=='root' else next(s for s in value['workspaces'] if s['id']==owner)['layout'];return {r['key']:[r['x'],r['y']] for r in rows if r['key'] in ['source','editor-1','browser']}
 def nav():
  ready();page.locator('#nav').click();page.locator('.nav-menu').get_by_role('button',name='개념',exact=True).click();ready()
  if page.locator('.nav-menu').count():page.locator('#nav').click()
 def root():page.locator('#workspace-home-tab').click();ready()
 def intact():
  expect(window('source').locator('#source')).to_have_value(latest_source);expect(window('editor-1').locator('[data-description]')).to_have_value(latest_property)
  assert page.locator('#source').evaluate('e=>e===globalThis.__imp7Source');assert window('editor-1').locator('[data-description]').evaluate('e=>e===globalThis.__imp7Property')
  assert saved()['inputs']['source']['draft']==basis['draft'];assert [(v['view'],v['id'],v['mode']) for v in state()['editorViews']]==bindings
 nav();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(window('schema').locator('[data-description]')).to_be_visible(timeout=120000);window('schema').locator('[data-close]').click();page.locator('#browser-actions').click();page.locator('#keep-properties').click();ready();expect(window('editor-1').locator('[data-description]')).to_be_visible();position('editor-1',1230,220);page.locator('#browser-actions').click();page.locator('#advanced-source').click();ready()
 latest_source=page.locator('#source').input_value()+'\n// IMP7_PENDING';latest_property='IMP7_PROPERTY_PENDING';page.locator('#source').fill(latest_source);window('editor-1').locator('[data-description]').fill(latest_property);position('source',500,180);position('browser',240,750);position('editor-1',1230,220)
 basis=copy.deepcopy(saved()['inputs']['source']);bindings=[(v['view'],v['id'],v['mode']) for v in state()['editorViews']]
 def remember():page.locator('#source').evaluate('e=>globalThis.__imp7Source=e');window('editor-1').locator('[data-description]').evaluate('e=>globalThis.__imp7Property=e')
 remember();initial=history();menu('source','자식 창 연결…');page.keyboard.press('Escape');assert history()==initial
 connect('source','editor-1');h=history();assert len(h['undo'])==len(initial['undo'])+1;step();assert not saved()['links'];assert len(history()['redo'])==1;step(False);assert saved()['links']==[{'parent':'source','child':'editor-1'}];intact()
 connect('editor-1','browser');connect('source','browser');assert saved()['links']==[{'parent':'source','child':'editor-1'},{'parent':'source','child':'browser'}];step();assert saved()['links'][-1]=={'parent':'editor-1','child':'browser'};step(False)
 menu('source','자식 연결 모두 해제');assert not saved()['links'];step();assert len(saved()['links'])==2;step(False);step();connect('editor-1','browser');assert not history()['redo'];menu('browser','부모 연결 해제');assert len(saved()['links'])==1;step();assert len(saved()['links'])==2
 # Completed linked movement is one entry. Provisional checkpoints, cancellation and no-op clicks are not entries.
 before=saved();count=len(history()['undo']);b=title('source').bounding_box();drag('source',b['x']+200,b['y']+68);moved=saved();assert len(history()['undo'])==count+1;assert geometry(before)!=geometry(moved)
 for cancel in ['Escape','pointercancel','lostpointercapture']:
  snapshot=history();b=title('source').bounding_box();drag('source',b['x']+230,b['y']+78,cancel);assert history()==snapshot;assert geometry(saved())==geometry(moved)
 snapshot=history();title('source').click(position={'x':110,'y':18});assert history()==snapshot
 b=title('source').bounding_box();page.mouse.move(b['x']+120,b['y']+18);page.mouse.down();page.mouse.move(b['x']+230,b['y']+78,steps=10);assert geometry(saved())==geometry(moved);assert history()==snapshot;page.keyboard.press('Escape');page.mouse.up()
 latest_source+='\n// EDIT_AFTER_MOVE';latest_property='EDIT_AFTER_MOVE';page.locator('#source').fill(latest_source);window('editor-1').locator('[data-description]').fill(latest_property);step();assert geometry(saved())==geometry(before);intact();step(False);assert geometry(saved())==geometry(moved);intact()
 # A portal transfer and its internal forest undo/redo together, using the same retained document DOM.
 area=page.locator('#workspace').bounding_box();page.locator('#workspace').click(button='right',position={'x':1850-area['x'],'y':950-area['y']});page.get_by_role('button',name='하위 Workspace 만들기',exact=True).click();portal=page.locator('.workspace-portal').last;child=portal.get_attribute('data-workspace-id');prior=saved();box=portal.bounding_box();drag('source',box['x']+box['width']/2,box['y']+box['height']/2);transferred=saved();assert len(geometry(transferred,child))==3;assert len(next(s for s in transferred['workspaces'] if s['id']==child)['links'])==2
 step();assert geometry(saved())==geometry(prior);intact();step(False);assert geometry(saved(),child)==geometry(transferred,child);portal.dblclick();ready();intact();step();assert not geometry(saved(),child);root();intact();step(False);portal=page.locator('.workspace-portal[data-workspace-id="'+child+'"]');portal.dblclick();ready();intact();root()
 # Backend accepts scoped history, rejects document/input snapshots and identity changes in it.
 valid=saved()
 for mutation in ['meta','null','flag','kind']:
  bad=copy.deepcopy(valid);c=next(c for c in bad['privateHistory']['undo'][-1]['changes'] if c.get('placement'))
  if mutation=='meta':c['after']['layout']['meta']={'revision':'must-not-become-authority'}
  elif mutation=='null':c['before']=None
  elif mutation=='flag':c['placement']=False
  else:c['kind']='inputs'
  invoke('savePresentation',{'presentation':bad},False);assert state()['presentation']==valid
 # A/B/A keeps independent history, documents and pending input. A real host restart restores both stacks.
 aid=state()['projectId'];a_history=history();page.locator('.brand').click();page.locator('[data-project]').filter(has_text='History B').locator('[data-enter]').click();ready();nav();assert state()['projectId']!=aid;assert not history()['undo'];position('browser',200,250);bh=history();assert bh['undo'];step();assert history()['redo'];page.locator('.brand').click();page.locator('[data-project]').filter(has_text='History A').locator('[data-enter]').click();ready();assert state()['projectId']==aid;assert history()==a_history
 root();step();cold=saved();assert cold['privateHistory']['redo'];restart();ready();root();remember();intact();assert history()==cold['privateHistory'];step(False);assert geometry(saved(),child)==geometry(transferred,child);step();intact()
 # An independent geometry change to one member blocks the complete inverse, retaining both stacks and every input.
 step(False);committed=saved();conflict=copy.deepcopy(committed);next(r for s in conflict['workspaces'] if s['id']==child for r in s['layout'] if r['key']=='editor-1')['x']+=17;invoke('savePresentation',{'presentation':conflict});restart();ready();root();snapshot=saved();step();expect(page.locator('#status')).to_contain_text('배치가 바뀌어');assert geometry(saved(),child)==geometry(snapshot,child);assert history()==snapshot['privateHistory'];assert saved()['inputs']==snapshot['inputs'];assert saved()['editorBindings']==snapshot['editorBindings']
 page.screenshot(path='/tmp/confectory-imp7-conflict.png',full_page=True)
 # Restore the fixture's committed placement; latest edits/CAS survive cold redo and another project switch.
 invoke('savePresentation',{'presentation':committed});restart();ready();root();step();remember();intact();step(False);page.locator('.workspace-portal[data-workspace-id="'+child+'"]').dblclick();ready();remember();intact();page.screenshot(path='/tmp/confectory-imp7-history.png',full_page=True)
 # The existing containing-group rule contributes both decorations and linked windows to one inverse.
 def create(label,x,y):
  area=page.locator('#workspace').bounding_box();page.locator('#workspace').click(button='right',position={'x':x-area['x'],'y':y-area['y']});page.get_by_role('button',name=label,exact=True).click()
 create('메모 만들기',1850,1000);note=page.locator('.workspace-note').last;note.locator('textarea').fill('GROUP_NOTE_FIRST');nid=note.get_attribute('data-workspace-item');create('그룹 만들기',1850,850);gid=page.locator('.workspace-group').last.get_attribute('data-workspace-item')
 fixture=saved();owner=next(s for s in fixture['workspaces'] if s['id']==child);group=next(i for i in owner['items'] if i['id']==gid);members=owner['layout']+[i for i in owner['items'] if i['id']==nid];left=min(r['x'] for r in members);top=min(r['y'] for r in members);group.update(x=left-30,y=top-40,width=max(r['x']+r['width'] for r in members)-left+60,height=max(r['y']+r['height'] for r in members)-top+70);invoke('savePresentation',{'presentation':fixture});restart();ready();remember();intact();note=page.locator('.workspace-note[data-workspace-item="'+nid+'"]');note.locator('textarea').evaluate('e=>globalThis.__imp7Note=e');g=page.locator('.workspace-group[data-workspace-item="'+gid+'"]');b=g.locator('.workspace-item-handle').bounding_box();prior=saved();page.mouse.move(b['x']+100,b['y']+18);page.mouse.down();page.mouse.move(b['x']+180,b['y']+68,steps=15);page.mouse.up();ready();after=saved();assert geometry(after,child)!=geometry(prior,child);assert len(after['privateHistory']['undo'][-1]['changes'])==5
 note.locator('textarea').fill('GROUP_NOTE_LATEST');step();assert geometry(saved(),child)==geometry(prior,child);expect(note.locator('textarea')).to_have_value('GROUP_NOTE_LATEST');assert note.locator('textarea').evaluate('e=>e===globalThis.__imp7Note');intact();step(False);assert geometry(saved(),child)==geometry(after,child);expect(note.locator('textarea')).to_have_value('GROUP_NOTE_LATEST');assert note.locator('textarea').evaluate('e=>e===globalThis.__imp7Note');intact();page.screenshot(path='/tmp/confectory-imp7-history.png',full_page=True)
 for file,data in original.items():assert file.read_bytes()==data,file
 assert not (project/'.confectory/project-activity').exists()
 print('PASS actual IMP7 private layout history: linked/group movement with latest canonical note and atomic portal/forest transfer Undo/redo, connect/reparent/disconnect-all, no-op/Escape/pointercancel/lostcapture and provisional checkpoint, redo branching, project isolation, cold both stacks, newest source/property DOM and CAS, atomic conflict and strict private payload',flush=True)
