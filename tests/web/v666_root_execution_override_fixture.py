"""Existing public branches, explicitly owned child body, readonly ancestry."""
import copy,json,sys,uuid
import v666_root_execution_fixture as x
f=x.f;graph=x.graph;feature=x.feature;impl=x.impl;owner=feature;graph_path='Flow.graph.json';external='--external-parent' in sys.argv
units={}
for id,kind,path in [(x.feature,'function','Flow.celem'),(x.impl,'implementation','FlowBody.celem'),(x.graph,'blueprint','Flow.graph.json'),(x.graph+'/node:choose','blueprint-node','Flow.node.json'),(f.n+'Main','function','Main.celem'),(f.n+'MainBody','implementation','MainBody.celem'),(x.caller,'blueprint','Main.graph.json'),(x.caller+'/node:after','blueprint-node','After.node.json')]:units[id]={'kind':kind,'path':path,'draft':(f.project/path).read_text()}
candidate=f.metadata('blueprintRootExecution',namespace=f.n[:-2],id=graph,units=units,plan=x.plan({'entry':x.root['entry'],'edges':x.root['edges']}))
for row in candidate['units'].values():(f.project/row['path']).write_text(row['draft'])
parent=('External.Ancestors::' if external else f.n)+'Parent';borrower=f.n+'Inherited';folder=f.case/'registered ancestors' if external else f.project
if external:folder.mkdir()
(folder/'Parent.celem').write_text('implementation '+parent+' for '+feature+' '+x.signature+' -> void {blueprint common "Parent.graph.json";}')
(folder/'Parent.graph.json').write_bytes((f.project/graph_path).read_bytes());(folder/'Parent.node.json').write_bytes((f.project/'Flow.node.json').read_bytes())
p=folder/'Parent.graph.json';p.write_text(p.read_text().replace('Flow.node.json','Parent.node.json'))
if external:
 (folder/'pack.cpack').write_text('pack External.Ancestors version "1" {standalone false;dependency Owned.Elements version "1";element Parent implementation "Parent.celem";}')
 extra='dependency External.Ancestors version "1";registry External.Ancestors "'+str(folder/'pack.cpack')+'";'
else:extra='element Parent implementation "Parent.celem";'
p=f.project/'FlowBody.celem';p.write_text(p.read_text().replace(' {',' extends '+parent+' {',1))
(f.project/'Inherited.celem').write_text('implementation '+borrower+' for '+feature+' '+x.signature+' -> void extends '+parent+' {}')
x.manifest.write_text(x.manifest.read_text().replace('registry Confectory.Build.DotNet',extra+'element Inherited implementation "Inherited.celem";registry Confectory.Build.DotNet',1))
if external:
 for p in folder.iterdir():p.chmod(0o440)
 folder.chmod(0o750)
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts}
if external:physical.update({p:p.read_bytes() for p in folder.iterdir()})
f.original={str(p.relative_to(f.project)):v for p,v in physical.items() if p.is_relative_to(f.project)}
parent_file=folder/'Parent.celem';modes={p:p.stat().st_mode for p in folder.glob('Parent.*')}
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def originals_retained():assert all(p.read_bytes()==v for p,v in physical.items() if p!=f.project/graph_path);assert all(p.stat().st_mode==v for p,v in modes.items())
def rpc(action,ok=True,**kw):return f.invoke('blueprint',{'action':action,'id':graph,**kw},ok)['result'].get('result')
def read():return rpc('read')
def plan(data,branch='failure'):
 exits={r['name']:json.loads(r['valueJson']) for r in data['exits']};exits['yes']={'executionBranch':branch};return {'entry':data['entry'],'edges':copy.deepcopy(data['edges']),'exits':exits}
def request(data,selection=None):return {'id':graph,'attempt':uuid.uuid4().hex,'checkpointHash':data['checkpointHash'],'sourceProof':x.proof(data),'dependencyHash':data['nodeFlowDependencyHash'],'edits':[{'action':'branchExits','node':'$branches','definition':selection or plan(data)}]}
def checkpoint():return x.checkpoint()
def build(label,after=False,branch='failure'):x.build(label,stdout=('callee:1\nafter:10' if '--out-root' in sys.argv else 'callee:1\nafter') if after else 'callee:1')
def mutate_parent(suffix=b' '):
 parent_file.chmod(0o640)
 try:parent_file.write_bytes(physical[parent_file]+suffix)
 finally:parent_file.chmod(modes[parent_file]&0o777)
def restore_parent():
 parent_file.chmod(0o640)
 try:parent_file.write_bytes(physical[parent_file])
 finally:parent_file.chmod(modes[parent_file]&0o777)
