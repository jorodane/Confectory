"""Exact private ABI and explicit native return beside an unchanged owned import."""
import copy,hashlib,json,time
import v666_private_return_alias_fixture as _alias
for key in dir(_alias):
 if not key.startswith('_'):globals()[key]=getattr(_alias,key)

helper=f.n+'StablePrivateHelper';helper_paths=['StablePrivateHelper.celem','StablePrivateHelperBody.celem','stable-private-helper.csbody']
helper_texts=[
 'function '+helper+' (long value) -> long {provide '+helper+' with '+helper+'Body;} // 원래 helper 계약 😀\r\n',
 'implementation '+helper+'Body for '+helper+' (long nativeValue) -> long {body common "'+helper_paths[2]+'";} // 원래 helper 별칭 😀\r\n',
 'return checked(nativeValue); // 읽기 의존성 · BOM/CRLF 보존 😀\r\n',
]
for index,(path,text) in enumerate(zip(helper_paths,helper_texts)):(f.project/path).write_bytes((b'\xef\xbb\xbf'if index==2 else b'')+text.encode())
helper_identity={path:dict(dev=(f.project/path).stat().st_dev,ino=(f.project/path).stat().st_ino,mode=(f.project/path).stat().st_mode,mtime=(f.project/path).stat().st_mtime_ns,sha256=hashlib.sha256((f.project/path).read_bytes()).hexdigest())for path in helper_paths}
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element StablePrivateHelper function "'+helper_paths[0]+'";element StablePrivateHelperBody implementation "'+helper_paths[1]+'";registry Confectory.Build.DotNet',1))
fn=functions[1];header=f.project/(fn.split('::')[1]+'Body.celem');header.write_bytes(header.read_bytes().replace(b'{',('{import '+helper+' as StableHelper (long) -> long; // 원래 소유 import 😀\r\n').encode(),1))
sources[fn]='nativeCount=calls.StableHelper.Invoke(5);return checked(nativeAmount+nativeCount); // 원래 별칭·helper·out 😀\r\n'
selected[fn]='nativeCount=calls.StableHelper.Invoke(checked(nativeAmount-5));return nativeCount+0.5; // 직접 작성한 반환·helper 😀\r\n'
(f.project/paths[fn]).write_bytes(b'\xef\xbb\xbf'+sources[fn].encode())
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_alias.snapshot=snapshot
def unchanged():
 _alias.unchanged();assert all((f.project/p).read_bytes()==snapshot[p]and(f.project/p).stat().st_mode==helper_identity[p]['mode']for p in helper_paths)
def request():return _alias.request()
def verify_rows(rows):
 _alias.selected_helpers=selected_helpers;_alias.verify_rows(rows)
 for path in helper_paths:assert(f.project/path).read_bytes()==snapshot[path]
 for id in [helper,helper+'Body',helper+'Body/body:common']:assert id not in rows,id
 # Only the explicitly chosen return signature may change in the native header.
 id=functions[1]+'Body';text=rows.get(id,{}).get('draft',(f.project/(fn.split('::')[1]+'Body.celem')).read_bytes().decode('utf-8-sig'))
 assert text.split('{',1)[1]==snapshot[fn.split('::')[1]+'Body.celem'].decode().split('{',1)[1]
def verify(checkpoint):
 _alias.selected_helpers=selected_helpers;ids=_alias.verify(checkpoint);doc=json.loads(checkpoint.read_text());owner_row=next(row for row in doc['changes']if row['id']==owner);receipt=owner_row['slotSaveReceipt'];assert set(helper_paths)<=set(receipt['readGuards']);assert not any(key in receipt for key in ['nativeBodyDependencies','nativeBodyDependencyReads','nativeTypeProofs','nativeTypeReads']);verify_rows({row['id']:row for row in doc['changes']});return ids
def verify_live():
 _alias.selected_helpers=selected_helpers;_alias.verify_live();verify_rows({})
 for path,v in helper_identity.items():
  st=(f.project/path).stat();assert(st.st_dev,st.st_ino,st.st_mode,st.st_mtime_ns)==(v['dev'],v['ino'],v['mode'],v['mtime']),path
 f.checked('unchanged owned helper function/header/BOM-CRLF body remain read dependencies; native import alias and non-signature header bytes, inode/mode/mtime preserved')
def after_contract(index):
 old_mode=_alias.mode;_alias.mode='normal'
 try:_alias.after_contract(index)
 finally:_alias.mode=old_mode
 if mode!='reproduce-ui'or index!=1:return
 from playwright.sync_api import expect
 cp=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=cp.read_bytes();pending=d.pending();mark=len(f.traffic)
 f.page.evaluate('()=>{globalThis.importSaveClicks=[];document.addEventListener("click",e=>{if(e.target.closest("[data-element-action=save]"))importSaveClicks.push({trusted:e.isTrusted});},true)}');button=f.owner().locator('[data-element-action=save]');expect(button).to_be_enabled();button.click();deadline=time.monotonic()+60;replies=[]
 while time.monotonic()<deadline:
  ids={v['invoke']['requestId']for v in f.traffic[mark:]if v.get('invoke',{}).get('input',{}).get('action')=='applySlots'};replies=[v['result']for v in f.traffic[mark:]if v.get('result',{}).get('requestId')in ids]
  if replies:assert replies[-1]['ok']is False;break
  f.page.wait_for_timeout(25)
 else:raise AssertionError('Prior import Save terminal response missing')
 clicks=f.page.evaluate('()=>importSaveClicks');assert clicks and all(v['trusted']for v in clicks);assert cp.read_bytes()==before and d.pending()==pending;unchanged();f.page.screenshot(path=str(f.case/'prior-owned-import-save.png'));(f.case/'prior-owned-import-save.json').write_text(json.dumps(dict(replies=replies,clicks=clicks,inputRetained=True,checkpointRetained=True,helperPaths=helper_paths),ensure_ascii=False,indent=2));f.checked('intact prior package rejects one trusted private/return/import Save while preserving both inputs, checkpoint, helper/source bytes and permissions');f.browser.close();raise SystemExit(0)
