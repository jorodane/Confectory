"""Declare/Confirm public branches, create a copy, edit its return without restarting."""
import copy,json,uuid
import v666_root_execution_fixture as x
f=x.f;f.manifest=x.manifest;owner=f.n+'FreeInfo';module=f.n+'M12SessionRules';implementation=f.n+'M12SessionCopy';graph=implementation+'/body:common'
units={}
for id,kind,path in [(x.feature,'function','Flow.celem'),(x.impl,'implementation','FlowBody.celem'),(x.graph,'blueprint','Flow.graph.json'),(x.graph+'/node:choose','blueprint-node','Flow.node.json'),(f.n+'Main','function','Main.celem'),(f.n+'MainBody','implementation','MainBody.celem'),(x.caller,'blueprint','Main.graph.json'),(x.caller+'/node:after','blueprint-node','After.node.json')]:units[id]={'kind':kind,'path':path,'draft':(f.project/path).read_text()}
prepared=f.metadata('blueprintRootExecution',namespace=f.n[:-2],id=x.graph,units=units,plan=x.plan({'entry':x.root['entry'],'edges':x.root['edges']}))
for row in prepared['units'].values():(f.project/row['path']).write_text(row['draft'])
(f.project/'FreeInfo.celem').write_text('schema '+owner+' {module '+module+';}');(f.project/'M12SessionRules.celem').write_text('module '+module+' {require '+x.feature+' '+x.signature.replace(' amount','').replace(' result','')+' -> void;default '+x.feature+' with '+x.impl+';}')
x.manifest.write_text(x.manifest.read_text().replace('registry Confectory.Build.DotNet','element FreeInfo schema "FreeInfo.celem";element M12SessionRules module "M12SessionRules.celem";registry Confectory.Build.DotNet',1));p=f.project/'MainBody.celem';p.write_text(p.read_text().replace(' -> void;',' -> void in '+owner+';',1))
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};code={p:v for p,v in physical.items() if p.name.endswith('.node.json') or p.suffix=='.csbody'}
def schema():return f.invoke('schema',{'id':owner})['state']['schema']
def rpc(action,**kw):return f.invoke('blueprint',{'action':action,**kw})['result']['result']
def read():
 s=schema();return rpc('read',id=graph,owner=owner,ownerHash=s['textHash'],ownerRevision=s['revision'])
def confirm(ids):
 r=f.invoke('reviewGroup',{'ids':ids,'target':'portable'});assert not r['state']['review'].get('errors');assert f.invoke('confirmGroup',{'ids':ids,'token':r['state']['review']['token']})['result']['result']['sourceConfirmed']
try:
 f.start(0);f.invoke('select',{'id':x.feature});f.invoke('saveDraft',{});d=x.read();plan=x.plan(d);plan['branches'][0]['name']='성공 이름 확인';x.rpc('authorBatch',**x.request(d,plan));confirm(x.read()['reviewIds']);assert not json.loads(next(f.project.glob('.confectory/edit-workspaces/*/draft.json')).read_text())['changes'];f.checked('같은 세션의 공개 분기 정의 거래는 Confirm과 checkpoint 정착까지 완료한다')
 f.invoke('select',{'id':owner});s=schema();selection=rpc('readImplementationCopy',id=owner,function=x.feature,source=x.impl,target='common',implementation=implementation,revision=s['revision'],hash=s['textHash']);row={'function':x.feature,'implementation':implementation,'copySource':x.impl,'copyTarget':'common','basis':selection['basis'],'fingerprint':selection['fingerprint'],'edits':[]};rpc('applySlots',id=owner,rows=[row]);confirm(read()['reviewIds']);f.checked('재시작 없이 새 copy를 기존 공개 계약 그대로 생성·배정·확정하며 종료된 루트 거래가 새 저장을 잠그지 않는다')
 d=read();s=schema();exits={r['name']:json.loads(r['valueJson']) for r in d['exits']};exits['yes']={'executionBranch':'failure'};rpc('authorBatch',id=graph,owner=owner,ownerHash=s['textHash'],ownerRevision=s['revision'],attempt=uuid.uuid4().hex,checkpointHash=d['checkpointHash'],sourceProof=x.proof(d),edits=[{'action':'branchExits','node':'$branches','definition':{'entry':d['entry'],'edges':copy.deepcopy(d['edges']),'exits':exits}}]);confirm(read()['reviewIds']);assert all(p.read_bytes()==v for p,v in code.items());x.build('same-session-copy',stdout='callee:1\nafter:10');f.checked('같은 세션에서 저장 copy의 기존 분기 반환도 실제 실행하며 C#·ID·공개 IO와 caller 연결을 보존한다')
finally:
 (f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
print('M12_COPY_SESSION_FIXTURE '+str(f.case),flush=True)
