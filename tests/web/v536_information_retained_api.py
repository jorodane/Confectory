"""Real atomic retained graph/storage/post-call transaction, cold and Confirm."""
import copy,json
import v536_information_retained_fixture as x
f,owner,fn=x.f,x.owner,x.fn

def rpc(action,ok=True,**body):return f.invoke('blueprint',{'action':action,**body},ok)['result'].get('result')
def request():
 f.invoke('schema',{'id':owner});s=f.state()['schema'];method=next(r for r in s['ownFunctions'] if r['id']==fn)
 p=rpc('readOwnerEdits',id=owner,hash=s['textHash'],includeFunctionInputs=fn,includeFunctionBodies=True,includeFunctionOutputs=True,includeFunctionOutputGraphs=True,functionSignature=x.new,functionRemap=x.remap)
 return {'id':owner,'rows':[],'basis':p['basis'],'declaration':{'id':owner,'hash':s['textHash'],'changes':[{'type':'function-edit','id':fn,'hash':method['hash'],'name':method['name'],'description':method['description'],'signature':x.new,'mapping':x.selections(p)}]}}
try:
 f.start(0);f.invoke('select',{'id':owner});f.invoke('saveDraft',{});checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes()
 for fault in ['alias','native-receipt','compile','output']+(['post'] if x.post_mode else []):
  r=request();m=r['declaration']['changes'][0]['mapping']
  if fault=='alias':m['implementations']={}
  elif fault=='native-receipt':m['bodies'][x.body_id]['whole']['hash']='0'*64
  elif fault=='compile':m['bodies'][x.body_id]['text']='nativeTotal=0;return missing;'
  elif fault=='output':m['outputs']={}
  else:m['bodies'][x.post_id]['helpers']='private static long Read(long value){return unknown;}'
  rpc('applySlots',False,**r);assert checkpoint.read_bytes()==baseline
 f.checked('별칭·graph 증거·출력/원문·후처리 오류는 기존 checkpoint를 바꾸지 않고 전체 거절한다')
 result=rpc('applySlots',**request());assert result['atomic'] and result['checkpointSaved'];ids=x.verify(checkpoint)
 if x.post_mode:assert json.loads(next(row['draft'] for row in json.loads(checkpoint.read_text())['changes'] if row['id']==x.caller+'Body/body:common'))['nodes'][0]['postCall']['source']==x.post_source
 f.stop();f.start(1);f.invoke('select',{'id':owner});assert x.verify(checkpoint)==ids
 f.checked('추가 노드·alias/live storage·정확한 local·본문·후처리를 한 후보/CAS에 저장하고 cold에서 유지한다')
 f.invoke('reviewGroup',{'ids':ids,'target':'portable'});r=f.state()['review'];assert r['status']=='ready',r;f.invoke('confirmGroup',{'ids':ids,'token':r['token']});f.stop();f.start(2);f.invoke('select',{'id':owner})
 assert json.loads((f.project/x.body_path).read_text())['source']==x.edited
 assert json.loads((f.project/'extra.node.json').read_text())['source']==x.extra_record['source']
 graph=json.loads((f.project/'function.graph.json').read_text());assert graph['edges']==x.g['edges'] and graph['locals'][1]==x.g['locals'][1]
 if x.post_mode:
  post=json.loads((f.project/'caller.graph.json').read_text())['nodes'][0]['postCall'];assert post['source']==x.post_source and post['helpers']==x.post_helpers
 f.checked('실제 compiler Review/Confirm·cold 뒤에도 노드/alias/원문·postCall helpers와 다른 소스를 보존한다')
finally:
 print(json.dumps({'checks':f.checks,'evidence':str(f.case),'storage':x.storage,'postMode':x.post_mode,'actualEngine':True,'projectRun':False,'nativeWindows':False},ensure_ascii=False));f.stop()
