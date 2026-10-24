"""Atomic callee/caller input replacement through the real fixture compiler."""
import copy,json
import v536_information_input_replacements_fixture as x
f,n,owner,fn=x.f,x.n,x.owner,x.fn

def rpc(action,ok=True,**body):return f.invoke('blueprint',{'action':action,**body},ok)['result'].get('result')
def schema():f.invoke('schema',{'id':owner});return f.state()['schema']
def unchanged():assert all((f.project/p).read_bytes()==b for p,b in x.snapshot.items())
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));saved=checkpoint.read_bytes()
 s=schema();method=next(m for m in s['ownFunctions'] if m['id']==fn);preview=rpc('readOwnerEdits',id=owner,hash=s['textHash'],includeFunctionInputs=fn)
 change={'type':'function-edit','id':fn,'hash':method['hash'],'name':method['name'],'description':method['description'],'signature':x.new,'mapping':x.selections(preview)}
 r={'id':owner,'rows':[],'basis':preview['basis'],'declaration':{'id':owner,'hash':s['textHash'],'changes':[change]}}
 cases=[]
 for field in ['implementations','callers']:
  bad=copy.deepcopy(r);bad['declaration']['changes'][0]['mapping'][field]={};cases.append(bad)
 for field,value in [('hash','0'*64),('before','{"input":"other"}'),('value',{'input':'missing'}),('value',{'valueJson':'"wrong type"'})]:
  bad=copy.deepcopy(r);next(iter(bad['declaration']['changes'][0]['mapping']['implementations'].values()))[field]=value;cases.append(bad)
 bad=copy.deepcopy(r);m=bad['declaration']['changes'][0]['mapping'];m['implementations']['Other::Body/body:common#body#amount']=copy.deepcopy(next(iter(m['implementations'].values())));cases.append(bad)
 if x.kind=='mixed':
  bad=copy.deepcopy(r);next(iter(bad['declaration']['changes'][0]['mapping']['callers'].values()))['disconnect']={'amount':'{"input":"first"}'};cases.append(bad)
 if hasattr(x,'extra_cases'):cases.extend(x.extra_cases(r))
 for bad in cases:
  rpc('applySlots',False,**bad);assert checkpoint.read_bytes()==saved;unchanged();assert n.canonical(next(m for m in schema()['ownFunctions'] if m['id']==fn)['signature'])==x.old
 f.checked('누락/잘못된 callee·caller 대응·source·값·다른 소유·모순 해제는 전체 거절 및 원문/기존 checkpoint 보존')
 if x.mode=='conflict':
  p=f.project/'caller.graph.json';g=json.loads(p.read_text());g['nodes'][0]['intent']='다른 편집자의 원문';p.write_text(json.dumps(g));peer=p.read_bytes();rpc('applySlots',False,**r);assert checkpoint.read_bytes()==saved and p.read_bytes()==peer;assert all((f.project/path).read_bytes()==b for path,b in x.snapshot.items() if path!='caller.graph.json');f.checked('선택 후 실제 caller source 변경은 전체 미적용 및 peer 원문 보존');raise SystemExit(0)
 if x.mode=='storage':
  checkpoint.chmod(0o400)
  try:rpc('applySlots',False,**r);assert checkpoint.read_bytes()==saved;unchanged()
  finally:checkpoint.chmod(0o600)
  f.checked('checkpoint 쓰기 실패는 정의·구현·양쪽 연결 전체 미적용')
 out=rpc('applySlots',**r);assert out['atomic'] and out['checkpointSaved'];ids=x.verify(checkpoint);unchanged();f.stop();f.start(1);f.invoke('select',{'id':owner});assert x.verify(checkpoint)==ids;unchanged();f.checked('명시 callee 대체와 caller 값/저장소를 한 후보/CAS에 저장·cold하며 정확64/C# 매개변수와 본문 보존')
 f.invoke('reviewGroup',{'ids':ids,'target':'portable'});review=f.state()['review'];assert review['status']=='ready',review;f.invoke('confirmGroup',{'ids':ids,'token':review['token']});f.stop();f.start(2);f.invoke('select',{'id':owner});assert n.canonical(next(m for m in schema()['ownFunctions'] if m['id']==fn)['signature'])==x.new
 assert json.loads((f.project/'function.node.json').read_text())['source']==n.record['source']
 allowed={'FreeInfo.celem','elements/'+fn.split('::')[1]+'.celem',fn.split('::')[1]+'Body.celem','function.graph.json','function.node.json','caller.graph.json','CallerBody.celem','function-windows.graph.json','function-windows.node.json'}
 assert all((f.project/p).read_bytes()==b for p,b in x.snapshot.items() if p not in allowed)
 f.checked('실제 compiler Review/Confirm·재시작은 전체 계약/바인딩만 반영하고 다른 소스·함수·부모 보존')
finally:
 print(json.dumps({'checks':f.checks,'mode':x.mode,'evidence':str(f.case),'nativeWindows':False,'projectRun':False},ensure_ascii=False));f.stop()
