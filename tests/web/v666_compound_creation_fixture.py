"""An explicitly authored new compound field shares the existing native Save."""
import copy,hashlib,json,time,importlib,sys
_prior=importlib.import_module('v666_header_bodies_fixture'if'--family=body'in sys.argv else'v666_native_header_contracts_fixture')
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
definition_source=f.project/'Leaf2.celem'
if '--registered-fields'in sys.argv:
 import shutil
 root=f.case/'registered-field-types';shutil.copytree(f.project/'registered',root);(root/'Leaf2.celem').write_text('schema External.Fields::Leaf2 {field Count single general long;field Note single general string;}');pack=root/'pack.cpack';pack.write_text(pack.read_text().replace('{','{element Leaf2 schema "Leaf2.celem";',1));f.manifest.write_text(f.manifest.read_text().replace('"registered/pack.cpack"',json.dumps(str(pack))));definition_source=root/'Leaf2.celem'
 snapshot.update({str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts});f.original.update(snapshot)
definition_original=definition_source.read_bytes();new_key='p_0123456789abcdef0123456789abcdef';new_label='새 복합 정보 😀';note='명시한 새 복합 값 · 😀';count='9223372036854775804'
shape=dict(kind='compound',cardinality='single',type='External.Fields::Leaf2'if'--registered-fields'in sys.argv else f.n+'Leaf2')
schema_path=f.project/'FreeInfo.celem';schema_text=schema_path.read_text()
def creation(r):
 view=f.metadata('effective',**r,definitionTypes=True,schemaView=True,validateObjects=True,observeSources=True);assert view['status']=='available';choice=next(row for row in view['definitionTypes']if row['kind']=='compound'and row['id']==shape['type']);assert choice['available'];return dict(type='typed-definition',name=new_key,displayName=new_label,contract=copy.deepcopy(shape),sources=copy.deepcopy(choice['sources']),valueJson=json.dumps(dict(Count=int(count),Note=note),ensure_ascii=False,separators=(',',':')))
def request():
 r=_prior.request();r['changes'].append(creation(r));return r
def expected():
 if 'accepted_description'in globals():_prior.accepted_description=accepted_description
def verify_fields(text):
 parsed=f.metadata('inspect',text=text);before=f.metadata('inspect',text=schema_text);semantic=lambda rows:{name:{k:v for k,v in row.items()if k!='Loc'}for name,row in rows.items()};fields=semantic(parsed['fields']);original=semantic(before['fields']);created=fields.pop(new_key);assert fields==original and created['Type']==shape['type']and created['Kind']=='compound'and created['Cardinality']=='single'and created['Origin']==owner
 values=parsed['values'];assert values['editorFieldName_'+new_key]==new_label and json.loads(values['editorFieldDefault_'+new_key])==dict(Count=int(count),Note=note)
 changed={'editorIcon','editorFieldName_'+new_key,'editorFieldDefault_'+new_key};assert{k:v for k,v in values.items()if k not in changed}=={k:v for k,v in before['values'].items()if k not in changed}
def verify_rows(rows):
 expected();_prior.verify_rows(rows)
 if owner in rows:verify_fields(rows[owner]['draft'])
def verify(checkpoint):
 expected();ids=_prior.verify(checkpoint);verify_fields(next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==owner)['draft']);return ids
def verify_live():
 expected();_prior.verify_live();verify_fields(schema_path.read_text());assert definition_source.read_bytes()==definition_original;f.checked('the explicitly created compound field, exact64 members and both native plans Confirm together; existing field IDs, defaults, reference target, named definitions and unselected CSharp remain unchanged')
def after_contract(index):
 global new_key
 from playwright.sync_api import expect
 _prior.after_contract(index)
 if index!=1:return
 row=d.add(new_label,'compound',shape['type']);selected_type=d.pending();target=row.locator('[data-property-type]');target.press('Control+z');undone=d.pending();assert len(undone)==5 and next(v for _,v in undone if v.get('kind')=='definition').get('definition')is None;target.press('Control+y');assert d.pending()==selected_type;target.press('Control+z');assert d.pending()==undone;target.press('Control+Shift+z');assert d.pending()==selected_type;expect(target).to_be_focused();f.checked('new compound type selection Undo/Redo retains the original new field identity, focus and all native inputs before member editing')
 row=f.owner().locator('[data-definition-key]').last;row.get_by_label('Count 기본값',exact=True).fill(count);row=f.owner().locator('[data-definition-key]').last;row.get_by_label('Note 기본값',exact=True).fill(note);f.idle();held=d.pending();created=[v for _,v in held if v.get('kind')=='definition'];assert len(created)==1;new_key=created[0]['nativeKey'];assert len(held)==5 and created[0]['definition']==shape and json.loads(created[0]['text'])==dict(Count=int(count),Note=note);unchanged();f.checked('original Add and type picker capture one explicit new compound definition with exact source proof and member values after both native editors; five inputs and original checkpoint retained')
 if mode=='reproduce-creation-ui':
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   ids={r['invoke']['requestId']for r in f.traffic[mark:]if r.get('invoke',{}).get('endpoint')=='blueprint'and r['invoke']['input'].get('action')=='applySlots'};replies=[r['result']for r in f.traffic[mark:]if r.get('result',{}).get('requestId')in ids]
   if replies:assert replies[-1]['ok']is False;break
   f.page.wait_for_timeout(20)
  else:raise AssertionError('No observed creation/native Save response')
  assert d.pending()==held and checkpoint.read_bytes()==before;unchanged();f.checked('published original UI rejects only the independently valid new compound/native group, preserving all five inputs and original sources');f.browser.close();raise SystemExit(0)
def validate_history():
 held=d.pending()
 for key in ['Control+z','Control+y','Control+Shift+z']:
  f.owner().locator('[data-own-functions-toggle]').press(key);assert d.pending()==held
 for key in ['Control+z','Control+y','Control+Shift+z']:
  f.owner().locator('[data-own-properties-toggle]').press(key);assert d.pending()==held
 f.checked('after later compound member editing, stale property and function snapshots consume owner hotkeys while preserving all five current inputs and the original new field identity')
