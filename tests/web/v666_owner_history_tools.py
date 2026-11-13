"""Observe event dispatch and browser history without changing application state."""
import json
from playwright.sync_api import expect
class Monitor:
 def __init__(self,x):self.x=x;self.f=x.f;self.d=x.d;self.events=[];self.phases=[]
 def capture(self,page):
  def record(source,event):
   self.events.append(event);(self.f.case/'owner-history-events.json').write_text(json.dumps(self.events,ensure_ascii=False,indent=2))
  page.expose_binding('recordOwnerHistoryBoundary',record)
  page.evaluate('''()=>{const node=el=>el?{tag:el.tagName,window:el.closest?.('.window')?.dataset.key,property:el.closest?.('[data-property-path]')?.dataset.propertyPath,draft:el.closest?.('[data-definition-key]')?.dataset.definitionKey,name:el.getAttribute?.('aria-label'),functionToggle:el.matches?.('[data-own-functions-toggle]'),propertyToggle:el.matches?.('[data-own-properties-toggle]'),headerIcon:el.matches?.('.object-icon-edit'),value:'value'in el?el.value:null}:null;for(const type of ['keydown','keyup','beforeinput','input','focusin'])document.addEventListener(type,e=>{if(type==='focusin'||type==='beforeinput'||type==='input'||e.ctrlKey||e.metaKey||e.key==='Control'){const initial={type,key:e.key,code:e.code,ctrl:e.ctrlKey,meta:e.metaKey,composing:e.isComposing,inputType:e.inputType,trusted:e.isTrusted,target:node(e.target),active:node(document.activeElement),busyAtCapture:!!document.querySelector(".brand")?.disabled,preventedAtCapture:e.defaultPrevented};setTimeout(()=>window.recordOwnerHistoryBoundary({...initial,preventedAfter:e.defaultPrevented,activeAfter:node(document.activeElement)}),0);}},true)}''')
 def phase(self,name):
  self.f.page.wait_for_timeout(1);pending=self.d.pending();self.phases.append(dict(name=name,pending=pending,focus=self.f.page.evaluate('({tag:document.activeElement?.tagName,html:document.activeElement?.outerHTML.slice(0,450)})')));(self.f.case/'owner-history-phases.json').write_text(json.dumps(self.phases,ensure_ascii=False,indent=2));return pending
 def guarded(self,held,label='rejected',busy=False):
  f=self.f;tested=[]
  for selector in ['[data-own-functions-toggle]','[data-own-properties-toggle]','.object-icon-edit']:
   target=f.owner().locator(selector)
   if busy and not target.is_enabled():continue
   target.focus();expect(target).to_be_focused();mark=len(self.events)
   for shortcut in ['Control+z','Control+y','Control+Shift+z']:
    f.page.keyboard.press(shortcut);assert self.phase(label+' '+selector+' '+shortcut)==held;expect(target).to_be_focused()
   recent=self.events[mark:];assert not any(e['type']=='beforeinput'and e.get('inputType')in ['historyUndo','historyRedo']for e in recent)
   keys=[e for e in recent if e['type']=='keydown'and e.get('key','').lower()in ['z','y']];assert len(keys)==3 and all(e['trusted']and e['preventedAfter']and e['target']['tag']=='BUTTON'for e in keys),keys;tested.append(selector)
  assert tested;self.x.unchanged();f.checked(label+' owner Undo/Redo consumes rejected snapshots, retains every input and the focused button, and never invokes browser history in a different field; regions='+','.join(tested))
 def native_text(self,held):
  f=self.f;field=f.owner().locator('.object-title-description');base=field.input_value();suffix=' · 텍스트 자체 Undo 유지';field.focus();field.press('End');f.page.keyboard.insert_text(suffix);expect(field).to_have_value(base+suffix);mark=len(self.events);f.page.keyboard.press('Control+z');expect(field).to_have_value(base);assert self.d.pending()==held;f.page.keyboard.press('Control+Shift+z');expect(field).to_have_value(base+suffix);f.page.keyboard.press('Control+z');expect(field).to_have_value(base);assert self.phase('native text restored')==held
  assert any(e['type']=='beforeinput'and e.get('inputType')=='historyUndo'and not e['preventedAfter']and e['target']['tag']in ['INPUT','TEXTAREA']for e in self.events[mark:]);f.checked('actual text-focus native Undo and Ctrl+Shift+Z Redo remain local to the text field; the existing global Ctrl+Y Yogi shortcut is unchanged')
 def composing(self,held):
  # Ctrl+Y is the existing global Yogi shortcut. Use Ctrl+Z/Shift+Z to
  # isolate the owned composing guard without changing that global policy.
  for selector in ['[data-own-functions-toggle]','[data-own-properties-toggle]','.object-icon-edit']:
   for redo in [False,True]:
    outcome=self.f.owner().locator(selector).evaluate('(el,shiftKey)=>{const e=new KeyboardEvent("keydown",{key:"z",ctrlKey:true,shiftKey,isComposing:true,bubbles:true,cancelable:true});el.dispatchEvent(e);return {prevented:e.defaultPrevented}}',redo);assert not outcome['prevented'];assert self.phase('synthetic composing '+selector+' '+str(redo))==held
  self.f.checked('synthetic composing Ctrl+Z/Ctrl+Shift+Z keeps its original unconsumed guard and does not mutate input; physical OS IME and a global Ctrl+Y policy change are not claimed')
