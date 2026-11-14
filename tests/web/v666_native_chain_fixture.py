"""Two explicitly retyped native functions form an explicitly authored call chain through an owned import."""
import copy,json,hashlib,re
import v666_input_import_observations_fixture as _base
import v666_native_inputs_fixture as _leaf
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)
first,second=functions;header=first.split('::')[1]+'Body.celem';p=f.project/header;p.write_text(p.read_text().replace('{','{import '+second+' as Second (long,long) -> long;',1))
sources[first]='return calls.StableHelper.Invoke(calls.Second.Invoke(nativeAmount,nativeCount)); // 原文 C# import 😀\n';selected=copy.deepcopy(selected);selected[first]='return calls.StableHelper.Invoke(calls.Second.Invoke(amount,count)); // 직접 작성한 새 string 호출 😀\n';(f.project/paths[first]).write_bytes(sources[first].encode());original_result=85;edited_result=34
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_base.snapshot=snapshot;_leaf.snapshot=snapshot;_leaf._prior.snapshot=snapshot;_leaf._prior._base.snapshot=snapshot

def request():
 r=_base.request()
 for row in r['changes']:
  for plan in row['mapping']['bodies'].values():plan['text']=selected[row['id']]
 return r

def unchanged():_base.unchanged()
def verify_rows(rows):
 _leaf.verify_rows.__globals__['selected']=selected;_leaf.verify_rows(rows)
 merged={v['id']:dict(draft=(f.project/v['path']).read_bytes().decode('utf-8-sig'))for v in f.metadata('describe',project=str(f.manifest))['units']}|rows
 for index,fn in enumerate(functions):
  old=snapshot[fn.split('::')[1]+'Body.celem'].decode().split('{',1)[1];current=merged[fn+'Body']['draft'].split('{',1)[1]
  if index==0:old=re.sub(r'import [^;]+ as Second \([^;]+;','',old);current=re.sub(r'import [^;]+ as Second \([^;]+;','',current);assert 'as Second (string' in merged[fn+'Body']['draft']
  assert old==current,(old,current)
 assert not any(key.startswith('External.')for key in rows)
def verify(checkpoint):
 rows={v['id']:v for v in json.loads(checkpoint.read_text())['changes']};verify_rows(rows);unchanged();ids=rows[owner]['atomicEditGroup'];assert set(functions+[fn+'Body'for fn in functions]+[fn+'Body/body:common'for fn in functions]+[owner,n.caller+'Body',n.caller+'Body/body:common'])<=set(ids);receipt=rows[owner]['slotSaveReceipt'];assert set(receipt['nativeBodyDependencies'])=={second};assert {str(external_manifest),str(external_function),str(external_parent)}<={v['path']for v in receipt['nativeBodyDependencyReads']};return ids

def verify_live():
 verify_rows({});allowed=set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{str(n.a.info.relative_to(f.project)),'CallerBody.celem','caller.graph.json'}
 for path,raw in snapshot.items():
  if path not in allowed:assert(f.project/path).read_bytes()==raw,path
 assert all(p.read_bytes()==raw and p.stat().st_mode==external_modes[p]for p,raw in external_bytes.items());execute(edited_result,'native-chain');f.checked('joint string contracts, original aliases/import edges and two authored CSharp bodies execute34; helper/external sources and permissions remain exact')

def after_contract(index):
 from playwright.sync_api import expect
 mapping=f.page.get_by_role('dialog',name='호출 계약 갱신',exact=True);expect(mapping).to_be_visible()
 for target in mapping.locator('section[data-abi-target]').all():target.locator('[data-abi-input=amount]').select_option('value');target.locator('[data-abi-value=amount]').fill(texts[index])
 mapping.locator('[data-abi-disconnect=amount]').select_option('disconnect');mapping.locator('[data-abi-remap-accept]').click();expect(mapping).to_have_count(0);f.idle();held=d.pending();dialog=f.page.locator('[role=dialog]:has([data-code-source])');selector='[data-inline-method="'+functions[index]+'"] [data-function-edit], [data-inline-method="'+functions[index]+'"] [data-function-write-direct]'
 def open_editor():
  f.owner().locator(selector).click();expect(f.page.locator('[role=dialog]:has([data-code-source]), [role=dialog]:has([data-information-body])')).to_be_visible();choice=f.page.locator('[data-information-body="'+functions[index]+'Body/body:common"]')
  if choice.count():choice.click()
  expect(dialog).to_be_visible();field=dialog.locator('[data-code-source]');assert sources[functions[index]]in field.input_value();field.evaluate('(el,text)=>{el.focus();const p=el.value.indexOf(text);el.setSelectionRange(p,p+text.length);}',sources[functions[index]]);f.page.keyboard.insert_text(selected[functions[index]]);f.idle()
 open_editor();dialog.locator('[data-code-cancel]').click();assert d.pending()==held;open_editor();dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==held;f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved
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
