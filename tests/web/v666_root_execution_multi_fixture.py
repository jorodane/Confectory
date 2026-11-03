"""Generated owned sources: two targets, repeated callers and a peer function."""
import copy,hashlib,json,pathlib,re,subprocess,sys
import v666_root_execution_fixture as base
f=base.f;multi_mode=True;out_mode=True
providers_mode='--providers-root' in sys.argv
feature=base.feature;impl=base.impl;graph=base.graph;caller=base.caller;peer=f.n+'PeerBody/body:common';linux=impl+'/body:linux';main_linux=f.n+'MainBody/body:linux'
no_callers='--no-callers' in sys.argv;single='--single-target' in sys.argv
route_node='invoke2';result_code=20;initial_stdout='callee:1\ncallee:2\nafter:20';final_stdout='callee:1\ncallee:2'
function=base.function;root=base.root
def record(g,fn,name,node,source,contracts):
 defs=f.metadata('featureBlueprintNodes',featureSource=fn,graph=g,featureContracts=contracts);assert defs['state']=='node-definitions',defs
 row=next(r for r in defs['nodes'] if r['id']==node);(f.project/name).write_text(json.dumps({'schema':1,'node':node,'definitionHash':row['definitionHash'],'source':source},ensure_ascii=False))
if not single:
 text=(f.project/'FlowBody.celem').read_text();(f.project/'FlowBody.celem').write_text(text.replace('blueprint common "Flow.graph.json";','blueprint common "Flow.graph.json";blueprint linux "FlowLinux.graph.json";'))
 other=copy.deepcopy(root);other['nodes'][0]['implementation']='FlowLinux.node.json';(f.project/'FlowLinux.graph.json').write_text(json.dumps(other));record(other,function,'FlowLinux.node.json','choose',base.original_source.replace('callee:','linux:').replace('amount*10','amount*20'),{})
if no_callers:
 (f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+feature+' as Flow (long,out int) -> void;body common "Main.csbody";}')
 (f.project/'Main.csbody').write_text('// Legacy IInvoke remains authored C#\r\ncalls.Flow.Invoke(1,out int value);global::System.Console.WriteLine("legacy:"+value);return value;\r\n')
 result_code=10;initial_stdout=final_stdout='callee:1\nlegacy:10'
else:
 cg=copy.deepcopy(base.cg);second=copy.deepcopy(cg['nodes'][0]);second['id']='invoke2';second['arguments']['amount']['constant']=2;cg['nodes'].insert(1,second);cg['nodes'][-1]['arguments']['value']['node']='invoke2';cg['exits']['return']['node']='invoke2';cg['edges']=[base.edge('invoke','invoke2'),base.edge('invoke2','after'),base.edge('after','exit:return')]
 (f.project/'Main.graph.json').write_text(json.dumps(cg));record(cg,base.main,'After.node.json','after','global::System.Console.WriteLine("after:"+value);',{feature:function})
 if not single:
  body=(f.project/'MainBody.celem').read_text();(f.project/'MainBody.celem').write_text(body.replace('blueprint common "Main.graph.json";','blueprint common "Main.graph.json";blueprint linux "MainLinux.graph.json";'))
  other=copy.deepcopy(cg);other['nodes'][0]['arguments']['amount']['constant']=4;other['nodes'][1]['arguments']['amount']['constant']=5;other['nodes'][-1]['implementation']='AfterLinux.node.json';(f.project/'MainLinux.graph.json').write_text(json.dumps(other));record(other,base.main,'AfterLinux.node.json','after','global::System.Console.WriteLine("after:"+value);',{feature:function})
 peer_source='function '+f.n+'Peer () -> int {provide '+f.n+'Peer with '+f.n+'PeerBody;}'
 pg=copy.deepcopy(base.cg);pg['feature']=f.n+'Peer';pg['contractHash']=f.metadata('blueprintPrepareFeature',id=f.n+'Peer',text='function '+f.n+'Peer () -> int {}',implementation=f.n+'PeerBody',graphPath='Peer.graph.json',nodePath='PeerAfter.node.json')['graph']['contractHash'];pg['nodes'][0]['arguments']['amount']['constant']=3;pg['nodes'][-1]['implementation']='PeerAfter.node.json'
 for name,text in [('Peer.celem',peer_source),('PeerBody.celem','implementation '+f.n+'PeerBody for '+f.n+'Peer () -> int {import '+feature+' as '+base.alias+' (long,out int) -> void;blueprint common "Peer.graph.json";}'),('Peer.graph.json',json.dumps(pg))]:(f.project/name).write_text(text)
 record(pg,peer_source,'PeerAfter.node.json','after','global::System.Console.WriteLine("peer-after:"+value);',{feature:function})
manifest=base.manifest;allowed={'Main','MainBody','Flow','FlowBody'}|({'Peer','PeerBody'} if not no_callers else set())
text=manifest.read_text();text=re.sub(r'element (\w+) \w+ "[^"]+";',lambda m:m.group() if m[1] in allowed else '',text)
if not no_callers:text=text.replace('registry Confectory.Build.DotNet','element Peer function "Peer.celem";element PeerBody implementation "PeerBody.celem";registry Confectory.Build.DotNet',1)
manifest.write_text(text)
if providers_mode:
 assert not no_callers and not single
 alternative=f.n+'AlternativeBody';support=f.n+'Support'
 support_source='function '+support+' (int value) -> int {provide '+support+' with '+f.n+'SupportBody;}'
 targets=''
 for target,prefix,multiplier in [('common','alternative:',100),('linux','alternative-linux:',200)]:
  file='Alternative'+target;g=copy.deepcopy(root);g['nodes'][0]['implementation']=file+'.node.json'
  (f.project/(file+'.graph.json')).write_text(json.dumps(g))
  record(g,function,file+'.node.json','choose',base.original_source.replace('callee:',prefix).replace('amount*10','amount*'+str(multiplier)),{})
  targets+='blueprint '+target+' "'+file+'.graph.json";'
 for name,text in [('AlternativeBody.celem','implementation '+alternative+' for '+feature+' (long amount,out int result) -> void {import '+support+' as Support (int) -> int;'+targets+'}'),('Support.celem',support_source),('SupportBody.celem','implementation '+f.n+'SupportBody for '+support+' (int value) -> int {body common "Support.csbody";}'),('Support.csbody','return value;')]:
  (f.project/name).write_text(text)
 # Existing scoped provider selection, authored before editing public branches.
 peer_file=f.project/'Peer.celem';peer_file.write_text(peer_file.read_text().replace('{','{provide '+feature+' with '+alternative+';',1))
 manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element AlternativeBody implementation "AlternativeBody.celem";element Support function "Support.celem";element SupportBody implementation "SupportBody.celem";registry Confectory.Build.DotNet',1))
 (f.project/'Support.celem').chmod(0o400)
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts}
original=base.original;read=base.read;rpc=base.rpc;checkpoint=base.checkpoint;proof=base.proof
base.physical=physical
def plan(data):
 result=base.plan(data);result.pop('caller');result['callers']=[];result['targets']=[]
 for row in data['rootExecution']['callers']:
  selected={'graph':row['graph'],'node':row['node']}
  if row['node']=='invoke2' or row['graph']==peer:selected['routes']=[{'branch':'success','to':'exit:return'}]
  result['callers'].append(selected)
 for row in data['rootExecution']['targets']:
  if row['graph']==data['id']:continue
  result['targets'].append({k:copy.deepcopy(row[k]) for k in ['graph','entry','edges','exits']})
  result['targets'][-1]['exits']={name:{'executionBranch':{'yes':'success','no':'failure','none':'none'}[name]} for name in row['exits']}
 return result
def request(data,selected=None):
 result=base.request(data,selected or plan(data));result['id']=data['id'];return result
def build(name,code=None,stdout=None,target='portable',entry='Main'):
 file=manifest
 if entry!='Main':file=f.project/(entry+'Run.cproj');file.write_text(manifest.read_text().replace('entry '+f.n+'Main;','entry '+f.n+entry+';'))
 default=(20,'callee:1\ncallee:2') if target=='portable' else (100,'linux:4\nlinux:5')
 if entry=='Peer':default=((300%256,'alternative:3') if target=='portable' else (600%256,'alternative-linux:3')) if providers_mode else ((30,'callee:3') if target=='portable' else (60,'linux:3'))
 if no_callers:default=(10,'callee:1\nlegacy:10') if target=='portable' else (20,'linux:1\nlegacy:20')
 code=default[0] if code is None else code;stdout=default[1] if stdout is None else stdout
 result=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(file),target],env=f.env,text=True,capture_output=True);(f.case/(name+'-build.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,result.stdout[-4000:]+result.stderr[-1000:];built=json.loads(result.stdout);run=subprocess.run(built['run'],env=f.env,text=True,capture_output=True);(f.case/(name+'-run.json')).write_text(json.dumps({'exit':run.returncode,'stdout':run.stdout,'stderr':run.stderr}));assert (run.returncode,run.stdout.strip())==(code,stdout),(run.returncode,run.stdout,run.stderr)

def original_code():assert all(p.read_bytes()==v for p,v in physical.items() if p.suffix=='.csbody' or p.name.endswith('.node.json'))
