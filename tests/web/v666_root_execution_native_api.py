"""Native M12 source/receiver identity and scoped readonly observation across CAS/restore."""
import copy,hashlib,json,stat
import v666_root_execution_native_fixture as x
f=x.f
try:
 x.build('native-before',x.result_code,x.initial_stdout);f.start(0);d=x.read();assert d['rootExecution'],d.get('rootExecutionError')
 units={r['id']:{'kind':r['kind'],'path':r['path'],'draft':(f.project/r['path']).read_text()} for r in d['sources']}
 pure=f.metadata('blueprintRootExecution',namespace='Owned.Elements',id=x.graph,units=units,plan=x.plan(d));assert len(pure['group'])==11,pure['group'];assert pure['observedContracts']==sorted([x.native,x.scope])
 for u in pure['units'].values():u['baseline']=hashlib.sha256((f.project/u['path']).read_bytes()).hexdigest()
 assert len(f.metadata('blueprintRootExecutionGuards',namespace='Owned.Elements',units=pure['units'])['checks'])==11
 before=x.checkpoint();req=x.request(d)
 for change in ['missing-scope','scope-kind','context-owner','context-import','context-signature','context-storage','source-identity']:
  bad=copy.deepcopy(units)
  if change=='missing-scope':bad.pop(x.scope)
  elif change=='scope-kind':bad[x.scope]['kind']='function'
  else:
   g=json.loads(bad[x.graph]['draft']);node=g['nodes'][0]
   if change=='context-owner':node['implementationContext']['implementation']=f.n+'WrongBody'
   elif change=='context-import':node['implementationContext']['imports']['Scoped']['scope']=f.n+'Unit'
   elif change=='context-signature':node['signature']['args'][0]['type']='int'
   elif change=='context-storage':node['arguments']['input']={'constant':2}
   else:node['sourceIdentity']='bad\nsource'
   bad[x.graph]['draft']=json.dumps(g)
  try:f.metadata('blueprintRootExecution',namespace='Owned.Elements',id=x.graph,units=bad,plan=x.plan(d))
  except AssertionError:pass
  else:raise AssertionError('Invalid native observation/context accepted: '+change)
  assert x.checkpoint()==before;x.original()
 f.checked('실제 this 재귀·receiver·scoped provider 실행을 확인하고 문맥/서명/저장소/원문 위치 변조와 scope 누락을 거절한다')
 def replace(path,value):
  mode=stat.S_IMODE(path.stat().st_mode);path.chmod(0o600)
  try:path.write_bytes(value)
  finally:path.chmod(mode)
 for file in ['Native.celem','ChosenScope.celem','Native.node.json']:
  path=f.project/file;replace(path,x.physical[path]+b' ')
  try:x.rpc('authorBatch',False,**req)
  finally:replace(path,x.physical[path])
  assert x.checkpoint()==before;x.original()
 f.checked('Save 전 native 원문·readonly import 함수·scope object 경합은 전체 후보를 거절하며 입력을 보존한다')
 saved=x.rpc('authorBatch',**req);assert saved['settled'] and saved['checkpointSaved'];assert x.rpc('settledAuthorBatch',**req)['settled'];assert len(x.read()['reviewIds'])==11;x.original();checkpoint=x.checkpoint()
 rows={u['id']:u for u in json.loads(next(iter(checkpoint.values())))['changes']}
 for kind in ['missing-scope','changed-scope','missing-receipt','tampered-hash']:
  bad=copy.deepcopy(rows)
  if kind=='missing-scope':bad.pop(x.scope)
  elif kind=='changed-scope':bad[x.scope]['draft']+=' '
  elif kind=='missing-receipt':bad[x.graph].pop('authorSaveReceipt')
  else:bad[x.graph]['authorSaveReceipt']['sources'][x.scope]['hash']='0'*64
  try:f.metadata('blueprintRootExecutionGuards',namespace='Owned.Elements',units=bad)
  except AssertionError:pass
  else:raise AssertionError('Invalid restored observation accepted: '+kind)
 f.stop();f.start(1);assert x.checkpoint()==checkpoint and x.rpc('settledAuthorBatch',**req)['settled'];assert x.read()['diagnostics']['state']=='source-ready';x.original()
 f.checked('전체 문맥·함수·scope를 한 checkpoint/receipt에 저장하고 누락·변조 복구를 거절하며 cold·응답 재조회를 보존한다')
 f.invoke('reviewGroup',{'ids':[x.graph]},False);ids=x.read()['reviewIds']
 for i,file in enumerate(['ChosenScope.celem','Native.celem','Native.node.json']):
  ids=x.read()['reviewIds'];view=f.invoke('reviewGroup',{'ids':ids});assert not view['state']['review'].get('errors');checkpoint=x.checkpoint();p=f.project/file;replace(p,x.physical[p]+b' ')
  try:reply=f.invoke('confirmGroup',{'ids':ids,'token':view['state']['review']['token']})['result']['result'];assert reply['sourceConfirmed'] is False,reply
  finally:replace(p,x.physical[p])
  assert x.checkpoint()==checkpoint;x.original();f.stop();f.start(i+2)
 f.checked('부분 Review와 Review 뒤 scope·import·native 원문 변경을 최종 CAS에서 전체 거절하고 재시작 입력을 유지한다')
 ids=x.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids});confirmed=f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']});assert confirmed['result']['result']['sourceConfirmed'],confirmed['state'].get('logs');x.build('native-after',x.result_code,x.final_stdout)
 for file in ['whole original.csbody','Native.node.json','Flow.node.json','Native.celem','ChosenScope.celem']:
  p=f.project/file;assert p.read_bytes()==x.physical[p],p
 for file in ['whole original.csbody','Native.celem','ChosenScope.celem']:assert stat.S_IMODE((f.project/file).stat().st_mode)==0o400
 f.checked('명시 Confirm은 native 원문·ID·위치·서명·readonly 모드를 유지하며 출력 발행 뒤 공개 분기를 실제 실행한다')
 # An unrouted branch keeps the existing caller continuation; ordinary IInvoke keeps native recursion.
 p=f.project/'Main.graph.json';confirmed=p.read_bytes();g=json.loads(confirmed);g['edges']=[e for e in g['edges'] if not(e['from']=='invoke' and e['port'].startswith('case:'))];p.write_text(json.dumps(g))
 try:x.build('native-continuation',x.result_code,x.initial_stdout)
 finally:p.write_bytes(confirmed)
 body=f.project/'MainBody.celem';confirmed=body.read_bytes();body.write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+x.feature+' as Original (long,out int) -> void;body common "Legacy.csbody";}');(f.project/'Legacy.csbody').write_text('calls.Original.Invoke(-2,out int value);global::System.Console.WriteLine("ordinary:"+value);return value;')
 try:x.build('native-ordinary',5,'native:5\nordinary:5')
 finally:body.write_bytes(confirmed)
 f.checked('분기 미연결 continuation과 ordinary IInvoke도 재귀/receiver 경계를 바꾸지 않고 기존 데이터와 scoped provider를 실행한다')
 f.stop();f.start(8);d=x.read();follow=x.plan(d);follow['branches'].reverse();follow['branches'][1]['name']='성공 이름 변경';x.rpc('authorBatch',**x.request(d,follow));f.stop();f.start(9);ids=x.read()['reviewIds'];review=f.invoke('reviewGroup',{'ids':ids});confirmed=f.invoke('confirmGroup',{'ids':ids,'token':review['state']['review']['token']});assert confirmed['result']['result']['sourceConfirmed'],confirmed['state'].get('logs');x.build('native-repeat',x.result_code,x.final_stdout)
 f.checked('반복 이름/순서 편집과 재시작에서도 기존 분기 ID/값과 native 문맥·호출 연결을 유지한다')
 print('M12_NATIVE_FIXTURE '+str(f.case),flush=True)
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
