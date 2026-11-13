"""Real consecutive type Undo/Redo retains the same owner, field and mixed inputs."""
import json
import v666_native_schema_contracts_fixture as _prior
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
def _expected():
 if 'accepted_description'in globals():_prior.accepted_description=accepted_description
def verify_rows(rows):_expected();return _prior.verify_rows(rows)
def verify(checkpoint):_expected();return _prior.verify(checkpoint)
def verify_live():_expected();return _prior.verify_live()
def focus():return f.page.evaluate('({tag:document.activeElement?.tagName,window:document.activeElement?.closest(".window")?.dataset.key,path:document.activeElement?.closest("[data-property-path]")?.dataset.propertyPath,draft:document.activeElement?.closest("[data-definition-key]")?.dataset.definitionKey,type:document.activeElement?.matches("[data-property-type]"),icon:document.activeElement?.matches("[data-property-icon]")})')
def after_contract(index):
 _prior.after_contract(index)
 if index!=0:return
 from playwright.sync_api import expect
 target=d.field(field_path).locator('[data-property-type]');planned=d.pending();before=[(key,value)for key,value in planned if value['kind']!='schema-field'];assert len(planned)==4 and len(before)==3;host=f.owner().get_attribute('data-key');target.focus();phases=[]
 for undo,redo in [('Control+z','Control+y'),('Control+z','Control+Shift+z'),('Control+z','Control+y')]:
  f.page.keyboard.press(undo);assert d.pending()==before;first=focus();f.page.keyboard.press(redo);second=focus();phases.append(dict(undo=first,redo=second,keys=[undo,redo],pending=d.pending()));(f.case/'type-focus-chain.json').write_text(json.dumps(dict(host=host,path=field_path,planned=planned,before=before,phases=phases),ensure_ascii=False,indent=2))
  if mode=='reproduce-focus':
   assert first['tag']=='BODY'and second['tag']=='BODY'and d.pending()==before;unchanged();f.checked('published type Undo leaves BODY focused; consecutive page-keyboard Redo is not delivered to the owner; mixed input and original source retained');f.browser.close();raise SystemExit(0)
  assert d.pending()==planned
  for current in [first,second]:assert current['type']and current['window']==host and current['path']==json.dumps(field_path,separators=(',',':')),current
  expect(target).to_be_focused()
 unchanged();f.checked('three trusted consecutive Ctrl+Z/Ctrl+Y/Ctrl+Shift+Z cycles retain exact mixed inputs and restore the same owner field without another focus or pointer action')
