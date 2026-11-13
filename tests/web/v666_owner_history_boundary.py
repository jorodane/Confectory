"""Trace trusted owner hotkeys and native browser history before any source write."""
import json,time,sys
from playwright.sync_api import sync_playwright,expect
import v666_scalar_owner_contracts_fixture as x
f,d=x.f,x.d;events=[];phases=[]
def capture(page):
 def record(source,event):
  events.append(event);(f.case/'owner-history-events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
 page.expose_binding('recordOwnerHistoryBoundary',record)
 page.evaluate('''()=>{const node=el=>el?{tag:el.tagName,window:el.closest?.('.window')?.dataset.key,property:el.closest?.('[data-property-path]')?.dataset.propertyPath,draft:el.closest?.('[data-definition-key]')?.dataset.definitionKey,name:el.getAttribute?.('aria-label'),functionToggle:el.matches?.('[data-own-functions-toggle]'),propertyToggle:el.matches?.('[data-own-properties-toggle]'),headerIcon:el.matches?.('.object-icon-edit'),value:'value'in el?el.value:null}:null;for(const type of ['keydown','keyup','beforeinput','input','focusin'])document.addEventListener(type,e=>{if(type==='focusin'||type==='beforeinput'||type==='input'||e.ctrlKey||e.metaKey||e.key==='Control'){const initial={type,key:e.key,code:e.code,ctrl:e.ctrlKey,meta:e.metaKey,composing:e.isComposing,inputType:e.inputType,trusted:e.isTrusted,target:node(e.target),active:node(document.activeElement),preventedAtCapture:e.defaultPrevented};setTimeout(()=>window.recordOwnerHistoryBoundary({...initial,preventedAfter:e.defaultPrevented,activeAfter:node(document.activeElement)}),0);}},true)}''')
def phase(name):
 data=dict(name=name,pending=d.pending(),focus=f.page.evaluate('({tag:document.activeElement?.tagName,html:document.activeElement?.outerHTML.slice(0,450)})'));phases.append(data);(f.case/'owner-history-phases.json').write_text(json.dumps(phases,ensure_ascii=False,indent=2));return data['pending']
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 with sync_playwright()as pw:
  expect.set_options(timeout=60000);f.browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);f.page=f.setup();f.page.set_viewport_size(dict(width=2300,height=1700));d.open_info();capture(f.page)
  if '--native'in sys.argv:
   for index in range(2):
    f.owner().locator('[data-inline-method="'+x.functions[index]+'"] > .function-node-heading').dblclick(position=dict(x=190,y=3));p=f.page.locator('.function-detail-popover');expect(p).to_be_visible();x.edit_contract(p,index);p.get_by_role('button',name='저장',exact=True).click();expect(p).to_have_count(0);x._prior.after_contract(index)
  row=d.add('키 경계 새 수량 😀','general','long');row.locator('[data-property-value]').fill('9223372036854775804');f.idle();held=phase('before-function-undo');button=f.owner().locator('[data-own-functions-toggle]');button.press('Control+z');f.idle();after=phase('after-function-undo');button.press('Control+y');f.idle();restored=phase('after-function-redo');x.unchanged();assert checkpoint.read_bytes()==before
  keys=[e for e in events if e['type']=='keydown'and e['key'].lower()=='z'and e.get('ctrl')];undos=[e for e in events if e['type']=='beforeinput'and e.get('inputType')=='historyUndo'];(f.case/'owner-history-outcome.json').write_text(json.dumps(dict(before=held,afterUndo=after,afterRedo=restored,keyEvents=keys,nativeUndoEvents=undos),ensure_ascii=False,indent=2))
  if x.mode=='reproduce':
   assert held!=after and keys and keys[-1]['target']['functionToggle']and not keys[-1]['preventedAfter']and undos,(keys,undos,held,after)
   assert next(v for _,v in after if v['kind']=='definition')['text']=='0';f.checked('trusted Ctrl+Z on the function toggle is not consumed when app history cannot apply; browser historyUndo changes the separate new scalar default to0; source/checkpoint remain unchanged')
  else:
   assert held==after==restored and keys[-1]['preventedAfter']and not undos;f.checked('rejected owner function Undo/Redo is consumed and preserves separate scalar input; no native historyUndo is dispatched')
   for selector in ['[data-own-properties-toggle]','.object-icon-edit']:
    target=f.owner().locator(selector);target.focus();expect(target).to_be_focused();mark=len(events)
    for shortcut in ['Control+z','Control+y','Control+Shift+z']:
     f.page.keyboard.press(shortcut);assert phase(selector+' '+shortcut)==held;expect(target).to_be_focused()
    recent=events[mark:];assert not any(e['type']=='beforeinput'and e.get('inputType')in ['historyUndo','historyRedo']for e in recent)
    assert all(e['preventedAfter']for e in recent if e['type']=='keydown'and e.get('key','').lower()in ['z','y'])
   f.checked('property and header icon owner regions consume missing/stale-history Undo/Redo and keep every input and the exact focused button')
   field=f.owner().locator('.object-title-description');base=field.input_value();suffix=' · 텍스트 자체 Undo 유지';field.focus();field.press('End');f.page.keyboard.insert_text(suffix);expect(field).to_have_value(base+suffix);mark=len(events);f.page.keyboard.press('Control+z');expect(field).to_have_value(base);assert d.pending()==held;f.page.keyboard.press('Control+Shift+z');expect(field).to_have_value(base+suffix);f.page.keyboard.press('Control+z');expect(field).to_have_value(base);assert d.pending()==held
   assert any(e['type']=='beforeinput'and e.get('inputType')=='historyUndo'and e['target']['tag']in ['INPUT','TEXTAREA']for e in events[mark:]);f.checked('actual text-focus native Undo/Redo still edits only that text field and restores the original mixed inputs')

  assert not f.errors and not f.external;f.browser.close()
except Exception:
 try:f.page.screenshot(path=str(f.case/'owner-history-failure.png'))
 except Exception:pass
 raise
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
