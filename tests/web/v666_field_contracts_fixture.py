"""Existing nominal property contracts share one explicit native body/ABI Save."""
import copy,hashlib,json,time,importlib,sys
_prior=importlib.import_module('v666_header_bodies_fixture'if'--family=body'in sys.argv else'v666_native_header_contracts_fixture')
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
definition_source=f.project/'Leaf2.celem'
if '--registered-fields'in sys.argv:
 import shutil
 root=f.case/'registered-field-types';shutil.copytree(f.project/'registered',root);(root/'Leaf2.celem').write_text('schema External.Fields::Leaf2 {field Count single general long;field Note single general string;}');pack=root/'pack.cpack';pack.write_text(pack.read_text().replace('{','{element Leaf2 schema "Leaf2.celem";',1));f.manifest.write_text(f.manifest.read_text().replace('"registered/pack.cpack"',json.dumps(str(pack))));definition_source=root/'Leaf2.celem'
 snapshot.update({str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts});f.original.update(snapshot)
definition_original=definition_source.read_bytes();note='새 멤버 값 · 9223372036854775806 😀'
schema_path=f.project/'FreeInfo.celem';schema_text=schema_path.read_text()
fields=dict(Tree=(dict(kind='compound',cardinality='single',type=f.n+'Leaf'),dict(kind='compound',cardinality='single',type=('External.Fields::Leaf2'if'--registered-fields'in sys.argv else f.n+'Leaf2'))),Peer=(dict(kind='reference',cardinality='single',type=f.n+'LeafChild'),dict(kind='reference',cardinality='single',type=f.n+'Leaf')))
def field_changes(r):
 view=f.metadata('effective',**r,definitionTypes=True,schemaView=True,validateObjects=True,observeSources=True);assert view['status']=='available';catalogue=view['definitionTypes'];rows=[]
 for name,(before,after)in fields.items():
  choice=next(row for row in catalogue if row['kind']==after['kind']and row['id']==after['type']);assert choice['available'];rows.append(dict(type='schema-field',path=[name],contract=copy.deepcopy(before),schema=owner,schemaHash=hashlib.sha256(schema_text.encode()).hexdigest(),definition=copy.deepcopy(after),sources=copy.deepcopy(choice['sources'])))
 return rows
def request():
 r=_prior.request();r['changes']+=field_changes(r);r['changes'].append(dict(type='data',path=['Tree'],contract=copy.deepcopy(fields['Tree'][0]),valueJson=json.dumps(dict(Count=9223372036854775805,Note=note),ensure_ascii=False,separators=(',',':'))));return r
def expected():
 if 'accepted_description'in globals():_prior.accepted_description=accepted_description
def verify_fields(text):
 parsed=f.metadata('inspect',text=text);before=f.metadata('inspect',text=schema_text)
 semantic=lambda rows:{name:{k:v for k,v in row.items()if k!='Loc'}for name,row in rows.items()}
 actual=semantic(parsed['fields']);wanted=semantic(before['fields'])
 for name,(_,shape)in fields.items():wanted[name]['Type']=shape['type']
 assert actual==wanted,(actual,wanted)
 assert json.loads(parsed['values']['editorFieldDefault_Tree'])==dict(Count=9223372036854775805,Note=note)
 assert {k:v for k,v in parsed['values'].items()if k not in ['editorIcon','editorFieldDefault_Tree']}=={k:v for k,v in before['values'].items()if k not in ['editorIcon','editorFieldDefault_Tree']}
def verify_rows(rows):
 expected();_prior.verify_rows(rows)
 if owner in rows:verify_fields(rows[owner]['draft'])
def verify(checkpoint):
 expected();ids=_prior.verify(checkpoint);verify_fields(next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==owner)['draft']);return ids
def verify_live():
 expected();_prior.verify_live();verify_fields(schema_path.read_text());assert definition_source.read_bytes()==definition_original;f.checked('existing compound/reference field IDs and precise defaults are retained while their explicit type contracts and both native plans Confirm; original named definitions, target and unselected CSharp remain untouched')
def after_contract(index):
 from playwright.sync_api import expect
 _prior.after_contract(index)
 if index!=1:return
 for name,(_,shape)in fields.items():
  d.choose(d.field([name]).locator('[data-property-type]'),shape['kind'],shape['type'])
  if name=='Tree':
   field=d.field(['Tree','Note']).locator('[data-property-value]')
   if not field.is_visible():d.field(['Tree']).locator(':scope>.property-content-box>.object-property-default>.property-expand').click()
   field.fill(note);f.idle()
 held=d.pending();assert len(held)==7,held;unchanged();f.checked('the original type picker captures two explicit nominal field contracts with their existing source proofs after both native editors; seven inputs and original checkpoint/source retained')
 if mode=='reproduce-fields-ui':
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   ids={row['invoke']['requestId']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='applySlots'};replies=[row['result']for row in f.traffic[mark:]if row.get('result',{}).get('requestId')in ids]
   if replies:assert replies[-1]['ok']is False;break
   f.page.wait_for_timeout(20)
  else:raise AssertionError('No observed field/native Save response')
  assert d.pending()==held and checkpoint.read_bytes()==before;unchanged();f.checked('published original UI rejects only the independently valid field/native combination and preserves all seven inputs, original definitions and source');f.browser.close();raise SystemExit(0)
def validate_history():
 held=d.pending()
 for key in ['Control+z','Control+y','Control+Shift+z']:
  f.owner().locator('[data-own-functions-toggle]').press(key);assert d.pending()==held
 target=d.field(['Peer']).locator('[data-property-type]');target.press('Control+z');undone=d.pending();assert len(undone)==6;target.press('Control+y');assert d.pending()==held
 target.press('Control+z');assert d.pending()==undone;target.press('Control+Shift+z');assert d.pending()==held
 f.checked('field type Undo/Redo restores the original path focus and only the last explicit field contract; stale function history preserves both later fields and all native inputs')
