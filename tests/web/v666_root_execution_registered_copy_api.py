"""Owner-bound public return edits retain donor, contract, storage and provenance."""
import copy,json,subprocess
import v666_root_execution_registered_copy_fixture as c
f=c.f;x=c.x
try:
 c.build('copy-before');f.start(0);f.invoke('select',{'id':c.owner});f.invoke('saveDraft',{});d=c.read();assert d['diagnostics']['state']=='source-ready' and d['executionExitMode'] and d['slotContext']['checkpointPlain'] and d['slotContext']['copySource'];assert d['rootExecution'] is None;assert [b['id'] for b in d['publicExecutionBranches']]==['success','failure'];req=c.request(d);before=c.checkpoint();c.original()
 for name in ['unknown-branch','contract-edit','incomplete-exit','stale-proof','wrong-owner']:
  bad=copy.deepcopy(req)
  if name=='unknown-branch':bad['edits'][0]['definition']['exits']['yes']={'executionBranch':'invented'}
  elif name=='contract-edit':bad['edits'][0]['definition']['branches']=[]
  elif name=='incomplete-exit':bad['edits'][0]['definition']['edges'].append({'from':'choose','port':'case:negative','to':'exit:missing'})
  elif name=='stale-proof':bad['sourceProof']=bad['sourceProof'].replace(d['sources'][0]['hash'],'0'*64)
  else:bad['ownerHash']='0'*64
  c.rpc('authorBatch',False,**bad);assert c.checkpoint()==before;c.original()
 f.checked('공개 계약·copy 소유/출처는 읽기 전용이며 기존 분기 ID만 선택한다. 잘못된 계약/분기/연결/소유 증거는 전체 미적용한다')
 guard=c.function_file;c.mutate_parent();c.rpc('authorBatch',False,**req);c.restore_parent();assert c.checkpoint()==before;c.original()
 saved=c.rpc('authorBatch',**req);assert saved['settled'] and saved['checkpointSaved'];assert c.rpc('settledAuthorBatch',**req)['settled'];c.original();cp=c.checkpoint();f.stop();f.start(1);f.invoke('select',{'id':c.owner});assert c.checkpoint()==cp and c.rpc('settledAuthorBatch',**req)['settled'];assert c.read()['diagnostics']['state']=='source-ready';c.original();f.checked('copy 반환·배정 소유자와 원문 closure는 한 후보/checkpoint CAS로 저장하고 cold/receipt 재시도는 중복 저장하지 않는다')
 snapshot=json.loads(next(iter(cp.values())));(f.case/'saved-before-review.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2));units={row['id']:row for row in snapshot['changes']};checks=f.metadata('blueprintPublicCopyReturnGuards',namespace=f.n[:-2],units=units)['checks'];assert {'FreeInfo.celem','M12Copy.celem',c.graph_path}<={row['path'] for row in checks}
 closure=f.metadata('blueprintOverrideContracts',action='verifyGroup',project=str(x.manifest),units=units);assert len(closure['reads'])==2;assert all(row['path'] not in [u['path'] for u in units.values()] for row in closure['reads']);assert c.feature not in units and 'publicBodyOrigin' not in units[c.graph]
 for mode in ['missing-external','tampered-external','foreign-path','raw-bom-change']:
  bad=copy.deepcopy(units)
  try:
   if mode=='missing-external':bad[c.graph]['authorSaveReceipt'].pop('registeredFunction')
   elif mode=='tampered-external':bad[c.graph]['authorSaveReceipt']['registeredFunction']['observations'][0]['hash']='0'*64
   elif mode=='foreign-path':bad[c.graph]['authorSaveReceipt']['registeredFunction']['observations'][0]['path']=str(f.case/'unregistered')
   else:c.mutate_parent(b'\xef\xbb\xbf')
   out=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'blueprintOverrideContracts','action':'verifyGroup','project':str(x.manifest),'units':bad}),capture_output=True,text=True,env=f.env,check=True);assert not json.loads(out.stdout)['ok'],mode
  finally:c.restore_parent()
 f.checked('외부 계약은 쓰기 그룹에 포함하지 않고 두 헤더의 원시 SHA/경로 영수증을 최종 typed CAS에 결합한다')
 for kind in ['missing-group','missing-receipt','missing-source','source-hash','owner-hash','provenance','missing-external','tampered-external','contract-text']:
  bad=copy.deepcopy(units);g=bad[c.graph]
  if kind=='missing-group':
   for row in bad.values():row.pop('atomicEditGroup',None)
  elif kind=='missing-receipt':g.pop('authorSaveReceipt')
  elif kind=='missing-source':g['authorSaveReceipt']['sources'].pop(c.impl)
  elif kind=='source-hash':g['authorSaveReceipt']['sources'][c.impl]['hash']='0'*64
  elif kind=='owner-hash':g['authorSaveReceipt']['slotRequest']['ownerHash']='0'*64
  elif kind=='provenance':doc=json.loads(g['draft']);doc['copySource']['implementation']=f.n+'Other';g['draft']=json.dumps(doc)
  elif kind=='missing-external':g['authorSaveReceipt'].pop('registeredFunction')
  elif kind=='tampered-external':g['authorSaveReceipt']['registeredFunction']['ownerHash']='0'*64
  else:g['authorSaveReceipt']['registeredFunction']['text']+=' '
  r=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'blueprintPublicCopyReturnGuards','namespace':f.n[:-2],'units':bad}),capture_output=True,text=True,env=f.env,check=True);reply=json.loads(r.stdout);assert reply['ok'] is False and reply['code']=='AUTHORING',reply
 c.original();assert c.checkpoint()==cp;f.checked('저장된 읽기 receipt의 누락·hash/출처·공개 계약 변조는 복원과 동일한 순수 guard에서 거절한다')
 ids=c.read()['reviewIds'];f.invoke('reviewGroup',{'ids':[c.graph]},False);review=f.invoke('reviewGroup',{'ids':ids,'target':'portable'});assert not review['state']['review'].get('errors');c.mutate_parent();result=f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']})['result']['result'];assert not result['sourceConfirmed'];c.restore_parent();c.original();f.checked('부분 Review와 Review 이후 공개 계약 원문 경합을 거절하고 donor·현재 입력을 보존한다')
 f.stop();f.start(2);f.invoke('select',{'id':c.owner});ids=c.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids,'target':'portable'});result=f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']})['result']['result'];assert result['sourceConfirmed'];c.originals_retained();assert json.loads((f.project/c.graph_path).read_text())['copySource']==c.provenance;c.build('copy-after',True);f.checked('copy만 기존 실패 분기를 반환하고 호출자가 이미 발행한 int out과 다음 줄을 실행하며 donor/C#·ID·provenance를 보존한다')
 f.stop();f.start(3);f.invoke('select',{'id':c.owner});d=c.read();req=c.request(d,c.plan(d,'success'));c.rpc('authorBatch',**req);f.stop();f.start(4);f.invoke('select',{'id':c.owner});ids=c.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids,'target':'portable'});f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']});c.originals_retained();c.build('copy-repeat');f.checked('Confirm 뒤 반복 반환 편집·cold·재저장·실제 실행도 원래 공개 ID와 소유 배정을 유지한다')
 print('M12_REGISTERED_COPY_API '+str(f.case),flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
