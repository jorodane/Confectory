"""Public wrapper executes the original once, publishes data, then maps branches."""
import copy,json,hashlib
import v666_root_execution_wrapper_fixture as x
f=x.f
try:
 x.build('public-before',stdout=x.initial_stdout);f.start(0);d=x.read(x.caller);assert d['diagnostics']['state']=='source-ready';row=next(n for n in d['nodes'] if n['id']=='invoke');assert row['publicExecution'];edit=x.wrap(d);before=x.checkpoint()
 legacy=f.metadata('blueprintCallWrapper',functionText=(f.project/'Flow.celem').read_text(),executionEnum={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0}]},source='return Result.NoBranch;',**({'returnMapping':'native-return-out-v1'} if x.base.nonvoid_mode else {}))
 assert legacy['originalOutcome']==('native-data-completion-only' if x.base.nonvoid_mode else 'native-void-completion-only') and legacy['originalExecution'] is None
 for field in ['receipt','output-contract','missing-receipt','primary']:
  bad=copy.deepcopy(edit)
  if field=='receipt':bad['originalExecution']='0'*64
  elif field=='output-contract':bad['contractHash']='0'*64
  elif field=='missing-receipt':bad.pop('originalExecution')
  else:bad['executionEnum']['primary']='success'
  x.rpc('authorBatch',False,**x.request(d,bad));assert x.checkpoint()==before;x.original()
 f.checked('실제 공개 call의 명시 wrapper만 원본 실행/출력 receipt로 준비하며 legacy NoBranch는 보존하고 위장·누락·다른 primary는 전체 거절한다')
 req=x.request(d,edit);saved=x.rpc('authorBatch',**req);assert saved['checkpointSaved'] and saved['settled'];assert x.rpc('settledAuthorBatch',**req)['settled'];x.original();v=x.read(x.caller);n=next(n for n in v['nodes'] if n['id']=='invoke');assert not n['publicExecution'] and n['postCall']['originalExecution']==edit['originalExecution'] and n['postCall']['source']==edit['text'] and n['executionEnum']==edit['executionEnum'];assert json.loads(next(iter(x.checkpoint().values())))['changes']
 f.stop();f.start(1);assert x.rpc('settledAuthorBatch',**req)['settled'];assert x.read(x.caller)['diagnostics']['state']=='source-ready';x.original()
 f.checked('명시 전환은 원래 ID·분기 연결과 C#을 보존하고 한 checkpoint·cold·응답 재조회에서 중복 적용하지 않는다')
 stored={r['id']:r for r in json.loads(next(iter(x.checkpoint().values())))['changes']};units={}
 for row in x.read(x.caller)['sources']:
  text=(f.project/row['path']).read_text();units[row['id']]=copy.deepcopy(stored.get(row['id'],{'kind':row['kind'],'path':row['path'],'draft':text,'original':text,'baseline':hashlib.sha256((f.project/row['path']).read_bytes()).hexdigest()}))
 def guard(rows):return f.metadata('blueprintRootExecutionGuards',namespace='Owned.Elements',units=rows)
 assert len(guard(units)['checks'])==len(units)
 for kind in ['missing-receipt','missing-marker','tampered-contract','missing-source','changed-locator']:
  bad=copy.deepcopy(units)
  if kind=='missing-receipt':bad[x.caller].pop('authorSaveReceipt')
  elif kind=='missing-marker':bad[x.caller]['authorSaveReceipt'].pop('publicWrapper')
  elif kind=='tampered-contract':bad[x.caller]['authorSaveReceipt']['sources'][x.feature]['hash']='0'*64
  elif kind=='missing-source':bad.pop(x.feature)
  else:bad[x.caller]['authorSaveReceipt']['sources'][x.feature]['path']='other.celem'
  try:guard(bad)
  except AssertionError:pass
  else:raise AssertionError('Corrupt wrapper observation accepted: '+kind)
 f.checked('누락·변조한 wrapper marker/계약 receipt·소스·경로는 최종 가드에서 거절한다')

 v=x.read(x.caller);ids=v['reviewIds'] or [r['id'] for r in v['sources']];view=f.invoke('reviewGroup',{'ids':ids});assert not view['state']['review'].get('errors');baseline=x.checkpoint();p=f.project/'Flow.celem';p.write_bytes(x.physical[p]+b' ')
 try:answer=f.invoke('confirmGroup',{'ids':ids,'token':view['state']['review']['token']})['result']['result'];assert not answer['sourceConfirmed']
 finally:p.write_bytes(x.physical[p])
 assert x.checkpoint()==baseline;x.original();f.stop();f.start(2)
 f.checked('Review 뒤 원본 함수 경합은 최종 CAS에서 wrapper 전환 전체를 미반영하고 입력을 복원한다')
 v=x.read(x.caller);ids=v['reviewIds'] or [r['id'] for r in v['sources']];view=f.invoke('reviewGroup',{'ids':ids});assert not view['state']['review'].get('errors');f.invoke('confirmGroup',{'ids':ids,'token':view['state']['review']['token']});x.build('public-wrapper-after');x.preserved()
 f.checked('원본은 한번만 실제 호출하고 기존 native 반환/ref/out snapshot 뒤 공개 성공1을 자체 성공으로 대응하여 기존 반환선을 실행한다')
 f.stop();f.start(3);v=x.read(x.caller);assert v['diagnostics']['state']=='source-ready';n=next(n for n in v['nodes'] if n['id']=='invoke');assert n['postCall']['source']==edit['text'];x.preserved();f.checked('확정 뒤 cold에서도 OriginalResult 연결·원문·공개 분기와 데이터 계약을 보존한다')
 d=x.read(x.graph);choices=d['rootExecution'];assert not choices['callers'] and len(choices['wrappers'])==1
 plan={'branches':copy.deepcopy(choices['branches']),'entry':d['entry'],'edges':copy.deepcopy(d['edges']),'exits':{e['name']:json.loads(e['valueJson']) for e in d['exits']},'callers':[],'targets':[],'wrappers':[]}
 plan['branches'][0]['name']='명시 갱신한 성공';plan['branches'].append({'id':'extra','name':'추가 원본 분기','value':3})
 def update(p):return {'id':x.graph,'attempt':__import__('uuid').uuid4().hex,'checkpointHash':d['checkpointHash'],'sourceProof':x.proof(d),'edits':[{'action':'rootExecution','node':'$root','definition':p}]}
 before=x.checkpoint();x.rpc('authorBatch',False,**update(plan));assert x.checkpoint()==before
 plan['wrappers']=[{k:r[k] for k in ['graph','node','originalExecution','contractHash']} for r in choices['wrappers']];request=update(plan);x.rpc('authorBatch',**request);assert x.rpc('settledAuthorBatch',**request)['settled']
 n=next(n for n in x.read(x.caller)['nodes'] if n['id']=='invoke');assert n['postCall']['source']==edit['text'] and n['executionEnum']==edit['executionEnum'] and n['postCall']['originalExecution']!=edit['originalExecution'];assert len(x.read()['reviewIds'])==8
 f.stop();f.start(4);assert x.rpc('settledAuthorBatch',**request)['settled'];ids=x.read()['reviewIds'];view=f.invoke('reviewGroup',{'ids':ids});assert not view['state']['review'].get('errors');f.invoke('confirmGroup',{'ids':ids,'token':view['state']['review']['token']});x.build('public-wrapper-contract-update')
 assert (f.project/'Flow.node.json').read_bytes()==x.physical[f.project/'Flow.node.json'];assert next(n for n in x.read(x.caller)['nodes'] if n['id']=='invoke')['postCall']['source']==edit['text']
 f.checked('원본 분기 이름/추가 갱신은 모든 wrapper를 명시 선택해야 한 후보·cold·전체 Review/CAS로 반영하며 자체 enum·C#·연결과 실제 실행은 유지한다')

 print('M12_PUBLIC_WRAPPER_FIXTURE '+str(f.case),flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
