"""Retain an already assigned owned copy while editing its unchanged native callees."""
import copy,json,sys,time
from pathlib import Path
_requested=sys.argv[3]if len(sys.argv)>3 else'normal'
if len(sys.argv)>3:sys.argv[3]='leaf'
import v666_body_imports_fixture as _prior
if len(sys.argv)>3:sys.argv[3]=_requested
for _key in dir(_prior):
 if not _key.startswith('_'):globals()[_key]=getattr(_prior,_key)
_base=_prior._base;mode=_requested;_base.mode=mode
original_result=40;edited_result=20
copy_owner=f.n+'CallerHost';copy_id=f.n+'CallerOwnedCopy';donor_impl=n.caller+'Body'
for local,kind,text in [('CallerRules','module','module '+f.n+'CallerRules {require '+n.caller+' (long,long) -> long;}'),('CallerHost','object','object '+copy_owner+' {module '+f.n+'CallerRules;}')]:
 (f.project/(local+'.celem')).write_text(text);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+local+' '+kind+' "'+local+'.celem";registry Confectory.Build.DotNet',1))
prepared=f.metadata('implementationCopy',project=str(f.manifest),action='prepare',feature=n.caller,source=donor_impl,target='common',implementation=copy_id,owner=copy_owner,ownerText=(f.project/'CallerHost.celem').read_text())
retained_header='CallerOwnedCopy.celem';retained_graph=prepared['graphPath'];retained_file='Main.csbody';assignment_file='CallerHost.celem';copy_graph=prepared['graph']
assert not prepared['records'],prepared['records']
(f.project/retained_header).write_bytes(prepared['implementation'].replace('\n','\r\n').encode());(f.project/assignment_file).write_bytes(prepared['owner'].replace('\n','\r\n').encode());f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element CallerOwnedCopy implementation "'+retained_header+'";registry Confectory.Build.DotNet',1))
(f.project/retained_graph).parent.mkdir(parents=True,exist_ok=True);(f.project/retained_graph).write_bytes((json.dumps(copy_graph,ensure_ascii=False,indent=2)+'\n').replace('\n','\r\n').encode())
# The existing direct default provider executes the assigned local copy. Its donor
# remains registered and byte-identical as a separate read-only source identity.
p=f.project/'Caller.celem';text=p.read_text();assert 'with '+donor_impl in text;text=text.replace('with '+donor_impl,'with '+copy_id);p.write_text(text)
original_graph=copy.deepcopy(copy_graph);original_graph.pop('copySource')
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_base.snapshot=snapshot
_request=_base.request

def request():
 r=_request()
 for row in r['changes']:
  proofs=f.metadata('informationFunctionCopies',project=str(f.manifest),manifest=r['manifest'],id=owner,function=row['id'],units=r['units']);assert set(proofs)=={copy_id+'/body:common'};row['mapping']['copies']=proofs
 return r

def verify_rows(rows):
 merged={row['id']:{'draft':(f.project/row['path']).read_bytes().decode()}for row in f.metadata('describe',project=str(f.manifest))['units']}|rows
 for id,path in [(donor_impl,'CallerBody.celem'),(donor_impl+'/body:common','caller.graph.json'),(copy_id,retained_header),(copy_id+'/body:common',retained_graph),(copy_owner,assignment_file),(n.caller,'Caller.celem')]:assert merged[id]['draft']==snapshot[path].decode(),id
 assert json.loads(merged[copy_id+'/body:common']['draft'])==copy_graph
 for fn in functions:
  assert n.canonical(f.metadata('inspect',text=merged[fn]['draft'])['signature'])==old
  assert merged[fn+'Body']['draft']==snapshot[fn.split('::')[1]+'Body.celem'].decode()
  assert merged[fn+'Body/body:common']['draft']==selected[fn]
_base.verify_rows=verify_rows

def verify(checkpoint):return _base.verify(checkpoint)
def verify_live():
 verify_rows({})
 if 'accepted_description'in globals():assert f.metadata('inspect',text=n.a.info.read_text())['description']==accepted_description
 for path,raw in snapshot.items():
  if path not in set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{str(n.a.info.relative_to(f.project))}:assert(f.project/path).read_bytes()==raw,path
 execute(edited_result,'retained-owned-copy');f.checked('actual edited program20 uses the existing default owned copy, preserving donor/copy provenance, assignment, contracts, IDs and exact original bytes')
def caller_arguments(index):return copy.deepcopy(graph['nodes'][index]['arguments'])
def caller_exits():return copy.deepcopy(graph['exits'])
def after_contract(index):
 from playwright.sync_api import expect
 fn=functions[index];held=d.pending();selector='[data-inline-method="'+fn+'"] [data-function-edit], [data-inline-method="'+fn+'"] [data-function-write-direct]'
 def open_editor():
  f.owner().locator(selector).click();chooser=f.page.get_by_role('dialog',name='구현 선택',exact=True)
  if chooser.count():chooser.locator('[data-information-body="'+fn+'Body/body:common"]').click();expect(chooser).to_have_count(0)
  dialog=f.page.locator('[role=dialog]:has([data-code-source])');expect(dialog).to_be_visible();return dialog
 def fill(dialog):
  field=dialog.locator('[data-code-source]');assert sources[fn]in field.input_value();field.evaluate('(el,text)=>{el.focus();const i=el.value.indexOf(text);if(i<0)throw Error("Original native body absent");el.setSelectionRange(i,i+text.length);}',sources[fn]);f.page.keyboard.insert_text(selected[fn]);f.idle()
 dialog=open_editor();fill(dialog);dialog.locator('[data-code-cancel]').click();assert d.pending()==held
 dialog=open_editor();fill(dialog);f.page.screenshot(path=str(f.case/('native-copy-caller-'+str(index)+'.png')));dialog.locator('[data-code-save]').click();expect(dialog).to_have_count(0);f.idle();saved=d.pending();f.owner().locator('[data-own-functions-toggle]').press('Control+z');assert d.pending()==held;f.owner().locator('[data-own-functions-toggle]').press('Control+y');assert d.pending()==saved
 if index==1 and mode=='reproduce-ui':
  checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();mark=len(f.traffic);f.owner().locator('[data-element-action=save]').click();deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   ids={row['invoke']['requestId']for row in f.traffic[mark:]if row.get('invoke',{}).get('endpoint')=='blueprint'and row['invoke']['input'].get('action')=='applySlots'};replies=[row['result']for row in f.traffic[mark:]if row.get('result',{}).get('requestId')in ids]
   if replies:assert replies[-1]['ok']is False;break
   f.page.wait_for_timeout(20)
  else:raise AssertionError('No observed joint native Save result')
  assert d.pending()==saved and checkpoint.read_bytes()==baseline;unchanged();f.checked('existing chooser edits only native callees; grouped same-contract Save rejects while retaining existing copy/donor/assignment and both inputs');f.browser.close();raise SystemExit(0)
