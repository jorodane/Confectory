"""One checkpoint/receipt and original physical CAS for the source dependency."""
import copy,hashlib,json,os,subprocess
import v666_retained_caller_contract_fixture as x
f=x.f
h=lambda text:hashlib.sha256(text.encode()).hexdigest()
def rpc(action,ok=True,**kw):return f.invoke('blueprint',dict(action=action,**kw),ok)['result'].get('result')
def prepare(changes=None):
 f.invoke('schema',dict(id=x.owner));s=f.state()['schema'];basis=rpc('readOwnerEdits',id=x.owner,hash=s['textHash']);return dict(id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=s['textHash'],changes=x.request()['changes']if changes is None else changes))
def reviewed(ids):
 f.invoke('reviewGroup',dict(ids=ids,target='portable'));v=f.state()['review'];assert v['status']=='ready',v;return v['token']
def receipt(cp):return next(v for v in json.loads(cp.read_text())['changes']if v['id']==x.owner)['slotSaveReceipt']
def guard(units,ok):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(dict(operation='informationBodyGroupGuards',action='validate',project=str(f.manifest),namespace=f.n[:-2],units=units,selected=[x.owner])),env=f.env,text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,v;return v
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});cp=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=cp.read_bytes()
 bad=prepare();next(iter(bad['declaration']['changes'][-1]['mapping']['bodies'].values()))['text']='return MissingPeerSource;';rpc('applySlots',False,**bad);assert cp.read_bytes()==baseline;x.unchanged();f.checked('invalid last native callee source rejects all explicit callee/caller edits without changing the checkpoint')
 request=prepare();path=f.project/x.retained_file;stat=path.stat();raw=path.read_bytes();path.write_bytes(raw+b'\n')
 try:rpc('applySlots',False,**request);assert cp.read_bytes()==baseline and path.read_bytes()!=raw
 finally:path.write_bytes(raw);os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns))
 x.unchanged();f.checked('changed retained CSharp source before Save rejects the entire original observation')
 reply=rpc('applySlots',**prepare());assert reply['atomic']and reply['checkpointSaved'];ids=x.verify(cp);plans=copy.deepcopy(receipt(cp)['nativeBodyContexts']);reads=copy.deepcopy(receipt(cp)['readGuards']);saved=cp.read_bytes();units=copy.deepcopy(x.request()['units'])
 for row in json.loads(saved)['changes']:units[row['id']]=row
 (f.case/'guard-request.json').write_text(json.dumps(dict(operation='informationBodyGroupGuards',action='validate',project=str(f.manifest),namespace=f.n[:-2],units=units,selected=[x.owner]),ensure_ascii=False,indent=2));document=json.loads(saved);v=receipt(cp);(f.case/'format.json').write_text(json.dumps(dict(workspaceVersion=document['version'],receiptVersion=v['version'],newTypeProfile='nativeTypeProfile'in document,contexts=len(v['nativeBodyContexts']))));assert guard(units,True)['result']['reads']==[]
 for fault in ['capture','capture-and-guards','missing-plan','wrong-original-source','member','missing-read','foreign-read','wrong-owner','modified-source-and-proof']:
  bad=copy.deepcopy(units);v=bad[x.owner]['slotSaveReceipt'];key=x.callee+'Body/body:common'
  if fault in ['capture','capture-and-guards']:
   v.pop('nativeBodyContexts')
   if fault=='capture-and-guards':v['readGuards']={};v.pop('declaration',None)
  elif fault=='missing-plan':v['nativeBodyContexts'][1]['mapping']['bodies'].pop(key)
  elif fault=='wrong-original-source':v['nativeBodyContexts'][1]['mapping']['bodies'][key]['hash']='0'*64
  elif fault=='member':v['sources'].pop(x.caller_graph)
  elif fault=='missing-read':v['readGuards'].pop(x.code_path)
  elif fault=='foreign-read':v['readGuards']['unobserved.csbody']=dict(path='unobserved.csbody',hash='0'*64)
  elif fault=='wrong-owner':v['owner']=f.n+'Unknown'
  elif fault=='modified-source-and-proof':
   graph=json.loads(bad[x.caller_graph]['draft']);graph['nodes'][1]['arguments']['bonus']={'constant':100};bad[x.caller_graph]['draft']=json.dumps(graph);v['sources'][x.caller_graph]['hash']=h(bad[x.caller_graph]['draft'])
  guard(bad,False);assert cp.read_bytes()==saved;x.unchanged();f.checked(fault+' refuses a malformed cold source/receipt shape without checkpoint or original writes')
 f.stop();f.start(1);f.invoke('select',dict(id=x.owner));assert x.verify(cp)==ids
 late='원래 retained 호출자 의존성을 유지하는 후속 설명 · 😀';rpc('applySlots',**prepare([dict(type='description',text=late)]));assert receipt(cp)['nativeBodyContexts']==plans and receipt(cp)['readGuards']==reads
 rows={v['id']:v for v in json.loads(cp.read_text())['changes']};fn=x.caller_function;meta=dict(type='function-edit',id=fn,hash=h(rows[fn]['draft']),name=x.labels[0],description='후속 함수 설명',signature=copy.deepcopy(x.nexts[0]));rpc('applySlots',**prepare([meta]));assert receipt(cp)['nativeBodyContexts']==plans and receipt(cp)['readGuards']==reads;x.unchanged();f.checked('cold and owner/function metadata Saves retain all original source/context plans and read versions')
 rows={v['id']:v for v in json.loads(cp.read_text())['changes']};fn=x.callee;manual=copy.deepcopy(plans[1]);manual['hash']=h(rows[fn]['draft']);manual['mapping']['before']=copy.deepcopy(manual['signature']);manual['mapping']['args']={arg['name']:arg['name']for arg in manual['signature']['args']};key=fn+'Body/body:common';body=manual['mapping']['bodies'][key];body['hash']=h(rows[key]['draft']);body['beforeSignature']=copy.deepcopy(body['signature']);body['text']+='// 명시적인 후속 callee 본문 😀\r\n';rpc('applySlots',**prepare([manual]));x.selected[fn]=body['text'];assert receipt(cp)['readGuards']==reads;assert receipt(cp)['nativeBodyContexts'][1]['mapping']['bodies'][key]['hash']==plans[1]['mapping']['bodies'][key]['hash'];plans=copy.deepcopy(receipt(cp)['nativeBodyContexts']);x.verify(cp);f.checked('follow-up explicit native source uses current metadata and retains the original caller/callee contracts, source hashes and physical versions')
 request=prepare([dict(type='description',text=late+' next')]);path=f.project/x.header_path;raw=path.read_bytes();path.write_bytes(raw+b'\n');saved=cp.read_bytes()
 try:rpc('applySlots',False,**request);assert cp.read_bytes()==saved
 finally:path.write_bytes(raw)
 for index,name in enumerate([x.caller_path,x.header_path,x.retained_file,x.paths[x.callee],'retained-code.node.json']):
  token=reviewed(ids);saved=cp.read_bytes();path=f.project/name;stat=path.stat();raw=path.read_bytes();path.write_bytes(raw+b'\n')
  try:
   result=f.invoke('confirmGroup',dict(ids=ids,token=token))['result']['result'];assert result['sourceConfirmed']is False,result;assert cp.read_bytes()==saved and path.read_bytes()!=raw
  finally:path.write_bytes(raw);os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns))
  x.unchanged();f.stop();f.start(index+2);f.invoke('select',dict(id=x.owner));assert receipt(cp)['nativeBodyContexts']==plans and receipt(cp)['readGuards']==reads;f.checked(name+' after Review blocks final Confirm and preserves original/peer/checkpoint state')
 token=reviewed(ids);out=f.invoke('confirmGroup',dict(ids=ids,token=token))['result']['result'];assert out.get('sourceConfirmed')is not False;x.verify_live();assert f.metadata('inspect',text=x.n.a.info.read_text())['description']==late;f.checked('fresh Review/Confirm after exact restoration executes22 with original retained caller contract, independent calculation, source bytes and read boundaries retained')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
