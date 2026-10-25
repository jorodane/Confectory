"""A private enum/source/helper update is one physical-root checkpoint transaction."""
import copy,json,uuid
import v536_information_nested_fixture as x
f=x.f;root=x.caller_id;id=root+'/graph:left'
def rpc(action,ok=True,**body):return f.invoke('blueprint',{'action':action,**body},ok)['result'].get('result')
try:
 f.start(0);f.invoke('saveDraft',{});r=rpc('read',id=id);checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));baseline=checkpoint.read_bytes();node=next(n for n in r['nodes'] if n['id']=='body');execution=copy.deepcopy(node['executionEnum']);execution['members'][1]['name']='Renamed';execution['members'].reverse();source=x.record_sources['left'].replace('Result.Next','Result.Renamed');helpers=x.code_helpers
 def request():return {'id':id,'attempt':uuid.uuid4().hex,'checkpointHash':r['checkpointHash'],'sourceProof':json.dumps([[s['id'],s.get('revision'),s['hash']] for s in r['sources']],separators=(',',':')),'privateBinding':{'graph':id,'root':root,'node':'body','source':node['sourceId'],'definitionHash':node['definitionHash'],'sourceHash':next(s['hash'] for s in r['sources'] if s['id']==node['sourceId'])},'edits':[{'action':'enumCode','node':'body','definition':{'executionEnum':execution,'source':source,'helpers':helpers}}]}
 for fault in ['enum','field','source','path','binding']:
  req=request();p=req['edits'][0]['definition']
  if fault=='enum':p['executionEnum']={'primary':'done','members':[{'id':'missing','name':'Missing','value':0}]}
  elif fault=='field':p['extra']='unsupported'
  elif fault=='source':p['source']=[]
  elif fault=='path':req['id']=root+'/graph:right'
  else:req['privateBinding']['sourceHash']='0'*64
  rpc('authorBatch',False,**req);assert checkpoint.read_bytes()==baseline and all((f.project/p).read_bytes()==v for p,v in x.snapshot.items())
 req=request();reply=rpc('authorBatch',**req);assert reply['checkpointSaved'];assert rpc('settledAuthorBatch',**req)['settled'];data=rpc('read',id=id);current=next(n for n in data['nodes'] if n['id']=='body');assert current['executionEnum']==execution and current['source']==source and current['helpers']==helpers;g=json.loads(next(v['draft'] for v in json.loads(checkpoint.read_text())['changes'] if v['id']==root));assert g['nodes'][1:]==x.root['nodes'][1:] and g['locals']==x.root['locals'] and g['edges']==x.root['edges']
 f.stop();f.start(1);assert rpc('settledAuthorBatch',**req)['settled'];assert next(n for n in rpc('read',id=id)['nodes'] if n['id']=='body')['helpers']==helpers;f.checked('가상 private enum·source·helpers는 실제 root한후보/CAS·오류미적용·cold receipt에 묶이며 형제 원문을 보존한다')
 ids=[s['id'] for s in data['sources']];f.invoke('reviewGroup',{'ids':ids,'target':'portable'});review=f.state()['review'];assert review['status']=='ready',review;f.invoke('confirmGroup',{'ids':ids,'token':review['token']});record=json.loads((f.project/'left.node.json').read_text());assert record['source']==source and record['helpers']==helpers;assert json.loads((f.project/'caller.graph.json').read_text())['nodes'][0]['graph']['nodes'][1]['executionEnum']==execution;f.checked('실제 compiler Review/Confirm은 private 포트 식별성과 C#·보조 함수만 반영한다')
finally:
 f.stop();print(json.dumps({'checks':f.checks,'evidence':str(f.case),'actualEngine':True,'projectRun':False,'nativeWindows':False},ensure_ascii=False))
