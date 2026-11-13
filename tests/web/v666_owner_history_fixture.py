"""The originally failing order: both native editors, then scalar structure/value edits."""
import copy,json,sys
import v666_scalar_owner_contracts_fixture as _prior
from v666_owner_history_tools import Monitor
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
monitor=Monitor(sys.modules[__name__]);original_setup=f.setup
def setup():
 page=original_setup();monitor.capture(page);return page
f.setup=setup
def expected():
 _prior.new_key=new_key
 if 'accepted_description'in globals():_prior.accepted_description=accepted_description
def verify_rows(rows):expected();return _prior.verify_rows(rows)
def verify(checkpoint):expected();return _prior.verify(checkpoint)
def verify_live():expected();return _prior.verify_live()
def after_contract(index):
 global new_key,last_inputs
 from playwright.sync_api import expect
 _prior._prior.after_contract(index)
 if index!=1:return
 row=d.field(['Scale']);d.choose(row.locator('[data-property-type]'),'general','double');d.field(['Gauge']).locator('[data-property-value]').fill(gauge_value);d.field(['Gauge']).locator('[data-property-name]').fill(gauge_label);f.idle();d.field(['Gauge']).locator('[data-property-icon]').click();dialog=f.page.get_by_role('dialog',name='Gauge 아이콘 편집',exact=True);expect(dialog).to_be_visible();dialog.locator('[data-icon-choice="'+glyph+'"]').click();dialog.get_by_role('button',name='적용',exact=True).click();f.idle();d.field(['Retired']).locator('[data-schema-remove]').click();expect(d.field(['Retired'])).to_have_count(0);created=d.add(new_label,'general','long');created.locator('[data-property-value]').fill(new_value);f.idle();new_key=next(v['nativeKey']for _,v in d.pending()if v.get('kind')=='definition');saved=d.pending();assert len(saved)==10,saved;x=next(v for _,v in saved if v['kind']=='definition');assert x['definition']==scalar and x['text']==new_value
 _prior.new_key=new_key;last_inputs=copy.deepcopy(saved);unchanged();f.checked('both explicit native editors precede scalar structure/default/presentation edits, retaining the original ten-cell failing order')
def validate_history():
 held=d.pending();assert len(held)==10;monitor.guarded(held);monitor.native_text(held);monitor.composing(held)
def history_during_save():
 # Do not force a presentation RPC before the actual keys. A held successful
 # response can settle through the normal receipt lookup while observing it.
 from playwright.sync_api import expect
 late=f.owner().locator('.object-title-description').input_value();mark=len(monitor.events);tested=[]
 for selector in ['[data-own-functions-toggle]','[data-own-properties-toggle]','.object-icon-edit']:
  button=f.owner().locator(selector)
  if not button.is_enabled():continue
  button.focus();expect(button).to_be_focused();f.page.keyboard.press('Control+z');tested.append(selector)
 pending=monitor.phase('held response after trusted owner keys');recent=monitor.events[mark:];keys=[e for e in recent if e['type']=='keydown'and e.get('key')=='z'];assert tested and len(keys)==len(tested)and all(e['trusted']and e['preventedAfter']for e in keys);assert any(e['busyAtCapture']for e in keys),keys;assert not any(e['type']=='beforeinput'and e.get('inputType')in ['historyUndo','historyRedo']for e in recent)
 expected=copy.deepcopy(last_inputs);description_key=next(k for k,v in expected if v['kind']=='description')
 for _,value in expected:
  if value['kind']=='description':value['text']=late
 if len(pending)==10:assert pending==expected;settled=False
 else:
  assert len(pending)==1 and pending[0][0]==description_key and pending[0][1]['kind']=='description'and pending[0][1]['text']==late;checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));verify(checkpoint);settled=True
 unchanged();(f.case/'busy-owner-history.json').write_text(json.dumps(dict(keys=keys,regions=tested,pending=pending,receiptSettledWhileOriginalResponseHeld=settled),ensure_ascii=False,indent=2));f.checked('trusted owner keys include an actually busy dispatch, keep late text and captured Save intact, and never invoke another input history; receipt lookup may legitimately clear the captured rows during observation')
