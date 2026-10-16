"""Actual Home placed text search: graph, private notes, live results and workspace lifetimes."""
import json,uuid,time
from playwright.sync_api import expect

def verify_placed_find(page,project,mount,send,envelope,settle,restart):
 page.set_viewport_size({'width':1440,'height':1000})
 before={p:p.read_bytes() for p in project.iterdir() if p.is_file()};writes=[]
 def record(request):
  if request.url.endswith('/api/request'):
   try:
    data=json.loads(request.post_data or '{}')
    if data.get('op')=='invoke':writes.append(data.get('endpoint'))
   except ValueError:pass
 page.on('request',record)
 def ready():expect(page.locator('#nav')).to_be_enabled(timeout=180000)
 def invoke(endpoint,args):
  v=mount();request=uuid.uuid4().hex;assert send(envelope(v,'invoke',endpoint=endpoint,requestId=request,expectedRevision=v['revision'],input=args))['ok'];deadline=time.monotonic()+180;result=None
  while time.monotonic()<deadline:
   reply=send(envelope(v,'update'));assert reply['ok'],reply;result=next((r for r in reply.get('results',[]) if r['requestId']==request),None)
   if result:break
   time.sleep(.02)
  assert result and result['ok'],result;assert send(envelope(v,'dispose'))['ok'];return result['result']
 def nav(name):
  ready()
  if not page.locator('.nav-menu:visible').count():page.locator('#nav').click()
  page.locator('.nav-menu').get_by_role('button',name=name,exact=True).click();ready()
 def finder():return page.get_by_role('dialog',name='Workspace에서 찾기',exact=True)
 def search(panel,text,count):
  panel.get_by_role('searchbox').fill(text);expect(panel.locator('[data-find-count]')).to_have_text(count)
 def blank(x=1000,y=600):
  area=page.locator('#workspace').bounding_box()
  for px,py in [(x,y)]+[(area['width']*fx,area['height']*fy) for fx in [.85,.6,.3,.12] for fy in [.7,.45,.2]]:
   if 8<px<area['width']-8 and 8<py<area['height']-8 and page.evaluate("p=>{const el=document.elementFromPoint(p.x,p.y);return el?.id==='workspace'||(el?.closest('#workspace')&&!el.closest('.window,.workspace-decoration,.bubble-dock,.workspace-tabs'))}",{'x':area['x']+px,'y':area['y']+py}):return {'x':px,'y':py}
  raise AssertionError('no actual unoccupied Workspace point')
 def add(label,x,y):
  page.locator('#workspace').click(button='right',position=blank(x,y));page.get_by_role('button',name=label,exact=True).click()
 def zoom(delta):
  area=page.locator('#workspace').bounding_box();point=blank();page.mouse.move(area['x']+point['x'],area['y']+point['y']);page.mouse.wheel(0,delta)
 zoom(400)

 nav('기능 Blueprint');graph=page.locator('.window[data-key="blueprint"]');expect(graph.locator('[data-bp-node]')).to_have_count(2)
 graph.locator('[data-bp-find]').click();find=page.get_by_role('dialog',name='기능의 배치된 노드에서 찾기',exact=True);search(find,'POSITIVE','1 / 1');expect(graph.locator('[data-bp-node="condition"]')).to_have_class('bp-node is-placed-find-match');find.get_by_role('searchbox').press('Enter');expect(find.locator('[data-find-count]')).to_have_text('1 / 1');search(find,'fallback','1 / 1');expect(graph.locator('.bp-exit.is-placed-find-match')).to_have_count(1)
 find.locator('[data-find-close]').click();handle=graph.locator('[data-bp-drag="calculate"]');box=handle.bounding_box();page.mouse.move(box['x']+30,box['y']+12);page.mouse.down();page.mouse.move(box['x']+600,box['y']+12,steps=8);page.mouse.up();graph.locator('.caption strong').click();page.keyboard.press('Control+f');find=page.get_by_role('dialog',name='기능의 배치된 노드에서 찾기',exact=True);search(find,'four','1 / 1');node=graph.locator('[data-bp-node="calculate"]').bounding_box();viewport=graph.locator('.bp-scroll').bounding_box();assert node['width']<230 and node['x']>=viewport['x']-4 and node['x']+node['width']<=viewport['x']+viewport['width']+4,(node,viewport)
 search(find,'positive','1 / 1');graph.locator('[data-bp-read]').click();ready();expect(find.locator('[data-find-count]')).to_have_text('1 / 1');expect(graph.locator('[data-bp-node="condition"].is-placed-find-match')).to_have_count(1);page.screenshot(path='/tmp/confectory-v480-blueprint-find.png',full_page=True);graph.locator('[data-close]').click();expect(find).to_have_count(0);zoom(-400)
 # Search visible placed notes, including their current private input; not hidden cached graph windows.
 add('메모 만들기',300,150);first=page.locator('.workspace-note').last;first.locator('textarea').fill('Needle alpha <img src=x onerror=alert(1)>');first_id=first.get_attribute('data-workspace-item')
 add('메모 만들기',650,300);second=page.locator('.workspace-note').last;second.locator('textarea').fill('Needle beta');second_id=second.get_attribute('data-workspace-item')
 second.locator('textarea').press('Control+f');find=finder();search(find,'needle','1 / 2');find.get_by_role('searchbox').press('Enter');expect(find.locator('[data-find-count]')).to_have_text('2 / 2');find.get_by_role('searchbox').press('Shift+Enter');expect(find.locator('[data-find-count]')).to_have_text('1 / 2');expect(page.locator('.workspace-note.is-placed-find-match')).to_have_attribute('data-workspace-item',first_id);expect(find.locator('img')).to_have_count(0);expect(find.locator('[data-find-result]')).to_contain_text('<img src=x')
 search(find,'positive','0 / 0');search(find,'needle','1 / 2');page.locator('[data-workspace-item="'+second_id+'"] textarea').fill('Other private text');expect(find.locator('[data-find-count]')).to_have_text('1 / 1');page.screenshot(path='/tmp/confectory-v480-workspace-find.png',full_page=True)
 # Owned DOM guard fixture: password and hidden inputs are never included in the search text.
 page.locator('[data-workspace-item="'+first_id+'"]').evaluate("el=>{const password=document.createElement('input');password.type='password';password.value='SecretNeedleNever';el.append(password);const hidden=document.createElement('span');hidden.hidden=true;hidden.textContent='HiddenNeedleNever';el.append(hidden)}")
 search(find,'SecretNeedleNever','0 / 0');search(find,'HiddenNeedleNever','0 / 0');find.get_by_role('searchbox').press('Escape');expect(find).to_have_count(0);expect(page.locator('.is-placed-find-match')).to_have_count(0)
 # A child has an independent placed-node search scope. No query or overlay survives a switch/cold process.
 add('하위 Workspace 만들기',950,500);portal=page.locator('.workspace-portal').last;portal.dblclick();expect(page.locator('#workspace-home-tab')).to_have_attribute('aria-selected','false');page.keyboard.press('Control+f');find=finder();search(find,'needle','0 / 0');find.locator('[data-find-close]').click();add('메모 만들기',450,250);page.locator('.workspace-note textarea').fill('Needle child');page.locator('.workspace-note textarea').press('Control+f');find=finder();search(find,'needle','1 / 1');page.locator('#workspace-home-tab').click();expect(find).to_have_count(0);expect(page.locator('.workspace-note')).to_have_count(2)
 invoke('saveDraft',{});page.evaluate('()=>globalThis.confectoryFlushPresentation()');restart();ready();expect(page.locator('.placed-text-find')).to_have_count(0);nav('배치된 노드 찾기 · Ctrl+F');find=finder();expect(find.get_by_role('searchbox')).to_have_value('');search(find,'needle','1 / 1');page.locator('.brand').click();expect(find).to_have_count(0)
 assert all(p.read_bytes()==value for p,value in before.items()),'placed text search changed a source file'
 forbidden={'editDraft','editField','editMetadata','editDeclaration','editViewDeclaration','reviewDraft','confirmDraft','reviewGroup','confirmGroup','runProject','startAI','prepareAI','nodeTask','startBuild'};assert not forbidden.intersection(writes),writes
 print('PASS actual v480 placed text find: live placed graph/start/return and private notes, case-insensitive wrap, fresh source DOM, literal text, password/hidden exclusions, source preservation, independent child scope, close and cold/no query replay; no source/runtime/AI actions',flush=True)
