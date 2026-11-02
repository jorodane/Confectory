"""Public return body candidate, ancestry receipts, checkpoint and final CAS."""
import copy,json,subprocess
import v666_root_execution_override_fixture as c
f=c.f;x=c.x
try:
 c.build('override-before');provider=f.project/'Flow.celem';provider.write_text(provider.read_text().replace('with '+c.impl+';', 'with '+c.borrower+';'))
 try:c.build('borrowed-runtime-before')
 finally:provider.write_bytes(c.physical[provider])
 c.original();f.start(0);f.invoke('select',{'id':c.feature});f.invoke('saveDraft',{});d=c.read();assert d['diagnostics']['state']=='source-ready' and d['publicBodyReturnsAvailable'] and d['rootExecution'] is None;req=c.request(d);before=c.checkpoint()
 for name in ['unknown-branch','contract-edit','incomplete-exit','stale-proof']:
  bad=copy.deepcopy(req)
  if name=='unknown-branch':bad['edits'][0]['definition']['exits']['yes']={'executionBranch':'invented'}
  elif name=='contract-edit':bad['edits'][0]['definition']['branches']=[]
  elif name=='incomplete-exit':bad['edits'][0]['definition']['edges'].append(x.edge('choose','exit:missing','case:negative'))
  else:bad['sourceProof']=bad['sourceProof'].replace(d['sources'][0]['hash'],'0'*64)
  c.rpc('authorBatch',False,**bad);assert c.checkpoint()==before;c.original()
 # A parent's body cannot be selected through the child locator.
 c.rpc('read',False,id=c.borrower+'/body:common');c.original()
 c.mutate_parent()
 try:c.rpc('authorBatch',False,**req);assert c.checkpoint()==before
 finally:c.restore_parent()
 assert c.rpc('authorBatch',**req)['checkpointSaved'];assert c.rpc('settledAuthorBatch',**req)['settled'];c.original();cp=c.checkpoint()
 snapshot=json.loads(next(iter(cp.values())));units={r['id']:r for r in snapshot['changes']};origin=units[c.graph]['publicBodyOrigin'];assert origin['version']==1
 guard=f.metadata('blueprintOverrideContracts',action='verifyGroup',project=str(x.manifest),units=units);assert {'Flow.celem','FlowBody.celem','Flow.graph.json','Flow.node.json'}<={r['path'] for r in guard['checks']};assert bool(guard['reads'])==c.external
 for mode in ['missing-origin','missing-source','changed-source','changed-node','invalid-branch']+(['missing-external','tampered-external'] if c.external else []):
  bad=copy.deepcopy(units);g=bad[c.graph]
  if mode=='missing-origin':g.pop('publicBodyOrigin')
  elif mode=='missing-source':g['publicBodyOrigin']['sources'].pop(c.feature)
  elif mode=='changed-source':bad[c.feature]['draft']+=' '
  elif mode=='missing-external':g['publicBodyOrigin']['registeredAncestry']=None
  elif mode=='tampered-external':g['publicBodyOrigin']['registeredAncestry']['observations'][0]['hash']='0'*64
  else:
   doc=json.loads(g['draft'])
   if mode=='changed-node':doc['nodes'][0]['intent']='tampered'
   else:doc['exits']['yes']={'executionBranch':'invalid'}
   g['draft']=json.dumps(doc)
  proc=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'blueprintOverrideContracts','action':'verifyGroup','project':str(x.manifest),'units':bad}),capture_output=True,text=True,env=f.env,check=True);assert json.loads(proc.stdout)['ok'] is False,(mode,proc.stdout)
 f.stop();f.start(1);f.invoke('select',{'id':c.feature});assert c.checkpoint()==cp and c.rpc('settledAuthorBatch',**req)['settled'];assert c.read()['diagnostics']['state']=='source-ready';c.original()
 # Repeated edit retains the original source closure and external receipt.
 assert c.rpc('authorBatch',**c.request(c.read(),c.plan(c.read(),'none')))['checkpointSaved'];c.original();f.checked('자식 소유 반환·기존 분기/None·반복/cold/receipt·불완전/변조/부모 변경 거절은 원계약과 원문을 보존한다')
 ids=c.read()['reviewIds'];f.invoke('reviewGroup',{'ids':[c.graph],'target':'portable'},False);review=f.invoke('reviewGroup',{'ids':ids,'target':'portable'});assert not review['state']['review'].get('errors');c.mutate_parent();result=f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']})['result']['result'];assert not result['sourceConfirmed']
 assert (f.project/c.graph_path).read_bytes()==c.physical[f.project/c.graph_path];c.restore_parent();f.checked('Review 뒤 부모 변경은 최종 CAS에서 전체 미적용하며 기존 입력과 부모 원문을 보존한다')
 f.stop();f.start(2);f.invoke('select',{'id':c.feature});ids=c.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids,'target':'portable'});result=f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']})['result']['result'];assert result['sourceConfirmed'];c.originals_retained();c.build('override-after',True,'none');f.checked('자식 소유 그래프만 기존 None을 반환하며 out 발행과 기존 다음 줄을 실제 실행하고 부모/원문/공개 계약을 보존한다')
 f.stop();f.start(3);f.invoke('select',{'id':c.feature});d=c.read();c.rpc('authorBatch',**c.request(d,c.plan(d,'success')));f.stop();f.start(4);f.invoke('select',{'id':c.feature});ids=c.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids,'target':'portable'});assert f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']})['result']['result']['sourceConfirmed'];c.originals_retained();c.build('override-repeat');f.checked('확정 후 재진입·반복 저장도 기존 성공 ID와 모든 소유/실행 계약을 유지한다')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('M12_OVERRIDE_API '+str(f.case),flush=True)
