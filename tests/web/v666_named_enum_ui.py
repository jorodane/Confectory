"""Explicit ID-only to native enum preparation in the existing header transaction."""
import copy,json,sys,time
from playwright.sync_api import sync_playwright,expect
import v536_wide_mixed as f
mode=sys.argv[3]if len(sys.argv)>3 else'normal';detached='view'in sys.argv[4:];owner=f.n+'Mood';panel_key='editor-1'if detached else'declaration'
initial=[dict(id='stable-ready',name='준비',icon='★'),dict(id='stable-done',name='완료')]
file=f.project/'Mood.celem';file.write_bytes(('enum '+owner+' { // 원래 종류 · 😀\r\nvalue editorEnumProfile="nominal-members-v1";value editorEnumValues='+json.dumps(json.dumps(initial,ensure_ascii=False,separators=(',',':')))+';}\r\n').encode());f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element Mood enum "Mood.celem";element ChoiceShape schema "ChoiceShape.celem";element ChoiceOwner object "ChoiceOwner.celem";registry Confectory.Build.DotNet',1));(f.project/'ChoiceShape.celem').write_text('schema '+f.n+'ChoiceShape {field Choice single enum '+owner+';}');(f.project/'ChoiceOwner.celem').write_text('object '+f.n+'ChoiceOwner {use schema '+f.n+'ChoiceShape;data Choice="stable-done";}');snapshot={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()}
def original(except_names=()):assert all(p.read_bytes()==raw for p,raw in snapshot.items()if p.name not in except_names)
def panel():return f.page.locator('.window[data-key="'+panel_key+'"]')
def pending():return[(k,v)for k,v in f.pending()['schema']if'|'+owner+'|'in k]
def shown():
 f.invoke('openEditorView',dict(view='1',id=owner,viewMode='declaration'))if detached else f.invoke('inspectDeclaration',dict(id=owner));s=f.state();return next(row for row in s['editorViews']if row['view']=='1')['declaration']if detached else s['declaration']
def open_card():
 f.idle()
 if panel().locator('[data-enum-definition]').is_visible():return
 f.invoke('select',dict(id=owner));f.invoke('inspectDeclaration',dict(id=owner));f.page.reload();f.idle()
 if not f.page.locator('.window[data-key=declaration] [data-enum-definition]').is_visible():
  f.page.locator('#workspace').click(button='right',position=dict(x=1300,y=200));f.page.get_by_role('button',name='프로젝트 브라우저',exact=True).click();b=f.page.locator('.window[data-key^="browser:project:"]');b.locator('[data-tab=info]').click();b.locator('[data-browser-control=object-query]').fill('Mood');b.locator('[data-browser-control=object-search]').click();b.locator('[data-object="'+owner+'"]').press('F2');b.locator('[data-close]').first.click()
 if detached:f.page.locator('.window[data-key=declaration] [data-declaration-keep]').click();f.idle();f.invoke('select',dict(id=f.n+'Unit'));f.idle()
 expect(panel().locator('[data-enum-definition]')).to_be_visible()
def restart(i):
 f.pending();f.page.close();f.stop();f.start(i);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400));open_card()
def wait_save(ok=True):
 mark=len(f.traffic);panel().locator('[data-declaration-header-action=save]').click();deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  ids={row['invoke']['requestId']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='applySlots'};results=[row['result']for row in f.traffic[mark:]if row.get('result',{}).get('requestId')in ids and row['result'].get('error',{}).get('code')!='stale_revision']
  if results:assert bool(results[-1]['ok'])==ok,results[-1];f.idle();return
  f.page.wait_for_timeout(20)
 raise AssertionError('bounded enum preparation Save response deadline')
def verify():
 row=next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==owner);meta=f.metadata('inspect',text=row['draft']);assert meta['enumValues']==initial;assert meta['values']['editorEnumProfile']=='nominal-members-native-v2';numbers=json.loads(meta['values']['editorEnumNumbers']);assert numbers=={'stable-ready':1,'stable-done':2};return row['atomicEditGroup']if'atomicEditGroup'in row else[owner]
try:
 f.start(0);f.invoke('select',dict(id=owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=1900,height=1400));open_card();expect(panel().locator('[data-enum-clr-notice]')).to_contain_text('구버전');panel().locator('[data-enum-native]').click();held=copy.deepcopy(pending());assert len(held)==1 and held[0][1]['kind']=='enum-native';original();panel().locator('.object-title-name').click();panel().press('Control+z');assert not pending();panel().press('Control+y');assert pending()==held;restart(1);assert pending()==held and checkpoint.read_bytes()==before;original();f.checked('explicit native enum preparation preserves the exact ID/name/icon list through Undo/Redo and unsaved cold restoration without touching current ID-valued consumers')
  if detached:
   current=next(row for row in f.state()['editorViews']if row['view']=='1');binding=current['authorBinding'];hash=current['declaration']['textHash'];prepared=f.invoke('blueprint',dict(action='readOwnerEdits',id=owner,hash=hash,view='1',viewBinding=binding,owner=owner))['result']['result'];base=dict(basis=prepared['basis'],action='applySlots',id=owner,view='1',viewBinding=binding,owner=owner,rows=[],declaration=dict(id=owner,hash=hash,changes=[dict(type='enum-native',text='nominal-members-native-v2')]))
   for label,patch in [('stale view',dict(viewBinding='0'*32)),('another owner',dict(id=f.n+'Unit',owner=f.n+'Unit')),('unbound rows',dict(rows=[{}])),('raw source',dict(declaration=dict(base['declaration'],raw='enum '+owner+' {}'))),('non-header edit',dict(declaration=dict(base['declaration'],changes=[dict(type='data',text='{}')])) )]:
    f.invoke('blueprint',copy.deepcopy(base)|patch,False);assert checkpoint.read_bytes()==before and pending()==held;original()
   f.checked('bound detached enum preparation rejects stale binding, another owner, nonempty slot rows, raw source and unrelated edits without changing checkpoint, source or pending input')
  if mode=='cancel':
   panel().locator('[data-declaration-header-action=discard]').click();f.idle();assert not pending()and checkpoint.read_bytes()==before;restart(2);assert not pending();original();f.checked('explicit discard and cold restoration leave the legacy enum and all consumers unchanged');f.browser.close();raise SystemExit(0)
  if mode=='storage':
   checkpoint.chmod(0o400)
   try:wait_save(False);assert pending()==held and checkpoint.read_bytes()==before;original()
   finally:checkpoint.chmod(0o600)
   restart(2);assert pending()==held;f.checked('failed enum preparation storage retains the original profile, consumer IDs and exact pending activation across cold restart')
  wait_save();deadline=time.monotonic()+30
  while pending()and time.monotonic()<deadline:f.page.wait_for_timeout(20)
  assert not pending();ids=verify();original();restart(3);assert verify()==ids and not pending();f.checked('the same header Save stores a versioned permanent number table atomically and restores it without rewriting item IDs or source consumers')
  f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;f.invoke('confirmGroup',dict(ids=ids,token=review['token']));original({'Mood.celem'});doc=f.metadata('informationClr',project=str(f.manifest),id=owner);assert doc['kind']=='enum'and{row['id']:row['value']for row in doc['members']}=={'stable-ready':1,'stable-done':2};f.checked('explicit compiler Review/Confirm publishes only the enum numeric contract; existing stored selection stable-done and other source bytes survive')
  assert not f.errors and not f.external,(f.errors,f.external);f.idle();f.page.screenshot(path=str(f.case/'enum-numeric-preparation.png'));f.browser.close()
except Exception:
 try:(f.case/'enum-clr-failure.json').write_text(json.dumps(dict(state=f.state(),traffic=f.traffic[-60:],errors=f.errors),ensure_ascii=False,indent=2))
 except Exception:pass
 raise
finally:f.stop();(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2))
