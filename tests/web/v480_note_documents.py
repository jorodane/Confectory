"""Actual note document views, canonical private ownership and retained editor lifetimes."""
import json,time,uuid
from playwright.sync_api import expect

def verify_note_documents(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1440,'height':1000});before={p:p.read_bytes() for p in project.iterdir() if p.is_file()};requests=[];external=[]
 def observe(request):
  if request.url.endswith('/api/request') and request.method=='POST':requests.append((request.post_data_json or {}).get('endpoint'))
  if 'notes-paste.invalid' in request.url:external.append(request.url)
 page.on('request',observe)
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=180000)
 def state():
  v=mount();s=v['state'];assert send(envelope(v,'dispose'))['ok'];return s
 def invoke(endpoint,args):
  v=mount();request=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args))['ok'];deadline=time.monotonic()+180;result=None
  while time.monotonic()<deadline:
   reply=send(envelope(v,'update'));assert reply['ok'],reply;result=next((r for r in reply.get('results',[]) if r['requestId']==request),None)
   if result:break
   time.sleep(.02)
  assert result and result['ok'],result;assert send(envelope(v,'dispose'))['ok'];return result['result']
 def flush():page.evaluate('()=>globalThis.confectoryFlushPresentation()')
 def saved():flush();return state()['presentation']
 def item(id):
  p=saved();return next(x for x in p['workspaceItems']+[x for w in p.get('workspaces',[]) for x in w.get('items',[])] if x['id']==id)
 def note(id):return page.locator('[data-workspace-item="'+id+'"]')
 def doc(id):return page.locator('[data-note-document="'+id+'"]')
 def body(id):return doc(id).locator('[data-note-editor]')
 def tab(id):return page.locator('[data-note-tab="'+id+'"]')
 def blank(x,y):
  area=page.locator('#workspace').bounding_box()
  for px,py in [(x,y)]+[(area['width']*fx,area['height']*fy) for fx in [.85,.6,.3,.12] for fy in [.7,.45,.2]]:
   if 8<px<area['width']-8 and 8<py<area['height']-8 and page.evaluate("p=>{const el=document.elementFromPoint(p.x,p.y);return el?.id==='workspace'||(el?.closest('#workspace')&&!el.closest('.window,.workspace-decoration,.bubble-dock,.workspace-tabs,.tab-document'))}",{'x':area['x']+px,'y':area['y']+py}):return {'x':px,'y':py}
  raise AssertionError('no unoccupied Workspace point')
 def add(label,x,y):page.locator('#workspace').click(button='right',position=blank(x,y));page.get_by_role('button',name=label,exact=True).click()
 def new_note(text,x=350,y=220):
  add('메모 만들기',x,y);id=page.locator('.workspace-note').last.get_attribute('data-workspace-item');note(id).locator('textarea').fill(text);return id
 def workspace():page.locator('#workspace-home-tab').click()
 def open_note(id):
  note(id).locator('.workspace-item-name').dblclick();expect(doc(id)).to_be_visible();expect(note(id).locator('.workspace-name-editor')).to_have_count(0);assert doc(id).locator('.note-document-heading').bounding_box()['y']>=page.locator('#workspace-tabs').bounding_box()['y']+page.locator('#workspace-tabs').bounding_box()['height'],'document heading must be below the tab bar'
 ready();original='Plain <b>literal</b>\nline';first=new_note(original);baseline=item(first);camera=saved()['workspaceView'];open_note(first)
 assert body(first).inner_text()==original;expect(body(first).locator('b')).to_have_count(0);assert item(first)==baseline,'opening a document must not migrate the plain note';assert saved()['workspaceView']==camera
 page.locator('[data-note-tab-close="'+first+'"]').click();expect(doc(first)).to_have_count(0);expect(note(first).locator('textarea')).to_have_value(original);assert item(first)==baseline
 open_note(first);body(first).fill('Document body');body(first).press('Control+a');doc(first).get_by_role('button',name='굵게',exact=True).click();formatted=body(first).inner_html();body(first).press('Control+z');assert body(first).inner_html()!=formatted,'native undo must change document formatting';body(first).press('Control+Shift+z');assert body(first).inner_html()==formatted,'native redo must restore document formatting';assert item(first)['text']=='Document body' and 'richText' in item(first)
 workspace();expect(note(first).locator('[data-note-editor]')).to_have_text('Document body');assert saved()['workspaceView']==camera;note(first).locator('[data-note-editor]').fill('Inline latest');tab(first).click();expect(body(first)).to_have_text('Inline latest');workspace();open_note(first);expect(doc(first)).to_have_count(1);expect(tab(first)).to_have_count(1)
 # Focus on the document header must not delete the hidden Workspace selection.
 doc(first).focus();page.keyboard.press('Delete');expect(doc(first)).to_be_visible();assert item(first)['text']=='Inline latest'
 body(first).press('Control+f');find=page.get_by_role('dialog',name='메모 본문에서 찾기',exact=True);find.get_by_role('searchbox').fill('Inline latest');expect(find.locator('[data-find-count]')).to_have_text('1 / 1');workspace();expect(find).to_have_count(0)
 second=new_note('Second independent note',780,410);second_before=item(second);open_note(second);tab(first).click();expect(body(first)).to_have_text('Inline latest');page.locator('[data-note-tab-close="'+second+'"]').click();expect(doc(first)).to_be_visible();assert item(second)==second_before
 doc(first).get_by_role('button',name='메모 제목 서식',exact=True).click();title=page.get_by_role('dialog',name='제목 서식',exact=True);title.locator('[data-title-size]').fill('23');title.locator('[data-title-apply]').click();expect(doc(first).locator('[data-note-document-title]')).to_have_css('font-size','23px');workspace();expect(note(first).locator('.workspace-item-name')).to_have_css('font-size','23px')
 # A child note remains owned by that child when its global document is edited from Root.
 add('하위 Workspace 만들기',1050,560);page.locator('.workspace-portal').last.dblclick();child=new_note('Child document');open_note(child);workspace();tab(child).click();body(child).fill('Child changed from Root');doc(child).get_by_role('button',name='메모 제목 서식',exact=True).click();title=page.get_by_role('dialog',name='제목 서식',exact=True);title.locator('[data-title-size]').fill('21');title.locator('[data-title-apply]').click();p=saved();assert all(x['id']!=child for x in p['workspaceItems']);assert any(x['id']==child and x['text']=='Child changed from Root' and x['titleStyle']['size']==21 for w in p['workspaces'] for x in w['items']);workspace();page.locator('.workspace-portal').last.dblclick();expect(note(child).locator('[data-note-editor]')).to_have_text('Child changed from Root');workspace()
 # Keep an ordinary source editor alive with unapplied text while a document hides it.
 page.locator('#nav').click();page.locator('.nav-menu button').filter(has_text='개념').first.click();ready();page.locator('#nav').click();page.locator('[data-id="Example.ButtonGame::Score"]').click();expect(page.locator('[data-description]')).to_be_visible();page.locator('.window[data-key="schema"] [data-close]').click();page.locator('#browser-actions').click();page.locator('#advanced-source').click();expect(page.locator('#source')).to_be_visible();pending=page.locator('#source').input_value()+'\n// NOTE_DOCUMENT_PENDING';page.locator('#source').fill(pending);tab(first).click();expect(page.locator('#source')).not_to_be_visible();expect(body(first)).to_have_text('Inline latest');flush();page.screenshot(path='/tmp/confectory-v480-note-document.png',full_page=True)
 restart();ready();expect(doc(first)).to_be_visible(timeout=60000);expect(body(first)).to_have_text('Inline latest');expect(doc(first).locator('[data-note-document-title]')).to_have_css('font-size','23px');expect(page.get_by_role('dialog',name='메모 본문에서 찾기',exact=True)).to_have_count(0);workspace();expect(page.locator('#source')).to_have_value(pending);expect(note(first).locator('[data-note-editor]')).to_have_text('Inline latest');page.screenshot(path='/tmp/confectory-v480-note-document-cold.png',full_page=True)
 tab(first).click();page.locator('.brand').click();page.locator('#home-projects').wait_for();expect(page.locator('.workspace-note-document')).to_have_count(0);page.locator('[data-enter]').click();ready();expect(doc(first)).to_be_visible();expect(body(first)).to_have_text('Inline latest');workspace();expect(page.locator('#source')).to_have_value(pending)
 # Deleting the source explicitly prunes its document without resurrecting a copy.
 page.locator('.window[data-key="source"] [data-close]').click();page.locator('.window[data-key="browser"] [data-close]').click();note(first).locator('.workspace-item-handle').click(button='right',position={'x':80,'y':18});page.locator('.context-menu').get_by_role('button',name='메모 삭제',exact=True).click();expect(note(first)).to_have_count(0);expect(tab(first)).to_have_count(0);expect(doc(first)).to_have_count(0);assert first not in saved().get('noteDocuments',[]);assert item(second)==second_before
 # Invalid restored view IDs are ignored, and display never rewrites raw private HTML.
 p=saved();target=next(x for x in p['workspaceItems'] if x['id']==second);raw='<b>Restored safe</b><img src="https://notes-paste.invalid/restore" onerror="globalThis.__noteInjected=true"><script>globalThis.__noteInjected=true</script>';target['richText']=raw;mirror=target['text'];p['noteDocuments']=[second,second,'missing-note-id'];p['activeNoteDocument']=second;invoke('savePresentation',{'presentation':p});restart();ready();expect(doc(second)).to_be_visible();expect(tab(second)).to_have_count(1);expect(body(second)).to_have_text('Restored safe');expect(body(second).locator('script,img,[onerror]')).to_have_count(0);assert not page.evaluate('()=>globalThis.__noteInjected');assert item(second)['richText']==raw and item(second)['text']==mirror
 body(second).fill('Explicit clean edit');assert item(second)['text']=='Explicit clean edit' and '<script' not in item(second)['richText'];assert all(p.read_bytes()==value for p,value in before.items()),'private document edits changed project source bytes';assert not external,external;assert not (set(requests)&{'editDraft','saveDraft','reviewDraft','confirmDraft','editEditorView','saveEditorView','runProject','startAI','startWorker','startBuild','adoptWorker'}),requests
 print('PASS actual v480 note documents: explicit view-only open/close, native formatting undo/redo, canonical inline/document sync, independent child ownership, title style, document Find and deletion guards, cold active tabs with retained unapplied source input, explicit source deletion cleanup, inert restored HTML without read migration, unchanged original project bytes',flush=True)
