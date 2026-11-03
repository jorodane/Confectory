"""기존 Result/out 원문과 이미 연결된 completion을 가진 직접 소유 자료."""
import copy,hashlib,json
import v666_root_execution_fixture as base
f=base.f
assert base.out_mode and not base.data_mode
feature,impl,graph,caller=base.feature,base.impl,base.graph,base.caller
root=json.loads((f.project/'Flow.graph.json').read_text())
root['nodes'].append({'id':'completed','kind':'code','control':'next','intent':'기존 완료 작업','branchOwner':'choose','signature':{'args':[{'type':'int','name':'value'}],'return':'void'},'arguments':{'value':{'node':'choose','output':'result'}},'implementation':'Completed.node.json'})
root['edges'].append({'from':'completed','port':'next','to':'return:choose'})
(f.project/'Flow.graph.json').write_text(json.dumps(root))
definitions=f.metadata('featureBlueprintNodes',featureSource=(f.project/'Flow.celem').read_text(),graph=root)
(f.project/'Completed.node.json').write_text(json.dumps({'schema':1,'node':'completed','definitionHash':next(n['definitionHash']for n in definitions['nodes']if n['id']=='completed'),'source':'global::System.Console.WriteLine("completed:"+value);'}))
units={}
for id,kind,path in [(feature,'function','Flow.celem'),(impl,'implementation','FlowBody.celem'),(graph,'blueprint','Flow.graph.json'),(graph+'/node:choose','blueprint-node','Flow.node.json'),(graph+'/node:completed','blueprint-node','Completed.node.json'),(f.n+'Main','function','Main.celem'),(f.n+'MainBody','implementation','MainBody.celem'),(caller,'blueprint','Main.graph.json'),(caller+'/node:after','blueprint-node','After.node.json')]:
 text=(f.project/path).read_text();units[id]={'kind':kind,'path':path,'original':text,'draft':text,'baseline':hashlib.sha256(text.encode()).hexdigest(),'revision':0}
for id,nodes in [(graph,[{'node':'choose','enabled':True}]),(caller,[])]:
 result=f.metadata('blueprintAsyncTransition',namespace='Owned.Elements',id=id,units=units,plan={'enabled':True,'nodes':nodes});units.update(result['units'])
for unit in units.values():(f.project/unit['path']).write_text(unit['draft'])
root=json.loads((f.project/'Flow.graph.json').read_text());root['edges'].append({'from':'choose','port':'completion','to':'completed'});(f.project/'Flow.graph.json').write_text(json.dumps(root))
base.physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and '.confectory'not in p.parts};physical=base.physical
code={name:json.loads((f.project/name).read_text())['source']for name in ['Flow.node.json','Completed.node.json','After.node.json']}
read,proof,rpc,checkpoint,original,build=base.read,base.proof,base.rpc,base.checkpoint,base.original,base.build
initial_edges=copy.deepcopy(root['edges']);initial_members=copy.deepcopy(next(n for n in root['nodes']if n['id']=='choose')['executionEnum'])
def code_unchanged():
 for name,text in code.items():assert json.loads((f.project/name).read_text())['source']==text
 for path,text in physical.items():
  if path.name not in ['Flow.graph.json','Flow.node.json','Completed.node.json','After.node.json']:assert path.read_bytes()==text,path

def request(data,flag=False):
 import uuid
 return {'id':graph,'attempt':uuid.uuid4().hex,'checkpointHash':data['checkpointHash'],'sourceProof':proof(data),'edits':[{'action':'asyncTransition','node':'$root','definition':{'enabled':True,'nodes':[{'node':'choose','enabled':flag}]}}]}

def check_demoted():
 current=read();node=next(n for n in current['nodes']if n['id']=='choose');assert not node.get('async');assert node['completionBranch']['label'];assert current['edges']==initial_edges;assert [m for m in node['executionEnum']['members']if m['id']!=node['completionBranch']['id']]==initial_members['members'];return node['completionBranch']

def run(name,ordinary=False):
 code_unchanged()
 if ordinary:
  marker=check_demoted();path=f.project/'Flow.node.json';saved=path.read_bytes();record=json.loads(saved);record['source']=record['source'].replace('return amount>0?Result.Positive:Result.Negative;','return Result.'+marker['name']+';');assert record['source']!=code['Flow.node.json'];path.write_text(json.dumps(record,ensure_ascii=False))
  try:build(name,10,'callee:1\ncompleted:10\nafter:10')
  finally:path.write_bytes(saved)
 else:build(name,10,'callee:1\nafter:10')
