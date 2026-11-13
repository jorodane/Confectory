"""Existing readonly registered imports in a same-contract owned body group."""
import copy,hashlib,json,subprocess
import v666_body_imports_fixture as _prior
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
local_helper=helper;helper='External.BodyHelpers::Stable';parent='External.BodyHelpers::Parent';foreign_root=f.case/'registered readonly helper';foreign_root.mkdir();external_manifest=foreign_root/'pack.cpack';external_function=foreign_root/'Stable.celem';external_parent=foreign_root/'Parent.celem'
external_manifest.write_text('pack External.BodyHelpers version "1" {element Parent function "Parent.celem";element Stable function "Stable.celem";element StableBody implementation "StableBody.celem";}')
external_parent.write_bytes(('function '+parent+' (long originalValue) -> long {} // 등록 부모 原文 😀\r\n').encode())
external_function.write_text('function '+helper+' (long value) -> long extends '+parent+' {provide '+helper+' with '+helper+'Body;}')
(foreign_root/'StableBody.celem').write_text('implementation '+helper+'Body for '+helper+' (long nativeValue) -> long {body common "Stable.csbody";}')
(foreign_root/'Stable.csbody').write_bytes('// 등록 provider 본문은 읽기 계약 proof 밖이며 원문 보존\r\nreturn checked(nativeValue+3);\r\n'.encode())
manifest=f.manifest.read_text()
for name,kind in [('StableBodyHelper','function'),('StableBodyHelperBody','implementation')]:manifest=manifest.replace('element '+name+' '+kind+' "'+name+'.celem";','')
f.manifest.write_text(manifest.replace('registry Confectory.Build.DotNet','dependency External.BodyHelpers version "1";registry External.BodyHelpers "'+str(external_manifest)+'";registry Confectory.Build.DotNet',1))
for fn in functions:
 p=f.project/(fn.split('::')[1]+'Body.celem');p.write_text(p.read_text().replace(local_helper+' as StableHelper',helper+' as StableHelper'))
for p in foreign_root.iterdir():p.chmod(0o440)
foreign_root.chmod(0o750)
external_bytes={p:p.read_bytes()for p in foreign_root.iterdir()};external_modes={p:p.stat().st_mode for p in external_bytes};snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_prior.snapshot=snapshot;_prior._base.snapshot=snapshot
original_result=46;edited_result=26;retained_header='CallerBody.celem';retained_file='caller.graph.json';retained_graph='caller.graph.json'
def unchanged():
 assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items());assert all(p.read_bytes()==raw and p.stat().st_mode==external_modes[p]for p,raw in external_bytes.items())
def request():
 r=_prior.request()
 for row in r['changes']:
  proof=f.metadata('informationFunctionDependencies',**{k:r[k]for k in ['project','manifest','id','units']},function=row['id']);assert set(proof)=={row['id']+'Body'};row['mapping']['dependencies']=proof
 return r
def verify(checkpoint):
 ids=_prior.verify(checkpoint);rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};assert not any(id.startswith('External.')for id in rows);receipt=rows[owner]['slotSaveReceipt'];assert set(receipt['nativeBodyDependencies'])==set(functions);assert {str(external_manifest),str(external_function),str(external_parent)}<={row['path']for row in receipt['nativeBodyDependencyReads']};return ids
def verify_live():
 _prior.verify_live();
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 assert all(p.read_bytes()==raw and p.stat().st_mode==external_modes[p]for p,raw in external_bytes.items());f.checked('registered helper and parent remain readonly/original; actual result26 uses both explicit bodies without external writes')
def edit_external(path,suffix):
 path.chmod(0o640)
 try:path.write_bytes(external_bytes[path]+suffix)
 finally:path.chmod(0o440)
def restore_external(path):
 path.chmod(0o640)
 try:path.write_bytes(external_bytes[path])
 finally:path.chmod(0o440)
