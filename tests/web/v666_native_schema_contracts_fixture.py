"""One existing scalar information field and explicit native ABI/body/caller edits."""
import copy,hashlib,json,time,importlib,sys
_prior=importlib.import_module('v666_header_bodies_fixture'if'--family=body'in sys.argv else'v666_native_header_contracts_fixture')
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
field_name='Scale';field_path=['Scale'];field_before=dict(kind='general',cardinality='single',type='long');field_type='double'
schema_path=f.project/'FreeInfo.celem';schema_text=schema_path.read_text().replace('{','{field Scale single general long;value editorFieldDefault_Scale="7";',1);schema_path.write_text(schema_text);snapshot['FreeInfo.celem']=schema_path.read_bytes();f.original['FreeInfo.celem']=schema_path.read_bytes()
def field_change():return dict(type='schema-field',path=field_path,contract=copy.deepcopy(field_before),schema=owner,schemaHash=hashlib.sha256(schema_text.encode()).hexdigest(),definition=dict(kind='general',cardinality='single',type=field_type),sources=None)
def request():
 r=_prior.request();r['changes'].insert(1,field_change());return r
def verify_field(text):
 parsed=f.metadata('inspect',text=text);before=f.metadata('inspect',text=schema_text);assert parsed['fields'][field_name]['Type']==field_type,parsed['fields'][field_name];assert{k:v for k,v in parsed['values'].items()if k.startswith('editorFieldDefault_')}=={k:v for k,v in before['values'].items()if k.startswith('editorFieldDefault_')};assert{key:value for key,value in parsed['fields'].items()if key!=field_name}=={key:value for key,value in before['fields'].items()if key!=field_name}
def verify_rows(rows):
 if 'accepted_description'in globals():_prior.accepted_description=accepted_description
 _prior.verify_rows(rows)
 if owner in rows:verify_field(rows[owner]['draft'])
def verify(checkpoint):
 if 'accepted_description'in globals():_prior.accepted_description=accepted_description
 ids=_prior.verify(checkpoint);verify_field(next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==owner)['draft']);return ids
def verify_live():
 if 'accepted_description'in globals():_prior.accepted_description=accepted_description
 _prior.verify_live();verify_field(schema_path.read_text());f.checked('explicit scalar field type and both native ABI/body/caller plans Confirm together; field identity/default raw bytes, unrelated fields and source ownership retained')
def after_contract(index):
 _prior.after_contract(index)
 if index==0:
  from playwright.sync_api import expect
  held=d.pending();assert len(held)==3;row=d.field(field_path);row.locator('[data-property-type]').click();picker=f.page.get_by_role('dialog',name='속성 타입 선택',exact=True);expect(picker).to_be_visible();picker.locator('[data-type='+field_type+']').click();f.idle();saved=d.pending();assert len(saved)==4
  target=row.locator('[data-property-type]');target.press('Control+z');assert d.pending()==held
  focus=f.page.evaluate('({tag:document.activeElement?.tagName,window:document.activeElement?.closest(".window")?.dataset.key,html:document.activeElement?.outerHTML.slice(0,300)})');target.press('Control+y');restored=d.pending();(f.case/'property-undo-focus.json').write_text(json.dumps(dict(afterUndo=focus,saved=saved,afterRedo=restored),ensure_ascii=False,indent=2));assert restored==saved;f.checked('original scalar property type picker and owner-focused Undo/Redo retain the owner presentation and explicit native contract/body inputs')
 if index==1 and mode=='reproduce-schema-ui':
  saved=d.pending();assert len(saved)==5;checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   ids={row['invoke']['requestId']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='applySlots'};replies=[row['result']for row in f.traffic[mark:]if row.get('result',{}).get('requestId')in ids]
   if replies:assert replies[-1]['ok']is False;break
   f.page.wait_for_timeout(20)
  else:raise AssertionError('No observed combined field/contract Save response')
  assert d.pending()==saved and checkpoint.read_bytes()==before;unchanged();f.checked('published original Save rejects independently valid field/native plans while preserving all five inputs and the checkpoint/source');f.browser.close();raise SystemExit(0)
