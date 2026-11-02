"""First Save publishes copy assignment and existing branch returns atomically."""
import copy,json,subprocess,uuid,sys
registered='--registered-creating' in sys.argv
if registered:import v666_root_execution_registered_creating_fixture as c
else:import v666_root_execution_copy_creating_fixture as c
f=c.f
try:
 c.build('creating-before');f.start(0);f.invoke('select',{'id':c.owner});f.invoke('saveDraft',{});selected=c.selection();d=selected['preview'];assert d['id'] is None and d['executionExitMode'] and [b['id'] for b in d['publicExecutionBranches']]==['success','failure'];request=c.row(selected);before=c.checkpoint();c.original()
 for kind in ['unknown','contract','shape','nested','deleted','duplicate']:
  bad=copy.deepcopy(request);edit=bad['edits'][0];plan=json.loads(edit['text'])
  if kind=='unknown':plan['exits']['yes']['executionBranch']='invented'
  elif kind=='contract':plan['branches']=[]
  elif kind=='shape':plan['edges'][0]['extra']='ignored'
  elif kind=='nested':edit['node']='choose/$branches'
  elif kind=='deleted':plan['edges'][0]['to']='exit:missing'
  else:bad['edits'].append(copy.deepcopy(edit))
  edit['text']=json.dumps(plan);c.rpc('applySlots',False,rows=[bad]);assert c.checkpoint()==before;c.original()
 f.checked('새 copy는 공개 분기/None만 반환하며 계약 변경·미등록 ID·잘못된 실행선·중복/다른 frame 입력을 전체 거절한다')
 source=c.source_file if registered else f.project/'Flow.celem';c.mutate_source() if registered else source.write_bytes(c.physical[source]+b' ');c.rpc('applySlots',False,rows=[request]);assert c.checkpoint()==before;c.restore_source() if registered else source.write_bytes(c.physical[source]);c.original();f.checked('첫 Save 전 원본 계약 경합은 copy 생성·소유 배정·반환 편집을 모두 미적용한다')
 c.rpc('applySlots',rows=[request]);saved=c.checkpoint();c.original();assert c.rpc('settledSlots',rows=[request])['settled'];f.stop();f.start(1);f.invoke('select',{'id':c.owner});assert c.rpc('settledSlots',rows=[request])['settled'] and c.checkpoint()==saved;assert c.read()['diagnostics']['state']=='source-ready';c.original();f.checked('첫 Save는 copy/배정/반환을 한 checkpoint에 저장하며 cold와 같은 receipt 재조회는 중복 생성하지 않는다')
 snapshot=json.loads(next(iter(saved.values())));(f.case/'saved-before-review.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2));units={row['id']:row for row in snapshot['changes']};guards=f.metadata('blueprintPublicCopyReturnGuards',namespace=f.n[:-2],units=units)['checks'];assert ({'FlowBody.celem','Flow.graph.json','Flow.node.json'} if registered else {'Flow.celem','FlowBody.celem','Flow.graph.json','Flow.node.json'})<={r['path'] for r in guards}
 if registered:
  assert c.x.feature not in units and units[c.implementation]['publicCopyOrigin']['owner']==c.owner
  closure=f.metadata('blueprintOverrideContracts',action='verifyGroup',project=str(c.x.manifest),units=units);assert any(row['path']==str(c.source_file) for row in closure['reads'])
  for mode in ['missing-origin','changed-origin','origin-hash','foreign-path','registration']:
   bad=copy.deepcopy(units)
   try:
    if mode=='missing-origin':bad[c.implementation].pop('publicCopyOrigin')
    elif mode=='changed-origin':bad[c.implementation]['publicCopyOrigin']['observations'][0]['sha256']='0'*64
    elif mode=='origin-hash':bad[c.owner]['slotSaveReceipt']['publicCopyOrigins'][c.implementation]='0'*64
    elif mode=='foreign-path':bad[c.implementation]['publicCopyOrigin']['observations'][0]['path']=str(f.case/'unregistered source')
    else:c.x.manifest.write_bytes(c.physical[c.x.manifest].replace(b'dependency External.Functions version "1";',b''))
    call={'operation':'blueprintOverrideContracts' if mode in ['foreign-path','registration'] else 'blueprintPublicCopyReturnGuards','action':'verifyGroup','namespace':f.n[:-2],'project':str(c.x.manifest),'units':bad}
    done=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(call),capture_output=True,text=True,env=f.env,check=True);assert not json.loads(done.stdout)['ok'],mode
   finally:c.x.manifest.write_bytes(c.physical[c.x.manifest])
  f.checked('외부 함수는 쓰기 단위가 아니며 첫 관측 origin/hash·원시 경로/헤더·현재 등록을 복원/최종 CAS guard에서 결합한다')
 for kind in ['group','receipt','read-guards','contract-read','hash','provenance','source-proof']:
  bad=copy.deepcopy(units);receipt=bad[c.owner]['slotSaveReceipt']
  if kind=='group':
   for row in bad.values():row.pop('atomicEditGroup',None)
  elif kind=='receipt':bad[c.owner].pop('slotSaveReceipt')
  elif kind=='read-guards':receipt.pop('readGuards')
  elif kind=='contract-read':receipt['readGuards'].pop('FlowBody.celem' if registered else 'Flow.celem')
  elif kind=='hash':receipt['readGuards']['FlowBody.celem' if registered else 'Flow.celem']['hash']='0'*64
  elif kind=='provenance':doc=json.loads(bad[c.graph]['draft']);doc['copySource']['implementation']=f.n+'Other';bad[c.graph]['draft']=json.dumps(doc)
  else:receipt['sources'][c.x.impl if registered else c.x.feature]['hash']='0'*64
  done=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'blueprintPublicCopyReturnGuards','namespace':f.n[:-2],'units':bad}),capture_output=True,text=True,env=f.env,check=True);assert json.loads(done.stdout)['ok'] is False,kind
 assert c.checkpoint()==saved;c.original();f.checked('첫 생성의 완전한 관측 그룹·영수증·원문 읽기 CAS와 출처를 복원 validator에서도 검증하며 누락/변조를 거절한다')
 for branch in ['none','failure']:
  current=c.read();binding=c.binding();exits={r['name']:json.loads(r['valueJson']) for r in current['exits']};exits['yes']={'executionBranch':branch};c.rpc('authorBatch',id=c.graph,owner=c.owner,ownerHash=binding['hash'],ownerRevision=binding['revision'],attempt=uuid.uuid4().hex,checkpointHash=current['checkpointHash'],sourceProof=c.x.proof(current),**({'dependencyHash':current['nodeFlowDependencyHash']} if registered else {}),edits=[{'action':'branchExits','node':'$branches','definition':{'exits':exits,'entry':current['entry'],'edges':copy.deepcopy(current['edges'])}}]);c.original();assert c.read()['diagnostics']['state']=='source-ready'
 f.checked('첫 Save 후 아직 미확정인 copy의 반복 반환 편집도 생성 출처와 기존 원문 읽기 증거를 유지한다')
 ids=c.read()['reviewIds'];f.invoke('reviewGroup',{'ids':[c.graph],'target':'portable'},False);review=f.invoke('reviewGroup',{'ids':ids,'target':'portable'});assert not review['state']['review'].get('errors');c.mutate_source() if registered else source.write_bytes(c.physical[source]+b' ');result=f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']})['result']['result'];assert not result['sourceConfirmed'];c.restore_source() if registered else source.write_bytes(c.physical[source]);c.original();f.stop();f.start(2);f.invoke('select',{'id':c.owner});assert c.confirm(c.read()['reviewIds'])['sourceConfirmed'];c.retained();
 if registered:
  donor=f.project/'Flow.node.json';donor.write_bytes(c.physical[donor]+b'\n');c.physical[donor]=donor.read_bytes()
 f.invoke('saveDraft',{});c.retained();c.build('creating-after','failure');f.checked('부분 Review·최종 원문 경합을 거절하고 정상 재검토 뒤 기존 int out→실패 분기→다음 줄을 실행한다')
 f.stop();f.start(3);f.invoke('select',{'id':c.owner});assert c.read()['diagnostics']['state']=='source-ready';c.retained();print('M12_CREATING_COPY_FIXTURE '+str(f.case),flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
