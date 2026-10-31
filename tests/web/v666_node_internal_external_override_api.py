"""Registered ancestry receipts, stale parents and final read-only file CAS."""
import copy,json,subprocess,sys,uuid
import v666_node_internal_external_override_fixture as n
x=n.x;f=n.f
def metadata(request):
 done=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),text=True,capture_output=True,env=f.env,check=True);return json.loads(done.stdout)
try:
 x.build('registered-override-before',7);f.start(0);catalog=x.rpc('featureBodies',feature=x.feature);assert catalog['declaredImplementation']==x.impl and not catalog['unresolvedParents'] and any(v['id']==x.graph and v['bodyOrigin']==x.impl for v in catalog['rows']);data=n.read();assert data['diagnostics']['state']=='source-ready' and data['nodeFlowDependencyHash'];before=x.checkpoint();n.original()
 owner=(f.project/'FlowBody.celem').read_text();query={'operation':'blueprintOverrideContracts','action':'read','project':str(x.manifest),'id':x.impl,'text':owner,'target':'common'};
 # The CLI metadata envelope is the same one used by the existing fixture.
 proof=f.metadata('blueprintOverrideContracts',**{k:v for k,v in query.items() if k!='operation'});snapshot=proof['snapshot'];assert proof['bodyReads']==0 and proof['readOnly'];assert not any(p['path'].endswith('.csbody') or p['path'].endswith('.node.json') for p in snapshot['observations']);assert n.parent in snapshot['ancestors']
 for name in ['missing','tampered','extra','path','owner']:
  bad=copy.deepcopy(snapshot)
  if name=='missing':bad=None
  elif name=='tampered':bad['observations'][0]['hash']='0'*64
  elif name=='extra':bad['ancestors']['Other.Pack::Parent']=copy.deepcopy(bad['ancestors'][n.parent])
  elif name=='path':bad['observations'][0]['path']=str(f.case/'not registered')
  else:bad['ownerHash']='0'*64
  result=metadata({**query,'action':'verify','snapshot':bad});assert not result['ok'],name;(f.case/('registered-receipt-'+name+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2));assert x.checkpoint()==before;n.original()
 for mode in ['missing-file','unreadable','undeclared']:
  held=n.parent_file.with_suffix('.retained')
  try:
   if mode=='missing-file':n.parent_file.rename(held)
   elif mode=='unreadable':n.parent_file.chmod(0)
   else:x.manifest.write_bytes(n.physical[x.manifest].replace(b'dependency External.Ancestors version "1";',b''))
   invalid=metadata({**query,'action':'verify','snapshot':snapshot});assert not invalid['ok'],mode
  finally:
   if mode=='missing-file':held.rename(n.parent_file)
   elif mode=='unreadable':n.parent_file.chmod(0o440)
   else:x.manifest.write_bytes(n.physical[x.manifest])
  assert x.checkpoint()==before;n.original()
 f.checked('등록된 부모·manifest·함수 헤더만 관측하고 누락/변조/다른 경로·소유 영수증은 거절한다')
 req=n.request(data,source='return amount+8;')
 for name in ['missing','tampered']:
  bad=copy.deepcopy(req)
  if name=='missing':bad['edits'][0]['definition']['binding'].pop('dependencyHash')
  else:bad['edits'][0]['definition']['binding']['dependencyHash']='0'*64
  x.rpc('authorBatch',False,**bad);assert x.checkpoint()==before;n.original()
 n.change_parent(b'\n// peer before Save\n');x.rpc('authorBatch',False,**req);assert x.checkpoint()==before and n.parent_file.read_bytes()!=n.physical[n.parent_file];n.restore_parent();n.original();f.checked('원래 등록 의존성 binding 누락/변조·Save 전 부모 변경은 전체 후보를 거절한다')
 applied,state=x.any_invoke('blueprint',{'action':'authorBatch',**req});(f.case/'first-save.json').write_text(json.dumps([applied,state],ensure_ascii=False,indent=2));assert applied['ok'],state;saved=x.checkpoint();n.original();f.stop();f.start(1);assert x.rpc('settledAuthorBatch',**req)['settled'];x.rpc('authorBatch',**req);assert x.checkpoint()==saved;n.original();f.checked('등록 부모 영수증·원자 그룹은 cold와 동일 요청 재시도에서 그대로 복원된다')
 # The same pure checkpoint validator is called by Restore; it does not rebase
 # saved evidence onto mutable external files.
 for name in ['missing','tampered']:
  saved_doc=json.loads(next(iter(saved.values())).decode());units={u['id']:u for u in saved_doc['changes']};origin=units[x.graph]['nodeFlowOrigin']
  if name=='missing':origin.pop('registeredAncestry')
  else:origin['registeredAncestry']['ownerHash']='0'*64
  invalid=metadata({'operation':'blueprintOverrideContracts','action':'validateGroup','units':units});assert not invalid['ok'];assert x.checkpoint()==saved;n.original()
 f.checked('cold 체크포인트의 등록 부모 영수증 누락/변조는 복원 검증에서 거절한다')
 ready=x.rpc('read',id=n.child);ids=ready['reviewIds'];f.invoke('reviewGroup',{'ids':[n.child]},False)
 review=f.invoke('reviewGroup',{'target':'portable','ids':ids});review_checkpoint=x.checkpoint();n.change_parent(b'\n// peer after Review\n');reply,state=x.any_invoke('confirmGroup',{'token':review['state']['review']['token'],'ids':ids});assert not reply.get('result',{}).get('sourceConfirmed');(f.case/'parent-confirm-rejection.json').write_text(json.dumps([reply,state],ensure_ascii=False,indent=2));assert (f.project/'Flow.graph.json').read_bytes()==n.physical[f.project/'Flow.graph.json'],'physical graph changed';assert x.checkpoint()==review_checkpoint,'checkpoint changed after rejected Confirm';f.stop();f.start(2);restored=x.rpc('read',id=n.child);assert next(v for v in restored['nodes'] if v['id']=='body')['source']=='return amount+8;';rejected,rejected_state=x.any_invoke('reviewGroup',{'target':'portable','ids':ids});assert not rejected['ok'] or rejected_state.get('review',{}).get('status')!='ready';n.restore_parent();n.original();f.checked('Review 후 부모 변경은 Confirm과 재시작 후 재검토에서 거절하며 저장된 입력·상대 변경을 보존한다')
 review=f.invoke('reviewGroup',{'target':'portable','ids':ids});f.invoke('confirmGroup',{'token':review['state']['review']['token'],'ids':ids});n.ancestors_original();x.build('registered-override-after',11);f.checked('현재 등록·권한만 사용해 자기 소유 자식만 반영하고 외부 부모 원문·모드·공개 계약을 보존한다')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
