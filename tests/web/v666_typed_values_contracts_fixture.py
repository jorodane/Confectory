"""Existing typed values, including registered compound data, share one native Save."""
import copy,hashlib,json,time,importlib,sys
_prior=importlib.import_module('v666_header_bodies_fixture'if'--family=body'in sys.argv else'v666_native_header_contracts_fixture')
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
scalar=dict(kind='general',cardinality='single',type='long');members=[dict(id='ten',name='처음'),dict(id='twenty',name='다음')];numbers=dict(ten=10,twenty=20)
extra={'RefTarget2':('object','object '+f.n+'RefTarget2 {use schema '+f.n+'LeafChild;data Count=9;}'),'NativeAltBody':('implementation','implementation '+f.n+'NativeAltBody for '+f.n+'Native (long input) -> long {body common "NativeAlt.csbody";}'),'ValueMode':('enum','enum '+f.n+'ValueMode {value editorEnumProfile="nominal-members-native-v2";value editorEnumValues='+json.dumps(json.dumps(members,ensure_ascii=False))+';value editorEnumNumbers='+json.dumps(json.dumps(numbers))+';}')}
for key,(kind,text)in extra.items():(f.project/(key+'.celem')).write_text(text)
external_definition=f.project/'registered/Leaf.celem'
if '--outside-values'in sys.argv:
 import shutil
 external_root=f.case/'registered-values';shutil.copytree(f.project/'registered',external_root);external_definition=external_root/'Leaf.celem';f.manifest.write_text(f.manifest.read_text().replace('"registered/pack.cpack"',json.dumps(str(external_root/'pack.cpack'))))
external_original=external_definition.read_bytes()
(f.project/'NativeAlt.csbody').write_bytes(b'return checked(input+4); // distinct pre-existing fixture provider\r\n');f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet',''.join('element '+key+' '+kind+' "'+key+'.celem";'for key,(kind,_)in extra.items())+'registry Confectory.Build.DotNet',1))
def default(name,value):return 'value editorFieldDefault_'+name+'='+json.dumps(json.dumps(value,ensure_ascii=False,separators=(',',':')))+';'
schema_path=f.project/'FreeInfo.celem';schema_text=schema_path.read_text().replace('{','{field Samples multiple general long;field ExternalTree single compound External.Fields::Leaf;field Handler single function '+f.n+'Native;field Mode single enum '+f.n+'ValueMode;'+default('Samples',[9223372036854775806,9223372036854775805])+default('ExternalTree',dict(HP=9223372036854775803))+default('Handler',{'$ref':f.n+'NativeBody'})+default('Mode','ten'),1);schema_path.write_text(schema_text);snapshot.update({str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts});f.original.update(snapshot)
expected_values=dict(Tree=dict(Count=9223372036854775801),ExternalTree=dict(HP=9223372036854775802),Samples=[9223372036854775806,9223372036854775804],Peer={'$ref':f.n+'RefTarget2'},Handler={'$ref':f.n+'NativeAltBody'},Mode='twenty')
contracts=dict(Tree=dict(kind='compound',cardinality='single',type=f.n+'Leaf'),ExternalTree=dict(kind='compound',cardinality='single',type='External.Fields::Leaf'),Samples=dict(kind='general',cardinality='multiple',type='long'),Peer=dict(kind='reference',cardinality='single',type=f.n+'LeafChild'),Handler=dict(kind='function',cardinality='single',type=f.n+'Native'),Mode=dict(kind='enum',cardinality='single',type=f.n+'ValueMode'))
def value_changes():return [dict(type='data',path=[name],contract=copy.deepcopy(contracts[name]),valueJson=json.dumps(value,ensure_ascii=False,separators=(',',':')))for name,value in expected_values.items()]
def request():
 r=_prior.request();r['changes']+=value_changes();return r
def expected():
 if 'accepted_description'in globals():_prior.accepted_description=accepted_description
def verify_values(text):
 parsed=f.metadata('inspect',text=text);before=f.metadata('inspect',text=schema_text);assert {n:{k:v for k,v in row.items()if k!='Loc'}for n,row in parsed['fields'].items()}=={n:{k:v for k,v in row.items()if k!='Loc'}for n,row in before['fields'].items()};changed={'editorFieldDefault_'+name for name in expected_values}|{'editorIcon'};assert{k:v for k,v in parsed['values'].items()if k not in changed}=={k:v for k,v in before['values'].items()if k not in changed}
 for name,value in expected_values.items():assert json.loads(parsed['values']['editorFieldDefault_'+name])==value,(name,parsed['values'])
def verify_rows(rows):
 expected();_prior.verify_rows(rows)
 if owner in rows:verify_values(rows[owner]['draft'])
def verify(checkpoint):
 expected();ids=_prior.verify(checkpoint);verify_values(next(row for row in json.loads(checkpoint.read_text())['changes']if row['id']==owner)['draft']);return ids
def verify_live():
 expected();_prior.verify_live();verify_values(schema_path.read_text());assert external_definition.read_bytes()==external_original;f.checked('compound/list/reference/function/enum defaults Confirm with both explicit native plans, retaining field contracts, exact integers, registered type sources and unselected implementation bytes')
def expanded(path,child):
 from playwright.sync_api import expect
 target=child()
 if not target.is_visible():d.field(path).locator(':scope>.property-content-box>.object-property-default>.property-expand').click()
 expect(child()).to_be_visible();return child()
def after_contract(index):
 from playwright.sync_api import expect
 f.page.set_viewport_size({'width':2300,'height':3000});_prior.after_contract(index)
 if index!=1:return
 for path,value in [(['Tree','Count'],'9223372036854775801'),(['ExternalTree','HP'],'9223372036854775802')]:expanded(path[:1],lambda path=path:d.field(path).locator('[data-property-value]')).fill(value)
 expanded(['Samples'],lambda:d.field(['Samples']).locator('[data-value-path=\'["Samples",1]\']')).fill('9223372036854775804')
 for name,target in [('Peer',f.n+'RefTarget2'),('Handler',f.n+'NativeAltBody')]:d.target(d.field([name]),target)
 d.field(['Mode']).locator('.property-reference-value').click();choices=f.page.get_by_role('listbox',name='Mode 종류 선택',exact=True);expect(choices).to_be_visible();choices.locator('[data-enum-choice=twenty]').click();f.idle();held=d.pending();assert len(held)==10,held;unchanged();f.checked('original compound/list and target/enum value controls capture six typed defaults after both explicit native editors without changing any field definition or external source')
 if mode=='reproduce-values-ui':
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   ids={row['invoke']['requestId']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='applySlots'};replies=[row['result']for row in f.traffic[mark:]if row.get('result',{}).get('requestId')in ids]
   if replies:assert replies[-1]['ok']is False;break
   f.page.wait_for_timeout(20)
  else:raise AssertionError('No mixed typed/native Save response')
  assert d.pending()==held and checkpoint.read_bytes()==before;unchanged();f.checked('published original UI rejects only the combined independently valid typed/native candidate; all ten inputs, checkpoint and original sources remain intact');f.browser.close();raise SystemExit(0)

def validate_history():
 held=d.pending()
 # Later property edits invalidate the old function snapshot; its rejection
 # must consume the hotkey without reaching another input's native history.
 for key in ['Control+z','Control+y','Control+Shift+z']:
  f.owner().locator('[data-own-functions-toggle]').press(key);assert d.pending()==held
 f.checked('stale function history preserves all six later typed values and both native plans without native text-history fallback')
 button=f.owner().locator('[data-own-properties-toggle]');button.press('Control+z');undone=d.pending();assert len(undone)==9 and all(value.get('path')!=['Mode']for _,value in undone)
 button.press('Control+y');assert d.pending()==held
 button.press('Control+z');assert d.pending()==undone
 button.press('Control+Shift+z');assert d.pending()==held
 f.checked('typed value Undo/Redo removes and restores only the last enum choice while preserving the other five values and both native plans')
