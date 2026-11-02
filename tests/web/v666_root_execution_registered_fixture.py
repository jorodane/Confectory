"""An owned explicit provider of a readonly directly registered public function."""
import copy,json,sys,uuid,hashlib
import v666_root_execution_fixture as x
f=x.f;f.manifest=x.manifest;graph=x.graph;impl=x.impl;old_feature=x.feature;feature='External.Functions::Flow';owner=f.n+'FreeInfo';module=f.n+'M12Rules';graph_path='Flow.graph.json'
units={}
for id,kind,path in [(x.feature,'function','Flow.celem'),(x.impl,'implementation','FlowBody.celem'),(x.graph,'blueprint','Flow.graph.json'),(x.graph+'/node:choose','blueprint-node','Flow.node.json'),(f.n+'Main','function','Main.celem'),(f.n+'MainBody','implementation','MainBody.celem'),(x.caller,'blueprint','Main.graph.json'),(x.caller+'/node:after','blueprint-node','After.node.json')]:units[id]={'kind':kind,'path':path,'draft':(f.project/path).read_text()}
prepared=f.metadata('blueprintRootExecution',namespace=f.n[:-2],id=graph,units=units,plan=x.plan({'entry':x.root['entry'],'edges':x.root['edges']}))
for row in prepared['units'].values():(f.project/row['path']).write_text(row['draft'])
pack=f.case/'registered public contract';pack.mkdir();function_file=pack/'Flow.celem';function_text=(f.project/'Flow.celem').read_text().replace('provide '+old_feature+' with '+impl+';','').replace('function '+old_feature+' ','function '+feature+' ')
function_file.write_text(function_text);(pack/'pack.cpack').write_text('pack External.Functions version "1" {standalone false;element Flow function "Flow.celem";}')
(f.project/'FreeInfo.celem').write_text('schema '+owner+' {module '+module+';provide '+feature+' with '+impl+';}')
(f.project/'M12Rules.celem').write_text('module '+module+' {require '+feature+' '+x.import_signature+' -> '+x.native_return+';}')
p=f.project/'FlowBody.celem';p.write_text(p.read_text().replace(' for '+old_feature+' ',' for '+feature+' '))
x.manifest.write_text(x.manifest.read_text().replace('element Flow function "Flow.celem";','').replace('registry Confectory.Build.DotNet','element FreeInfo schema "FreeInfo.celem";element M12Rules module "M12Rules.celem";dependency External.Functions version "1";registry External.Functions "'+str(pack/'pack.cpack')+'";registry Confectory.Build.DotNet',1))
g=json.loads((f.project/graph_path).read_text());g['feature']=feature
# Rebind through the real registry/compiler; do not duplicate contract hash rules.
rebound=f.metadata('blueprintDescribeOwned',project=str(x.manifest),id=impl,text=p.read_text(),graph=g,bodyTarget='common',definitionsOnly=True,rebindContract=True);assert rebound['state']=='node-definitions',rebound;g=rebound['reboundGraph'];(f.project/graph_path).write_text(json.dumps(g))
r=json.loads((f.project/'Flow.node.json').read_text());r['definitionHash']=next(n['definitionHash'] for n in rebound['nodes'] if n['id']=='choose');(f.project/'Flow.node.json').write_text(json.dumps(r,ensure_ascii=False))
p=f.project/'MainBody.celem';p.write_text(p.read_text().replace('import '+old_feature+' ','import '+feature+' ').replace(x.alias,'fg_call_'+hashlib.sha256(feature.encode()).hexdigest()[:24]).replace(' -> '+x.native_return+';',' -> '+x.native_return+' in '+owner+';',1))
cg=json.loads((f.project/'Main.graph.json').read_text());call=next(n for n in cg['nodes'] if n['id']=='invoke');call['feature']=feature;call['publicExecution']=g['contractHash'];defs=f.metadata('featureBlueprintNodes',featureSource=(f.project/'Main.celem').read_text(),graph=cg,featureContracts={feature:function_text});assert defs['state']=='node-definitions',defs;(f.project/'Main.graph.json').write_text(json.dumps(cg));r=json.loads((f.project/'After.node.json').read_text());r['definitionHash']=next(n['definitionHash'] for n in defs['nodes'] if n['id']=='after');(f.project/'After.node.json').write_text(json.dumps(r))
for p in pack.iterdir():p.chmod(0o440)
pack.chmod(0o750)
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};physical.update({p:p.read_bytes() for p in pack.iterdir()});f.original={str(p.relative_to(f.project)):v for p,v in physical.items() if p.is_relative_to(f.project)}
parent_file=function_file;modes={p:p.stat().st_mode for p in pack.iterdir()};external=True
# Existing information slot binding, with no copy or inferred provider selection.
def binding():
 row=f.invoke('schema',{'id':owner})['state']['schema'];return {'owner':owner,'ownerHash':row['textHash'],'ownerRevision':row['revision']}
def rpc(action,ok=True,**kw):return f.invoke('blueprint',{'action':action,'id':graph,**binding(),**kw},ok)['result'].get('result')
def read():return rpc('read')
def plan(data,branch='failure'):
 exits={r['name']:json.loads(r['valueJson']) for r in data['exits']};exits['yes']['executionBranch']=branch;return {'entry':data['entry'],'edges':copy.deepcopy(data['edges']),'exits':exits}
def request(data,selection=None):return {'id':graph,**binding(),'attempt':uuid.uuid4().hex,'checkpointHash':data['checkpointHash'],'sourceProof':x.proof(data),'dependencyHash':data['nodeFlowDependencyHash'],'edits':[{'action':'branchExits','node':'$branches','definition':selection or plan(data)}]}
def checkpoint():return x.checkpoint()
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def originals_retained():assert all(p.read_bytes()==v for p,v in physical.items() if p!=f.project/graph_path);assert all(p.stat().st_mode==v for p,v in modes.items())
def build(label,after=False,branch='failure'):x.build(label,stdout=x.initial_stdout if after else 'callee:1')
def mutate_parent(suffix=b' '):
 function_file.chmod(0o640)
 try:function_file.write_bytes(physical[function_file]+suffix)
 finally:function_file.chmod(0o440)
def restore_parent():
 function_file.chmod(0o640)
 try:function_file.write_bytes(physical[function_file])
 finally:function_file.chmod(0o440)
