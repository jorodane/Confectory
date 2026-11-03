"""Authored public OriginalResult wrapper; no legacy adapter migration."""
import copy,json
import v666_root_execution_fixture as base
f=base.f
assert base.out_mode and (not base.data_mode or base.nonvoid_mode)
feature=base.feature;impl=base.impl;graph=base.graph;caller=base.caller
# Generated fixture input, never user files. Publish the existing out value and
# materialize the already-supported public contract before testing the wrapper.
base.function=base.function.replace('{','{value blueprintPublishedOutputs = '+json.dumps(json.dumps(['result']))+';',1)
plain='function '+feature+' '+base.signature+' -> '+base.native_return+' {value blueprintPublishedOutputs = '+json.dumps(json.dumps(['result']))+';}'
base.root['contractHash']=f.metadata('blueprintPrepareFeature',id=feature,text=plain,implementation=impl,graphPath='Flow.graph.json',nodePath='Flow.node.json')['graph']['contractHash']
(f.project/'Flow.celem').write_text(base.function);(f.project/'Flow.graph.json').write_text(json.dumps(base.root))
rows={id:{'kind':kind,'path':path,'draft':(f.project/path).read_text()} for id,kind,path in [(feature,'function','Flow.celem'),(impl,'implementation','FlowBody.celem'),(graph,'blueprint','Flow.graph.json'),(graph+'/node:choose','blueprint-node','Flow.node.json'),(f.n+'Main','function','Main.celem'),(f.n+'MainBody','implementation','MainBody.celem'),(caller,'blueprint','Main.graph.json'),(caller+'/node:after','blueprint-node','After.node.json')]}
pure=f.metadata('blueprintRootExecution',namespace='Owned.Elements',id=graph,units=rows,plan=base.plan({'entry':base.root['entry'],'edges':base.root['edges']}))
for row in pure['units'].values():(f.project/row['path']).write_text(row['draft'])
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};base.physical=physical
read=base.read;rpc=base.rpc;checkpoint=base.checkpoint;proof=base.proof;original=base.original
result_code=base.result_code
initial_stdout='callee:1';final_stdout='callee:1\nwrapper:1:'+('420' if base.nonvoid_mode else '10')
def build(name,code=None,stdout=None):base.build(name,result_code if code is None else code,final_stdout if stdout is None else stdout)
def wrap(data,source=None):
 row=next(n for n in data['nodes'] if n['id']=='invoke');p=row['wrapperEditor'];assert p['originalExecution'] and p['originalOutcome']=='public-execution-branches'
 return {'action':'wrapCall','node':'invoke','contractHash':p['contractHash'],'originalExecution':p['originalExecution'],'executionEnum':copy.deepcopy(p['executionEnum']),**({'returnMapping':p['returnMapping']} if p.get('returnMapping') else {}),'text':('global::System.Console.WriteLine("wrapper:"+(int)originalBranch+":"+context.result);\r\n'+p['source']) if source is None else source,'helpers':''}
def request(data,edit):return {'id':caller,'attempt':__import__('uuid').uuid4().hex,'checkpointHash':data['checkpointHash'],'sourceProof':proof(data),'edits':[{'action':edit['action'],'node':edit['node'],'definition':{k:v for k,v in edit.items() if k not in ['action','node']}}]}
def preserved():
 for name in ['Flow.celem','FlowBody.celem','Flow.graph.json','Flow.node.json','After.node.json','Main.celem','MainBody.celem']:
  p=f.project/name;assert p.read_bytes()==physical[p],p
