"""Saved local copy of a readonly registered function; explicit owner and donor retained."""
import copy,json,uuid,pathlib
import v666_root_execution_registered_fixture as r
f=r.f;x=r.x;feature=r.feature;owner=r.owner;module=r.module;impl=f.n+'M12Copy';graph=impl+'/body:common'
prepared=f.metadata('implementationCopy',project=str(x.manifest),action='prepare',feature=feature,source=r.impl,target='common',implementation=impl,owner=owner,ownerText=(f.project/'FreeInfo.celem').read_text())
(f.project/'M12Copy.celem').write_text(prepared['implementation']);(f.project/'FreeInfo.celem').write_text(prepared['owner']);graph_path=prepared['graphPath'];(f.project/graph_path).parent.mkdir(parents=True,exist_ok=True);(f.project/graph_path).write_text(json.dumps(prepared['graph']))
for row in prepared['records']:
 path=f.project/pathlib.Path(graph_path).parent/row['relative'];path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(row['record'],ensure_ascii=False))
x.manifest.write_text(x.manifest.read_text().replace('registry Confectory.Build.DotNet','element M12Copy implementation "M12Copy.celem";registry Confectory.Build.DotNet',1))
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};physical.update({p:p.read_bytes() for p in r.pack.iterdir()});f.original={str(p.relative_to(f.project)):v for p,v in physical.items() if p.is_relative_to(f.project)}
provenance=copy.deepcopy(prepared['graph']['copySource']);function_file=r.function_file;parent_file=function_file;external=True;modes=r.modes
source_files=[p for p in physical if p!=f.project/graph_path]
def binding():
 row=f.invoke('schema',{'id':owner})['state']['schema'];return {'owner':owner,'ownerHash':row['textHash'],'ownerRevision':row['revision']}
def rpc(action,ok=True,**kw):return f.invoke('blueprint',{'action':action,'id':graph,**binding(),**kw},ok)['result'].get('result')
def read():return rpc('read')
def plan(data,branch='failure'):return r.plan(data,branch)
def request(data,selection=None):return {'id':graph,**binding(),'attempt':uuid.uuid4().hex,'checkpointHash':data['checkpointHash'],'sourceProof':x.proof(data),'dependencyHash':data['nodeFlowDependencyHash'],'edits':[{'action':'branchExits','node':'$branches','definition':selection or plan(data)}]}
def checkpoint():return x.checkpoint()
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def originals_retained():
 assert all(p.read_bytes()==physical[p] for p in source_files);assert all(p.stat().st_mode==v for p,v in modes.items());assert json.loads((f.project/graph_path).read_text())['copySource']==provenance
build=r.build
mutate_parent=r.mutate_parent
restore_parent=r.restore_parent
