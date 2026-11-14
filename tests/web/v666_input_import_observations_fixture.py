"""Explicit native input changes retain owned and registered helper observations."""
import copy,hashlib,json
import v666_native_inputs_fixture as _input
for _key in dir(_input):
 if not _key.startswith('_'):globals()[_key]=getattr(_input,_key)
local_helper=helper;external_helper='External.InputHelpers::Stable';external_parent_id='External.InputHelpers::Parent';foreign_root=f.case/'registered readonly helper';foreign_root.mkdir();external_manifest=foreign_root/'pack.cpack';external_function=foreign_root/'Stable.celem';external_parent=foreign_root/'Parent.celem'
external_manifest.write_text('pack External.InputHelpers version "1" {element Parent function "Parent.celem";element Stable function "Stable.celem";element StableBody implementation "StableBody.celem";}')
external_parent.write_bytes(('function '+external_parent_id+' (long originalValue) -> long {} // 등록 부모 原文 😀\r\n').encode())
external_function.write_text('function '+external_helper+' (long value) -> long extends '+external_parent_id+' {provide '+external_helper+' with '+external_helper+'Body;}')
(foreign_root/'StableBody.celem').write_text('implementation '+external_helper+'Body for '+external_helper+' (long nativeValue) -> long {body common "Stable.csbody";}')
(foreign_root/'Stable.csbody').write_bytes('// provider 본문은 등록 계약 관측 밖이며 원문 보존\r\nreturn checked(nativeValue+3);\r\n'.encode())
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','dependency External.InputHelpers version "1";registry External.InputHelpers "'+str(external_manifest)+'";registry Confectory.Build.DotNet',1))
for index,fn in enumerate(functions):
 path=f.project/(fn.split('::')[1]+'Body.celem');path.write_text(path.read_text().replace('{','{import '+(local_helper if index==0 else external_helper)+' as StableHelper (long) -> long;',1))
 sources[fn]='return calls.StableHelper.Invoke(checked(nativeAmount+nativeCount)); // 원래 import·본문 😀\n';(f.project/paths[fn]).write_bytes(sources[fn].encode())
selected={fn:'return calls.StableHelper.Invoke(checked(amount.Length'+(''if index==0 else'*2')+'+count)); // 명시 string 본문 😀\n'for index,fn in enumerate(functions)}
original_result=79;edited_result=27
for p in foreign_root.iterdir():p.chmod(0o440)
foreign_root.chmod(0o750)
external_bytes={p:p.read_bytes()for p in foreign_root.iterdir()};external_modes={p:p.stat().st_mode for p in external_bytes};snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_input.snapshot=snapshot;_input._prior.snapshot=snapshot;_input._prior._base.snapshot=snapshot

def unchanged():
 assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items());assert all(p.read_bytes()==raw and p.stat().st_mode==external_modes[p]for p,raw in external_bytes.items())
def request():
 result=_input.request()
 for row in result['changes']:
  for body in row['mapping']['bodies'].values():body['text']=selected[row['id']]
  proof=f.metadata('informationFunctionDependencies',**{k:result[k]for k in ['project','manifest','id','units']},function=row['id'])
  if proof:row['mapping']['dependencies']=proof
 assert 'dependencies'not in result['changes'][0]['mapping']and set(result['changes'][1]['mapping']['dependencies'])=={functions[1]+'Body'}
 return result

def verify_rows(rows):
 _input.verify_rows.__globals__['snapshot']=snapshot;_input.verify_rows.__globals__['selected']=selected;_input.verify_rows(rows)
 merged={v['id']:dict(draft=(f.project/v['path']).read_bytes().decode('utf-8-sig'))for v in f.metadata('describe',project=str(f.manifest))['units']}|rows
 for index,fn in enumerate(functions):
  text=merged[fn+'Body']['draft'];old_text=snapshot[fn.split('::')[1]+'Body.celem'].decode();assert text.split('{',1)[1]==old_text.split('{',1)[1],(text,old_text)
 assert not any(key.startswith('External.')for key in rows)
 for key in [local_helper,local_helper+'Body',local_helper+'Body/body:common']:assert key not in rows,key

def verify(checkpoint):
 rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();ids=rows[owner]['atomicEditGroup'];assert set(functions+[fn+'Body'for fn in functions]+[fn+'Body/body:common'for fn in functions]+[owner,n.caller+'Body',n.caller+'Body/body:common'])<=set(ids);assert not any(key.startswith('External.')for key in rows);receipt=rows[owner]['slotSaveReceipt'];assert set(receipt['nativeBodyDependencies'])=={functions[1]};assert {str(external_manifest),str(external_function),str(external_parent)}<={v['path']for v in receipt['nativeBodyDependencyReads']};assert not any(v['path']in{str(foreign_root/'StableBody.celem'),str(foreign_root/'Stable.csbody')}for v in receipt['nativeBodyDependencyReads']);return ids

def verify_live():
 verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 allowed=set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{str(n.a.info.relative_to(f.project)),'CallerBody.celem','caller.graph.json'}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 assert all(p.read_bytes()==raw and p.stat().st_mode==external_modes[p]for p,raw in external_bytes.items());execute(edited_result,'input-import-observations');f.checked('explicit string bodies and caller literals execute27 through unchanged owned/registered helpers; helper sources, external contracts/parent/provider and permissions preserved')

def after_contract(index):
 _input.after_contract.__globals__['selected']=selected;_input.after_contract(index)
 if mode=='prior-ui'and index==1:
  import time
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));saved=checkpoint.read_bytes();pending=d.pending();mark=len(f.traffic);button=f.owner().locator('[data-element-action=save]');accepted=None
  if not button.is_disabled():
   button.click();deadline=time.monotonic()+90
   while time.monotonic()<deadline:
    ids={v['invoke']['requestId']for v in f.traffic[mark:]if v.get('invoke',{}).get('endpoint')=='blueprint'and v['invoke'].get('input',{}).get('action')=='applySlots'};answers=[v['result']for v in f.traffic[mark:]if v.get('result',{}).get('requestId')in ids and v['result'].get('error',{}).get('code')!='stale_revision']
    if answers:accepted=answers[-1];assert not accepted['ok'],accepted;break
    f.page.wait_for_timeout(20)
   assert accepted is not None
  assert d.pending()==pending and checkpoint.read_bytes()==saved;unchanged();(f.case/'prior-ui-rejection.json').write_text(json.dumps(dict(reply=accepted,saveDisabled=button.is_disabled(),pendingRetained=True,checkpointRetained=True,traffic=f.traffic[-25:]),ensure_ascii=False,indent=2));f.checked('prior UI rejects the coupled input/import Save and preserves both explicit inputs, original checkpoint, external sources and modes');f.browser.close();raise SystemExit(0)
def edit_external(path,suffix):
 path.chmod(0o640)
 try:path.write_bytes(external_bytes[path]+suffix)
 finally:path.chmod(0o440)
def restore_external(path):
 path.chmod(0o640)
 try:path.write_bytes(external_bytes[path])
 finally:path.chmod(0o440)
