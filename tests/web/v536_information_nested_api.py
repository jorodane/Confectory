"""Actual qualified private frames and manual source/post edits, atomic cold/Confirm."""
import copy,json
import v536_information_nested_fixture as x
f,owner,fn=x.f,x.owner,x.fn

def rpc(action,ok=True,**body):return f.invoke('blueprint',{'action':action,**body},ok)['result'].get('result')
def request():
 f.invoke('schema',{'id':owner});s=f.state()['schema'];method=next(v for v in s['ownFunctions'] if v['id']==fn)
 p=rpc('readOwnerEdits',id=owner,hash=s['textHash'],includeFunctionInputs=fn,includeFunctionBodies=True,includeFunctionOutputs=x.callee,functionSignature=x.new,functionRemap=x.remap)
 return {'id':owner,'rows':[],'basis':p['basis'],'declaration':{'id':owner,'hash':s['textHash'],'changes':[{'type':'function-edit','id':fn,'hash':method['hash'],'name':method['name'],'description':method['description'],'signature':x.new,'mapping':x.selections(p)}]}}
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
 for fault in ['missing','path','source','body-path']:
  r=request();m=r['declaration']['changes'][0]['mapping'];key=next(iter(m['callers']))
  if fault=='missing':m['callers'].pop(key)
  elif fault=='path':m['callers'][key]['node']='right/'+x.leaf_id
  elif fault=='source':
   if x.callee:next(iter(m['implementations'].values()))['value']={'valueJson':'true'}
   else:m['bodies'][x.body_id]['text']='return invalid;'
  elif x.cpp:m['bodies'][x.record_ids['left']]['whole']['node']='right/deep/body'
  else:m['callers'][key]['hash']='0'*64
  rpc('applySlots',False,**r);assert checkpoint.read_bytes()==baseline
 f.checked('중첩 호출/record의 경계·source·누락 증거는 전체 거절하며 부모·형제·checkpoint를 보존한다')
 result=rpc('applySlots',**request());assert result['atomic'] and result['checkpointSaved'];ids=x.verify(checkpoint);f.stop();f.start(1);f.invoke('select',{'id':owner});assert x.verify(checkpoint)==ids
 f.checked('depth2·동명 leaf·명시 C#/postCall을 실제 한 후보/CAS에 저장하고 cold에서 분리 복원한다')
 f.invoke('reviewGroup',{'ids':ids,'target':'portable'});review=f.state()['review'];assert review['status']=='ready',review;f.invoke('confirmGroup',{'ids':ids,'token':review['token']});f.stop();f.start(2);f.invoke('select',{'id':owner})
 g=json.loads((f.project/'caller.graph.json').read_text());assert g['nodes'][2]==x.root['nodes'][2] and g['locals']==x.root['locals']
 for name in x.record_ids:
  record=json.loads((f.project/(name+'.node.json')).read_text());assert record['source']==(x.edited_records[name] if x.cpp and name in x.edited_records else x.record_sources[name])
  if x.code_control and name in x.record_helpers:assert record['helpers']==x.code_helpers
 if not x.callee:assert json.loads((f.project/x.body_path).read_text())['source']==x.edited
 else:assert json.loads((f.project/'inner.node.json').read_text())==json.loads(x.snapshot['inner.node.json'])
 f.checked('실제 compiler Review/Confirm·cold 뒤에도 모든 qualified source·부모/형제·정확한 값이 보존된다')
finally:
 print(json.dumps({'checks':f.checks,'evidence':str(f.case),'cpp':x.cpp,'postMode':x.post_mode,'actualEngine':True,'projectRun':False,'nativeWindows':False},ensure_ascii=False));f.stop()
