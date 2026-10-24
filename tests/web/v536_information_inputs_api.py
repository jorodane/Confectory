"""Real atomic API/compiler input add/delete, no project Run or paid calls."""
import copy,json
import v536_information_inputs_fixture as x
f,n,owner,fn=x.f,x.n,x.owner,x.fn
mode=x.mode
def rpc(action,ok=True,**body):return f.invoke('blueprint',{'action':action,**body},ok)['result'].get('result')
def schema():f.invoke('schema',{'id':owner});return f.state()['schema']
def request():
 s=schema();method=next(m for m in s['ownFunctions'] if m['id']==fn)
 p=rpc('readOwnerEdits',id=owner,hash=s['textHash'],includeFunctionInputs=fn)
 return {'id':owner,'rows':[],'basis':p['basis'],'declaration':{'id':owner,'hash':s['textHash'],'changes':[{'type':'function-edit','id':fn,'hash':method['hash'],'name':method['name'],'description':method['description'],'signature':x.new,'mapping':x.mapping|{'callers':x.plans(p['functionInputs'])}}]}}
def unchanged():assert all((f.project/p).read_bytes()==b for p,b in x.snapshot.items())
def verify():
 assert n.canonical(next(m for m in schema()['ownFunctions'] if m['id']==fn)['signature'])==x.new
 rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']}
 graph=json.loads(rows[n.caller+'Body/body:common']['draft'])
 for call in graph['nodes']:
  assert call['signature']==x.new
  assert call['arguments']==({'amount':{'input':'first'},'count':{'constant':7},'extra':{'input':'second'}} if mode=='binding' else {'amount':{'input':'first'},'count':{'input':'second'}}|({} if mode.startswith('delete') else {'extra':{'constant':9223372036854775806}}))
 code=json.loads(rows[fn+'Body/body:common/node:body']['draft'])
 assert code['source']==n.record['source']
 group=rows[owner]['atomicEditGroup'];assert {owner,fn,fn+'Body',fn+'Body/body:common',n.caller+'Body',n.caller+'Body/body:common'}<=set(group)
 return group
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{})
 checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes()
 r=request();cases=[]
 bad=copy.deepcopy(r);bad['declaration']['changes'][0]['mapping'].pop('callers');cases.append(bad)
 bad=copy.deepcopy(r);next(iter(bad['declaration']['changes'][0]['mapping']['callers'].values()))['hash']='0'*64;cases.append(bad)
 bad=copy.deepcopy(r);bad['declaration']['changes'][0]['mapping']['callers'].pop(next(iter(bad['declaration']['changes'][0]['mapping']['callers'])));cases.append(bad)
 bad=copy.deepcopy(r);selection=next(iter(bad['declaration']['changes'][0]['mapping']['callers'].values()))
 if mode.startswith('delete'):selection['disconnect']={}
 else:selection['inputs']['extra']={'valueJson':'"wrong type"'}
 cases.append(bad)
 # Deleting a still-used root input must not rewrite or discard its C# use.
 bad=copy.deepcopy(r);change=bad['declaration']['changes'][0];change['signature']={'args':[{'name':'amount','type':'long'}],'return':'long'};change['mapping']['args']={a['name']:('amount' if a['name']=='amount' else None) for a in x.old['args']}
 for key,selection in change['mapping']['callers'].items():
  selection['inputs']={'amount':'amount'};selection['disconnect']={'count':'{"input":"second"}'}|({'extra':'{"constant":9223372036854775806}'} if mode.startswith('delete') else {})
 cases.append(bad)
 for bad in cases:
  rpc('applySlots',False,**bad);assert checkpoint.read_bytes()==before;unchanged();assert n.canonical(next(m for m in schema()['ownFunctions'] if m['id']==fn)['signature'])==x.old
 f.checked('미선택·stale source·잘못된 값/삭제 연결은 모든 선언·구현·호출자 미적용 및 원문 보존')
 if mode=='storage':
  checkpoint.chmod(0o400)
  try:rpc('applySlots',False,**r);assert checkpoint.read_bytes()==before;unchanged()
  finally:checkpoint.chmod(0o600)
  f.checked('저장 장치 거절 뒤 기존 checkpoint·전체 원문 보존')
 if mode=='conflict':
  s=schema();f.invoke('editDescription',{'id':owner,'hash':s['textHash'],'revision':s['revision'],'value':'동시 편집 원문 보존'});held=f.state()['draft']['text'];rpc('applySlots',False,**r);assert f.state()['draft']['text']==held and checkpoint.read_bytes()==before;unchanged();f.checked('실제 동시 초안 수정은 전체 거절하며 peer 입력과 기존 checkpoint를 유지');raise SystemExit(0)
 out=rpc('applySlots',**r);assert out['atomic'] and out['checkpointSaved'];ids=verify();unchanged()
 f.stop();f.start(1);f.invoke('select',{'id':owner});assert verify()==ids;unchanged()
 f.checked('명시적 호출별 매핑 한 후보/CAS 저장·cold에서 정확64값과 내부 C# 원문을 보존')
 f.invoke('reviewGroup',{'ids':ids,'target':'portable'});review=f.state()['review'];assert review['status']=='ready',review
 f.invoke('confirmGroup',{'ids':ids,'token':review['token']});f.stop();f.start(2);f.invoke('select',{'id':owner})
 assert n.canonical(next(m for m in schema()['ownFunctions'] if m['id']==fn)['signature'])==x.new
 assert json.loads((f.project/'function.node.json').read_text())['source']==n.record['source']
 for p,b in x.snapshot.items():
  if p not in {'FreeInfo.celem','elements/'+fn.split('::')[1]+'.celem',fn.split('::')[1]+'Body.celem','function.graph.json','function.node.json','caller.graph.json','CallerBody.celem'}:assert (f.project/p).read_bytes()==b,p
 f.checked('실제 compiler Review/Confirm·cold에서 전체 closure만 반영, 다른 함수·부모·소스 보존')
finally:
 print(json.dumps({'checks':f.checks,'mode':mode,'evidence':str(f.case)},ensure_ascii=False));f.stop()
