"""Direct scalar owner edits share the existing explicit native body/ABI Save."""
import copy,hashlib,json,time,importlib,sys
_prior=importlib.import_module('v666_header_bodies_fixture'if'--family=body'in sys.argv else'v666_native_header_contracts_fixture')
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
scalar=dict(kind='general',cardinality='single',type='long');new_key='p_0123456789abcdef0123456789abcdef';new_label='새 수량 😀';gauge_label='현재 수량 😀';new_value='9223372036854775804';gauge_value='9223372036854775805';glyph='★'
schema_path=f.project/'FreeInfo.celem';schema_text=schema_path.read_text().replace('{','{field Scale single general long;value editorFieldDefault_Scale="7";field Gauge single general long;value editorFieldDefault_Gauge="9223372036854775806";field Retired single general long;value editorFieldDefault_Retired="6";value editorFieldName_Retired="삭제할 수량";value editorFieldIcon_Retired="★";',1);schema_path.write_text(schema_text);snapshot['FreeInfo.celem']=schema_path.read_bytes();f.original['FreeInfo.celem']=schema_path.read_bytes()
def owned(kind,field,**extra):return dict(type=kind,path=[field],contract=copy.deepcopy(scalar),schema=owner,schemaHash=hashlib.sha256(schema_text.encode()).hexdigest(),**extra)
def owner_changes():return [owned('schema-field','Scale',definition=dict(kind='general',cardinality='single',type='double'),sources=None),dict(type='data',path=['Gauge'],contract=copy.deepcopy(scalar),valueJson=gauge_value),owned('schema-name','Gauge',name=gauge_label),owned('schema-icon','Gauge',text=glyph),owned('schema-remove','Retired'),dict(type='typed-definition',name=new_key,displayName=new_label,contract=copy.deepcopy(scalar),sources=None,valueJson=new_value)]
def request():
 r=_prior.request();r['changes']+=owner_changes();return r

def semantic_fields(fields):return {name:{k:v for k,v in field.items()if k!='Loc'}for name,field in fields.items()}
def verify_fields(text):
 parsed=f.metadata('inspect',text=text);before=f.metadata('inspect',text=schema_text)
 fields=semantic_fields(parsed['fields']);original=semantic_fields(before['fields']);values=parsed['values']
 assert fields['Scale']['Type']=='double'
 assert 'Retired'not in fields and new_key in fields and fields[new_key]['Type']=='long'
 assert values['editorFieldDefault_Gauge']==gauge_value and values['editorFieldDefault_'+new_key]==new_value
 assert values['editorFieldName_Gauge']==gauge_label and values['editorFieldIcon_Gauge']==glyph and values['editorFieldName_'+new_key]==new_label
 assert all(key not in values for key in ['editorFieldDefault_Retired','editorFieldName_Retired','editorFieldIcon_Retired'])
 assert {k:v for k,v in fields.items()if k not in ['Scale','Retired',new_key]}=={k:v for k,v in original.items()if k not in ['Scale','Retired']}
 changed={'editorFieldDefault_Gauge','editorFieldName_Gauge','editorFieldIcon_Gauge','editorFieldDefault_'+new_key,'editorFieldName_'+new_key,'editorFieldDefault_Retired','editorFieldName_Retired','editorFieldIcon_Retired','editorIcon'}
 assert {k:v for k,v in values.items()if k not in changed}=={k:v for k,v in before['values'].items()if k not in changed}

def expected():
 if 'accepted_description'in globals():_prior.accepted_description=accepted_description
def verify_rows(rows):
 expected();_prior.verify_rows(rows)
 if owner in rows:verify_fields(rows[owner]['draft'])
def verify(checkpoint):
 expected();ids=_prior.verify(checkpoint);verify_fields(next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==owner)['draft']);return ids
def verify_live():
 expected();_prior.verify_live();verify_fields(schema_path.read_text());f.checked('scalar creation/removal, label/icon/default and type edits Confirm with both explicit native plans; original unrelated fields, precise integers and source ownership retained')
def after_contract(index):
 global new_key
 from playwright.sync_api import expect
 _prior.after_contract(index)
 if index==0:
  row=d.field(['Scale']);d.choose(row.locator('[data-property-type]'),'general','double');d.field(['Gauge']).locator('[data-property-value]').fill(gauge_value);d.field(['Gauge']).locator('[data-property-name]').fill(gauge_label);f.idle();d.field(['Gauge']).locator('[data-property-icon]').click();dialog=f.page.get_by_role('dialog',name='Gauge 아이콘 편집',exact=True);expect(dialog).to_be_visible();dialog.locator('[data-icon-choice="'+glyph+'"]').click();dialog.get_by_role('button',name='적용',exact=True).click();f.idle();d.field(['Retired']).locator('[data-schema-remove]').click();expect(d.field(['Retired'])).to_have_count(0);created=d.add(new_label,'general','long');created.locator('[data-property-value]').fill(new_value);f.idle();new_key=next(v['nativeKey']for _,v in d.pending()if v.get('kind')=='definition');saved=d.pending();assert len(saved)==9,saved;x=next(v for _,v in saved if v['kind']=='definition');assert x['definition']==scalar and x['text']==new_value
  f.checked('scalar structure/default/presentation cells are captured before the second native function edit; property history is not treated as function history')
  return
 saved=d.pending();assert len(saved)==10;unchanged();f.checked('original scalar controls retain ten explicit property/presentation/native inputs before one Save; source and checkpoint unchanged')
 if mode=='reproduce-owner-ui':
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   ids={row['invoke']['requestId']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='applySlots'};replies=[row['result']for row in f.traffic[mark:]if row.get('result',{}).get('requestId')in ids]
   if replies:assert replies[-1]['ok']is False;break
   f.page.wait_for_timeout(20)
  else:raise AssertionError('No mixed owner/native Save response')
  assert d.pending()==saved and checkpoint.read_bytes()==before;unchanged();f.checked('published original UI rejects only the combined scalar/native candidate and retains all ten inputs and original checkpoint/source');f.browser.close();raise SystemExit(0)
