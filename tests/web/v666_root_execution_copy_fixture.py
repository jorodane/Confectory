"""A saved owner-bound same-contract copy returns existing public branches."""
import copy,json,pathlib,sys,uuid
import v666_root_execution_fixture as x
f=x.f;f.manifest=x.manifest;owner=f.n+'FreeInfo';module=f.n+'M12Rules';implementation=f.n+'M12Copy';graph=implementation+'/body:common'
# Prepare a real published definition/caller, without duplicating enum/hash rules.
units={}
for id,kind,path in [(x.feature,'function','Flow.celem'),(x.impl,'implementation','FlowBody.celem'),(x.graph,'blueprint','Flow.graph.json'),(x.graph+'/node:choose','blueprint-node','Flow.node.json'),(f.n+'Main','function','Main.celem'),(f.n+'MainBody','implementation','MainBody.celem'),(x.caller,'blueprint','Main.graph.json'),(x.caller+'/node:after','blueprint-node','After.node.json')]:
 units[id]={'kind':kind,'path':path,'draft':(f.project/path).read_text()}
candidate=f.metadata('blueprintRootExecution',namespace=f.n[:-2],id=x.graph,units=units,plan=x.plan({'entry':x.root['entry'],'edges':x.root['edges']}))
for row in candidate['units'].values():(f.project/row['path']).write_text(row['draft'])
info=f.project/'FreeInfo.celem'
if not info.exists():
 info.write_text('schema '+owner+' {}');x.manifest.write_text(x.manifest.read_text().replace('registry Confectory.Build.DotNet','element FreeInfo schema "FreeInfo.celem";registry Confectory.Build.DotNet',1))
info.write_text(info.read_text().replace('FreeInfo {','FreeInfo {module '+module+';',1))
(f.project/'M12Rules.celem').write_text('module '+module+' {require '+x.feature+' '+x.import_signature+' -> '+x.native_return+';}')
x.manifest.write_text(x.manifest.read_text().replace('registry Confectory.Build.DotNet','element M12Rules module "M12Rules.celem";registry Confectory.Build.DotNet',1))
prepared=f.metadata('implementationCopy',project=str(x.manifest),action='prepare',feature=x.feature,source=x.impl,target='common',implementation=implementation,owner=owner,ownerText=info.read_text())
(f.project/'M12Copy.celem').write_text(prepared['implementation']);info.write_text(prepared['owner']);graph_path=prepared['graphPath']
(f.project/graph_path).parent.mkdir(parents=True,exist_ok=True);(f.project/graph_path).write_text(json.dumps(prepared['graph']))
for row in prepared['records']:
 path=f.project/pathlib.Path(graph_path).parent/row['relative'];path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(row['record'],ensure_ascii=False))
x.manifest.write_text(x.manifest.read_text().replace('registry Confectory.Build.DotNet','element M12Copy implementation "M12Copy.celem";registry Confectory.Build.DotNet',1))
path=f.project/'MainBody.celem';path.write_text(path.read_text().replace(' -> '+x.native_return+';',' -> '+x.native_return+' in '+owner+';',1))
caller=json.loads((f.project/'Main.graph.json').read_text());caller['nodes'].append({'id':'failed','kind':'code','control':'next','intent':'기존 실패 분기 소비','signature':{'args':[],'return':'void'},'arguments':{},'implementation':'Failed.node.json','branchOwner':'invoke'});caller['edges'] += [x.edge('invoke','failed','case:failure'),x.edge('failed','return:invoke')]
definitions=f.metadata('featureBlueprintNodes',featureSource=(f.project/'Main.celem').read_text(),graph=caller,featureContracts={x.feature:(f.project/'Flow.celem').read_text()});assert definitions['state']=='node-definitions',definitions
(f.project/'Main.graph.json').write_text(json.dumps(caller));(f.project/'Failed.node.json').write_text(json.dumps({'schema':1,'node':'failed','definitionHash':next(n['definitionHash'] for n in definitions['nodes'] if n['id']=='failed'),'source':'global::System.Console.WriteLine("failure");'}))
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};f.original={str(p.relative_to(f.project)):v for p,v in physical.items()}
provenance=copy.deepcopy(prepared['graph']['copySource']);source_files=[f.project/n for n in ['Flow.celem','FlowBody.celem','Flow.graph.json','Flow.node.json','Main.celem','MainBody.celem','Main.graph.json','After.node.json']]
source_files += [f.project/pathlib.Path(graph_path).parent/r['relative'] for r in prepared['records']]+[f.project/'Failed.node.json']
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def originals_retained():assert all(p.read_bytes()==physical[p] for p in source_files)
def binding():
 row=f.invoke('schema',{'id':owner})['state']['schema'];return {'owner':owner,'ownerHash':row['textHash'],'ownerRevision':row['revision']}
def rpc(action,ok=True,**kw):return f.invoke('blueprint',{'action':action,'id':graph,**binding(),**kw},ok)['result'].get('result')
def read():return rpc('read')
def plan(data,branch='failure'):
 exits={r['name']:json.loads(r['valueJson']) for r in data['exits']};exits['yes']['executionBranch']=branch;return {'entry':data['entry'],'edges':copy.deepcopy(data['edges']),'exits':exits}
def request(data,selection=None):return {'id':graph,**binding(),'attempt':uuid.uuid4().hex,'checkpointHash':data['checkpointHash'],'sourceProof':x.proof(data),'edits':[{'action':'branchExits','node':'$branches','definition':selection or plan(data)}]}
def checkpoint():return x.checkpoint()
def build(label,after=False,branch='failure'):x.build(label,stdout=('callee:1\n'+('failure\n' if branch=='failure' else '')+x.initial_stdout.split('\n',1)[1]) if after else 'callee:1')
