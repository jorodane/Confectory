"""Explicit CSharp value-to-ref call-site and the caller's existing ref storage."""
import copy,json,re
import v666_native_value_ref_fixture as _base
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)
first,second=functions;p=f.project/(first.split('::')[1]+'Body.celem');p.write_text(p.read_text().replace('{','{import '+second+' as Second (long,long) -> long;',1))
sources[first]='nativeCount=calls.Second.Invoke(nativeAmount,nativeCount);return nativeCount; // 原래 값 호출 😀\n'
selected[first]='nativeCount=calls.Second.Invoke(nativeAmount,ref nativeCount);return nativeCount; // 직접 작성한 ref 호출 😀\n'
(f.project/paths[first]).write_bytes(sources[first].encode());snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_base.snapshot=snapshot

def request():return _base.request()
def unchanged():assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items())
def verify_rows(rows):
 _base.verify_rows(rows);merged={v['id']:dict(draft=(f.project/v['path']).read_bytes().decode('utf-8-sig'))for v in f.metadata('describe',project=str(f.manifest))['units']}|rows
 for index,fn in enumerate(functions):
  before=snapshot[fn.split('::')[1]+'Body.celem'].decode().split('{',1)[1];after=merged[fn+'Body']['draft'].split('{',1)[1]
  if index==0:
   before=re.sub(r'import [^;]+ as Second \([^;]+;','',before);after=re.sub(r'import [^;]+ as Second \([^;]+;','',after);assert re.search(r'as Second \(long[^;]*ref long[^;]*\) -> long;',merged[fn+'Body']['draft'])
  assert before==after,(before,after)

def verify(checkpoint):
 rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();ids=rows[owner]['atomicEditGroup'];assert set(functions+[fn+'Body'for fn in functions]+[fn+'Body/body:common'for fn in functions]+[owner,n.caller+'Body',n.caller+'Body/body:common'])<=set(ids);return ids

def verify_live():
 verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 allowed={'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{str(n.a.info.relative_to(f.project)),'CallerBody.celem','caller.graph.json',paths[first]}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'native-role-chain');f.checked('actual native value-to-ref signatures and directly authored ref call execute79 and mutate the existing caller cell to79; B BOM/CRLF body, helper, input bindings and caller ABI remain exact')

def after_contract(index):
 from playwright.sync_api import expect
 selector='[data-inline-method="'+functions[index]+'"] [data-function-edit], [data-inline-method="'+functions[index]+'"] [data-function-write-direct]';held=d.pending();dialog=f.page.locator('[role=dialog]:has([data-code-source])')
 def open_editor():
  f.owner().locator(selector).click();expect(f.page.locator('[role=dialog]:has([data-code-source]), [role=dialog]:has([data-information-body])')).to_be_visible();choice=f.page.locator('[data-information-body="'+functions[index]+'Body/body:common"]')
  if choice.count():choice.click()
  expect(dialog).to_be_visible();field=dialog.locator('[data-code-source]');before=sources[functions[index]].replace('\r\n','\n');assert before in field.input_value();field.evaluate("el=>{el.focus();el.setSelectionRange(el.value.indexOf('(')+1,el.value.indexOf(')'));}");f.page.keyboard.insert_text('long nativeAmount, ref long nativeCount')
  if index==0:
   field.evaluate('(el,text)=>{el.focus();const p=el.value.indexOf(text);el.setSelectionRange(p,p+text.length);}',before);f.page.keyboard.insert_text(selected[functions[index]])
  f.idle()
 open_editor();dialog.locator('[data-code-cancel]').click();assert d.pending()==held;open_editor();dialog.locator('[data-code-save]').click();mapping=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(mapping).to_be_visible()
 for field in mapping.locator('[data-abi-input=amount]').all():field.select_option('pin:amount')
 for field in mapping.locator('[data-abi-input=count]').all():field.select_option('pin:count')
 for field in mapping.locator('[data-abi-output=return]').all():field.select_option('return')
 mapping.locator('[data-abi-remap-accept]').click();expect(mapping).to_have_count(0);f.idle();saved=d.pending()
 for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+z')
 assert d.pending()==held
 for _ in range(2):f.owner().locator('[data-own-functions-toggle]').press('Control+y')
 assert d.pending()==saved

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
  assert d.pending()==pending and checkpoint.read_bytes()==saved;unchanged();(f.case/'prior-ui-rejection.json').write_text(json.dumps(dict(reply=accepted,saveDisabled=button.is_disabled(),pendingRetained=True,checkpointRetained=True,traffic=f.traffic[-25:]),ensure_ascii=False,indent=2));f.checked('prior UI rejects the coupled value-to-ref/import Save and preserves both explicit inputs, original checkpoint, external sources and modes');f.browser.close();raise SystemExit(0)

