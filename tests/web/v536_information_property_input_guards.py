"""Actual selection proof races; mutations stay inside the copied fixture pack."""
import copy,json
import v536_information_property_inputs_fixture as c
x,f,n,owner,fn=c.x,c.f,c.n,c.owner,c.fn
def request():
 f.invoke('schema',{'id':owner});s=f.state()['schema'];method=next(m for m in s['ownFunctions'] if m['id']==fn);preview=f.invoke('blueprint',{'action':'readOwnerEdits','id':owner,'hash':s['textHash'],'includeFunctionInputs':fn})['result']['result']
 return {'action':'applySlots','id':owner,'rows':[],'basis':preview['basis'],'declaration':{'id':owner,'hash':s['textHash'],'changes':[{'type':'function-edit','id':fn,'hash':method['hash'],'name':method['name'],'description':method['description'],'signature':x.new,'mapping':x.selections(preview)}]}}
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));before=checkpoint.read_bytes();r=request()
 for field,value in [('contracts','0'*64),('value',{'valueJson':'null'}),('value',{'input':'number'})]:
  bad=copy.deepcopy(r);next(iter(bad['declaration']['changes'][0]['mapping']['implementations'].values()))[field]=value;f.invoke('blueprint',bad,False);assert checkpoint.read_bytes()==before
 bad=copy.deepcopy(r);del next(iter(bad['declaration']['changes'][0]['mapping']['implementations'].values()))['contracts'];f.invoke('blueprint',bad,False);assert checkpoint.read_bytes()==before;f.checked('위조/누락 계약 receipt와 null/다른 타입 수신자는 전체 미적용 및 원래 checkpoint 보존')
 for path in [c.model/'Read.celem',c.model/'pack.cpack',f.project/'ReceiverInfo.celem']:
  r=request();original=path.read_bytes();path.write_bytes(original+b'\n// another fixture editor changed this source\n');peer=path.read_bytes()
  try:f.invoke('blueprint',r,False);assert path.read_bytes()==peer and checkpoint.read_bytes()==before;assert all((f.project/p).read_bytes()==b for p,b in x.snapshot.items() if f.project/p!=path)
  finally:path.write_bytes(original)
 f.checked('선택 후 accessor·등록 manifest·필드 소유 선언의 실제 변경은 ABI가 같아도 전체 거절하고 peer/입력 보존')
 pure=n.request(x.new,x.mapping['args']);preview={k:f.metadata(op,project=str(f.manifest),manifest=f.manifest.read_text(),id=owner,function=fn,units=pure['units']) for k,op in [('functionInputs','informationFunctionInputs'),('functionInputUses','informationFunctionInputUses'),('functionDependencies','informationFunctionDependencies')]};pure['changes'][0]['mapping']=x.selections(preview);result=n.prepare(pure)
 observations={v['path'] for v in result['observations']};external={p for p in observations if p.startswith(str(c.model))};assert external=={str(c.model/p) for p in ['pack.cpack','Read.celem','Set.celem','RefCell.celem']},external
 assert all((c.model/p).read_bytes()==b for p,b in c.model_original.items());assert all((f.project/p).read_bytes()==b for p,b in x.snapshot.items());f.checked('property 계약 조회는 고정 accessor 선언/manifest만 관찰하고 provider 본문·실제 getter·원본 자료를 사용하지 않는다')
finally:
 print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'projectRun':False,'nativeWindows':False},ensure_ascii=False));f.stop()
