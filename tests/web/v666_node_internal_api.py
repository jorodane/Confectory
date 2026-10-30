"""M11: 기존 C#를 보존하는 단일 동작 래핑, 실제 엔진의 저장/복구/최종 CAS."""
import copy,hashlib,json,pathlib,subprocess,sys,uuid
import v536_wide_mixed as f
is_void=len(sys.argv)>3 and sys.argv[3]=='void';return_type='void' if is_void else 'long'
n=f.n;feature=n+'Flow';impl=n+'FlowBody';graph=impl+'/body:common';original_id=graph+'/node:calculate';child=graph+'/graph:calculate';leaf=original_id+'/node:body'
function='function '+feature+' (long amount) -> '+return_type+' {provide '+feature+' with '+impl+';}'
prepared=f.metadata('blueprintPrepareFeature',id=feature,text='function '+feature+' (long amount) -> '+return_type+' {}',implementation=impl,graphPath='Flow.graph.json',nodePath='Flow.node.json');g=prepared['graph'];g['profile']='sync-acyclic-methods-v1';g['nodes'][0]['id']='calculate';g['nodes'][0]['intent']='원문을 보존할 동작';g['entry']='calculate'
for e in g['edges']:
 for k in ['from','to']:
  if e.get(k)=='body':e[k]='calculate'
def rename_refs(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if k=='node' and x=='body':v[k]='calculate'
   else:rename_refs(x)
 elif isinstance(v,list):
  for x in v:rename_refs(x)
rename_refs(g)
defs=f.metadata('featureBlueprintNodes',featureSource=function,graph=g)
record={'schema':1,'node':'calculate','definitionHash':next(x for x in defs['nodes'] if x['id']=='calculate')['definitionHash'],'source':('System.Console.WriteLine("m11-once"); return;' if is_void else '// 원문 😀\r\nreturn Twice(amount) + 1;\r\n'),'helpers':'private static long Twice(long value) => value * 2;'}
for file,text in [('Flow.celem',function),('FlowBody.celem',prepared['implementation']),('Flow.graph.json',json.dumps(g)),('Flow.node.json',json.dumps(record,ensure_ascii=False)),('MainBody.celem','implementation '+n+'MainBody for '+n+'Main () -> int {import '+feature+' as Flow (long) -> '+return_type+';body common "Main.csbody";}'),('Main.csbody','calls.Flow.Invoke(3); return 7;' if is_void else 'return checked((int)calls.Flow.Invoke(3));')]: (f.project/file).write_text(text)
manifest=f.project/'project.cproj';manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element Flow function "Flow.celem";element FlowBody implementation "FlowBody.celem";registry Confectory.Build.DotNet'))
physical={p:p.read_bytes() for p in f.project.iterdir() if p.is_file()}
def rpc(action,ok=True,**kw):return f.invoke('blueprint',{'action':action,'id':graph,**kw},ok)['result'].get('result')
def read(id=graph):return rpc('read',id=id)
def proof(d):return json.dumps(sorted([[x['id'],x['revision'],x['hash']] for x in d['sources']]),separators=(',',':'))
def checkpoint():return {str(p):p.read_bytes() for p in f.project.glob('.confectory/edit-workspaces/*/draft.json')}
def original():assert all(p.read_bytes()==b for p,b in physical.items())
def request(d,nonce=None,source=None):return {'id':graph,'attempt':uuid.uuid4().hex,'checkpointHash':d['checkpointHash'],'sourceProof':proof(d),'edits':[{'action':'internalizeNode','node':'calculate','definition':{'nonce':nonce or uuid.uuid4().hex,**({'source':source} if source is not None else {})}}]}
def any_invoke(endpoint,body):
 import time
 v=f.mount();rid=uuid.uuid4().hex
 try:
  assert f.raw({'op':'invoke','view':v['view'],'scope':v['scope'],'expectedRevision':v['revision'],'requestId':rid,'endpoint':endpoint,'input':body})['ok']
  deadline=time.monotonic()+120
  while time.monotonic()<deadline:
   u=f.raw({'op':'update','view':v['view'],'scope':v['scope']});row=next((r for r in u.get('results',[]) if r['requestId']==rid),None)
   if row:return row,u.get('state')
   time.sleep(.01)
  raise AssertionError('bounded command result missing')
 finally:f.raw({'op':'dispose','view':v['view']})
def build(name,expected):
 run=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(manifest),'portable'],capture_output=True,text=True,env=f.env);(f.case/(name+'-build.log')).write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr[-2000:]+run.stdout[-2000:];report=json.loads(run.stdout);result=subprocess.run(report['run'],capture_output=True,text=True,env=f.env);assert result.returncode==expected,(result.returncode,result.stdout,result.stderr)
 if is_void:assert result.stdout.strip()=='m11-once',result.stdout
if __name__=='__main__':
 try:
  build('before',7);f.start(0);d=read();assert d['diagnostics']['state']=='source-ready';before=checkpoint();nonce=uuid.uuid4().hex
  preview=rpc('previewNodeInternal',node='calculate',definition={'nonce':nonce});assert preview['privatePath']=='calculate' and preview['nodeFlowPreview'];assert next(x for x in preview['nodes'] if x['id']=='body')['source']==record['source'];assert checkpoint()==before;original();f.checked('내부 진입 미리보기는 원문·helper·연결·물리 파일과 체크포인트를 변경하지 않는다')
  # The pure preparer refuses unsupported contexts before moving any code.
  owner_request={'project':str(manifest),'id':impl,'text':(f.project/'FlowBody.celem').read_text(),'bodyTarget':'common'}
  for name in ['legacy','context','forwarded','ref','out','branch','switch','wrong-receipt']:
   candidate=copy.deepcopy(g);doc=copy.deepcopy(record)
   if name=='legacy':candidate['profile']='sync-acyclic-v1'
   elif name=='context':candidate['nodes'][0]['implementationContext']={'implementation':impl}
   elif name=='forwarded':candidate['nodes'][0]['forwardCallerStorage']=True
   elif name in ['ref','out']:candidate['nodes'][0]['signature']['args'][0]['mode']=name
   elif name in ['branch','switch']:candidate['nodes'][0]['control']=name
   else:doc['definitionHash']='0'*64
   r=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({'operation':'blueprintNodeFlow','id':graph,'node':'calculate','nonce':nonce,'record':json.dumps(doc),'graph':candidate,'ownerRequest':owner_request}),text=True,capture_output=True,env=f.env,check=True);assert not json.loads(r.stdout)['ok'],name
  assert checkpoint()==before;original();f.checked('구형 profile·whole-body 문맥·ref/out·switch·낡은 receipt는 원본 보존 상태로 거절한다')
  req=request(d,nonce);bad=copy.deepcopy(req);bad['sourceProof']=bad['sourceProof'].replace(d['sources'][0]['hash'],'0'*64);rpc('authorBatch',False,**bad);assert checkpoint()==before;original()
  for nonce_bad in ['../escape','A'*32]:rpc('previewNodeInternal',False,node='calculate',definition={'nonce':nonce_bad});assert checkpoint()==before
  # Physical originals must be checked too, not just the in-memory receipt.
  file=f.project/'Flow.node.json';file.write_bytes(physical[file]+b' ');rpc('authorBatch',False,**req);file.write_bytes(physical[file]);assert checkpoint()==before;original();f.checked('잘못된 증거·경로·물리 원본 충돌은 후보와 입력을 전체 보존한다')
  collision=f.project/'nodes'/('internal_'+nonce+'.node.json');collision.parent.mkdir(exist_ok=True);collision.write_text('owned collision sentinel');rpc('authorBatch',False,**req);assert collision.read_text()=='owned collision sentinel' and checkpoint()==before;collision.rename(f.case/'preserved-collision-sentinel.json');original();f.checked('새 내부 소스 경로 충돌을 덮어쓰지 않고 전체 후보를 거절한다')
  result=rpc('authorBatch',**req);assert result['settled'] and result['checkpointSaved'];assert rpc('settledAuthorBatch',**req)['settled'];current=read();body=read(child);assert body['diagnostics']['state']=='source-ready',body['diagnostics'];outer=next(x for x in current['nodes'] if x['id']=='calculate');assert outer['kind']=='graph' and outer['signature']==next(x for x in d['nodes'] if x['id']=='calculate')['signature'];assert current['edges']==d['edges'];assert set(current['reviewIds'])>=set([graph,original_id,leaf]);original();f.checked('하나의 후보/최종 체크포인트 CAS로 래핑을 저장하며 원본은 보호하고 새 leaf를 따로 관리한다')
  saved=checkpoint();f.stop();f.start(1);assert read(child)['diagnostics']['state']=='source-ready';assert checkpoint()==saved;original();f.checked('재시작에서 원문 guard와 새 내부 leaf·원자 그룹을 복원한다')
  node=next(n for n in read(child)['nodes'] if n['id']=='body');rpc('source',id=child,basis=read(child)['basis'],node='body',text='return missingM11Value;');f.invoke('saveDraft',{});bad_checkpoint=checkpoint();failed,failed_state=any_invoke('reviewGroup',{'ids':read()['reviewIds']});review=(failed_state or {}).get('review') or {}
  if review.get('status')=='ready':failed,failed_state=any_invoke('confirmGroup',{'token':review['token'],'ids':read()['reviewIds']})
  (f.case/'compile-failure.json').write_text(json.dumps([failed,failed_state],ensure_ascii=False,indent=2));assert not failed.get('result',{}).get('sourceConfirmed');assert 'missingM11Value' in json.dumps([failed,failed_state]);assert checkpoint()==bad_checkpoint;original();assert next(n for n in read(child)['nodes'] if n['id']=='body')['source']=='return missingM11Value;'
  rpc('source',id=child,basis=read(child)['basis'],node='body',text=record['source']);f.invoke('saveDraft',{});f.checked('실제 C# 컴파일 오류는 물리 원본과 저장된 잘못된 입력을 보존하며 명시 수정으로 재검토한다')
  f.invoke('reviewGroup',{'ids':[graph]},False);original();f.checked('일부 소스만 Review하는 요청은 거절한다')
  view=f.invoke('reviewGroup',{'ids':current['reviewIds']});(f.case/'review.json').write_text(json.dumps(view,ensure_ascii=False,indent=2));assert not view['state']['review'].get('errors');original()
  # Explicit cancellation retains the saved draft, never publishes it.
  original();assert read(child)['diagnostics']['state']=='source-ready';f.checked('Review 준비는 실제 원본을 쓰지 않고 저장된 내부 초안을 유지한다')
  view=f.invoke('reviewGroup',{'ids':read()['reviewIds']});token=view['state']['review']['token'];old_source=f.project/'Flow.node.json';old_source.write_bytes(physical[old_source]+b' ');failed,_=any_invoke('confirmGroup',{'token':token,'ids':read()['reviewIds']});assert not failed.get('result',{}).get('sourceConfirmed');assert (f.project/'Flow.graph.json').read_bytes()==physical[f.project/'Flow.graph.json'];assert not any((f.project/'nodes').glob('internal_*.node.json'));old_source.write_bytes(physical[old_source]);original();f.stop();f.start(5);f.checked('Review 이후 원문 경합도 최종 CAS에서 전체 미반영하고 저장된 내부 초안을 보존한다')
  view=f.invoke('reviewGroup',{'ids':read()['reviewIds']});token=view['state']['review']['token'];f.invoke('confirmGroup',{'token':token,'ids':read()['reviewIds']});assert (f.project/'Flow.node.json').read_bytes()==physical[f.project/'Flow.node.json'];published=json.loads((f.project/'Flow.graph.json').read_text());wrapper=next(x for x in published['nodes'] if x['id']=='calculate');assert wrapper['retainedCode']['sourceTextHash']==hashlib.sha256(physical[f.project/'Flow.node.json']).hexdigest();new=next(x for x in wrapper['graph']['nodes'] if x['id']=='body');assert json.loads((f.project/new['implementation']).read_text())['source']==record['source'];build('after',7);f.checked('컴파일 Confirm 후 원문 파일은 바이트 그대로이고 새 내부 구현의 실제 CLR 결과도 같다')
  f.stop();f.start(2);assert read(child)['diagnostics']['state']=='source-ready';f.checked('최종 반영 후 재시작은 활성 내부 흐름을 다시 연다')
  print('M11_FIXTURE '+str(f.case),flush=True)
 finally:
  (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
