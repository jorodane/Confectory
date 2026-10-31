"""M11 실행 선택기: 직접 소유 및 저장된 단독 배정 copy의 Root/private fixture."""
import copy,json,pathlib,subprocess,sys
import v666_node_internal_api as x
f=x.f;feature=x.feature;root=x.graph;refs='--refs' in sys.argv;nested='--nested' in sys.argv;owned_case='--owned-case' in sys.argv
args=([{'type':'long','name':'x','mode':'ref'},{'type':'long','name':'y','mode':'ref'},{'type':'long','name':'audit','mode':'out'}] if refs else [{'type':'long','name':'amount'},{'type':'int[]','name':'trace'},{'type':'long','name':'audit','mode':'out'}]);result='void' if refs else 'long'
def sig(args,result='void'):return {'args':copy.deepcopy(args),'return':result}
def declaration(args,result,named=True):return '('+','.join((a.get('mode','')+' '+a['type']+(' '+a['name'] if named else '')).strip() for a in args)+') -> '+result
function='function '+feature+' '+declaration(args,result)+' {provide '+feature+' with '+x.impl+';}'
prepared=f.metadata('blueprintPrepareFeature',id=feature,text='function '+feature+' '+declaration(args,result)+' {}',implementation=x.impl,graphPath='Flow.graph.json',nodePath='Flow.node.json');implementation=prepared['implementation'].replace('blueprint common','body windows "other.csbody";blueprint common')
execution={'primary':'next','members':[{'id':'next','name':'Continue','value':-2},{'id':'alternate','name':'Alternate','value':17}]}
source=('// 원문을 그대로 보존 😀\r\nx=10;y+=x;audit=x+y+EditDelta();\r\nreturn Result.Alternate;\r\n' if refs else '// 원래 실행 선택기 😀\r\naudit=amount+Step(trace)+EditDelta();\r\nreturn Choose(amount);\r\n')
helpers=('private static long EditDelta()=>0;\r\n' if refs else 'private static long Step(int[] trace){trace[0]++;return trace[0];}\r\nprivate static Result Choose(long value)=>(Result)value;\r\nprivate static long EditDelta()=>0;\r\n')
calc={'id':'calculate','kind':'code','intent':'원래 실행 분기 선택','control':'switch','signature':sig(args),'executionEnum':copy.deepcopy(execution),'arguments':{a['name']:{'input':a['name']} for a in args if a.get('mode')!='out'},'implementation':'Flow.node.json'}
if refs:calc['forwardCallerStorage']=True
leaf_args=[{'type':'long','name':'x','mode':'ref'}] if refs else [{'type':'int[]','name':'trace'}]
def action(id,owner=None):
 n={'id':id,'kind':'code','intent':id,'control':'next','signature':sig(leaf_args,'void' if refs or id!='after' else 'long'),'arguments':{a['name']:{'input':a['name']} for a in leaf_args},'implementation':id+'.node.json'}
 if owner:n['branchOwner']=owner
 return n
def export(output,value,id=None,owner=None):
 n={'id':id or 'publish_'+output,'kind':'export','intent':'명시 출력 '+output,'control':'next','output':output,'signature':sig([{'type':'long','name':'value'}]),'arguments':{'value':value}}
 if owner:n['branchOwner']=owner
 return n
def edge(a,b,port='next'):return {'from':a,'to':b,'port':port}
graph={'schema':1,'profile':'sync-acyclic-switch-v1','feature':feature,'contractHash':prepared['graph']['contractHash'],'entry':'calculate','nodes':[calc,action('chosen','calculate'),action('fallback','calculate'),action('after')],'edges':[edge('calculate','after'),edge('calculate','return:calculate','case:next'),edge('calculate','chosen','case:alternate'),edge('calculate','fallback','default')],'exits':{}}
bodies={'calculate':(source,helpers),'chosen':('x++;' if refs else 'trace[1]++;',''),'fallback':('x+=100;' if refs else 'trace[2]++;',''),'after':('x++;' if refs else 'trace[3]++;return 42;','')}
if not refs:
 graph['nodes'] += [export('audit',{'node':'calculate','output':'audit'}),export('return',{'node':'after'})];graph['edges'] += [edge('after','publish_audit'),edge('publish_audit','publish_return')]
if owned_case:
 for node in graph['nodes']:
  if 'branchOwner' not in node:node['branchOwner']='outer'
 graph['nodes'].insert(0,{'id':'outer','kind':'code','intent':'소유 분기','control':'switch','signature':sig([]),'executionEnum':copy.deepcopy(execution),'arguments':{},'implementation':'outer.node.json'});graph['entry']='outer';graph['edges'].append(edge('outer','calculate','case:alternate'));bodies['outer']=('return Result.Alternate;','')
frame='frame' if nested else '';parent=root+('/graph:frame' if nested else '');child=parent+'/graph:calculate';path='frame/calculate' if nested else 'calculate';leaf_path=path+'/body'
if nested:
 inside=copy.deepcopy(graph);inside.pop('feature');inside.pop('contractHash');outer={'id':'frame','kind':'graph','intent':'기존 직접 소유 frame','control':'next','signature':sig(args,result),'arguments':{a['name']:{'input':a['name']} for a in args if a.get('mode')!='out'},'graph':inside}
 if refs:outer['forwardCallerStorage']=True
 graph={**graph,'entry':'frame','nodes':[outer],'edges':[]}
 if not refs:graph['nodes'] += [export('audit',{'node':'frame','output':'audit'}),export('return',{'node':'frame'})];graph['edges'] += [edge('frame','publish_audit'),edge('publish_audit','publish_return')]
main=('for(int i=0;i<2;i++){long n=5;calls.Flow.Invoke(ref n,ref n,out n);global::System.Console.WriteLine(n);}long x=5,y=6;calls.Flow.Invoke(ref x,ref y,out long audit);global::System.Console.WriteLine(x+","+y+","+audit);return 7;' if refs else 'foreach(long amount in new long[]{-2,17,99}){int[] trace=new int[4];for(int i=0;i<2;i++){long value=calls.Flow.Invoke(amount,trace,out long audit);global::System.Console.WriteLine(amount+":"+value+","+audit+":"+string.Join(",",trace));}}return 7;')
for name,text in [('Flow.celem',function),('FlowBody.celem',implementation),('other.csbody','audit=0;'+('' if refs else 'return 0;')),('MainBody.celem','implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+feature+' as Flow '+declaration(args,result,False)+';body common "Main.csbody";}'),('Main.csbody',main),('Flow.graph.json',json.dumps(graph,ensure_ascii=False))]:(f.project/name).write_bytes(text.encode())
defs=f.metadata('featureBlueprintNodes',featureSource=function,graph=graph,implementationContext={'implementation':x.impl},bodyTarget='common');assert defs['state']=='node-definitions',defs
for name,(body,helper) in bodies.items():
 key=(frame+'/' if frame else '')+name;row=next(r for r in defs['nodes']+defs.get('nestedNodes',[]) if r['id']==key);record={'schema':1,'node':name,'definitionHash':row['definitionHash'],'source':body,'helpers':helper};(f.project/('Flow.node.json' if name=='calculate' else name+'.node.json')).write_text(json.dumps(record,ensure_ascii=False))
copy_mode='--copy' in sys.argv
implementation_id=x.impl;implementation_file='FlowBody.celem';graph_file='Flow.graph.json';guard=f.project/'Flow.node.json';owner=None
if copy_mode:
 import v536_field_definitions_ui as d
 owner=d.owner;module=f.n+'M11Rules';implementation_id=f.n+'M11OwnedCopy';implementation_file='M11Copy.celem'
 info=f.project/'FreeInfo.celem';call_signature=declaration(args,result,False)
 (f.project/'M11Rules.celem').write_text('module '+module+' {require '+feature+' '+call_signature+';}')
 info.write_text(info.read_text().replace('FreeInfo {','FreeInfo {module '+module+';',1))
 f.manifest=x.manifest;f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element M11Rules module "M11Rules.celem";registry Confectory.Build.DotNet',1))
 copied=f.metadata('implementationCopy',project=str(f.manifest),action='prepare',feature=feature,source=x.impl,target='common',implementation=implementation_id,owner=owner,ownerText=info.read_text())
 (f.project/implementation_file).write_text(copied['implementation']);info.write_text(copied['owner'])
 f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element M11OwnedCopy implementation "M11Copy.celem";registry Confectory.Build.DotNet',1))
 graph_file=copied['graphPath'];(f.project/graph_file).parent.mkdir(parents=True,exist_ok=True);graph=copied['graph'];(f.project/graph_file).write_text(json.dumps(graph,ensure_ascii=False))
 for row in copied['records']:
  file=f.project/pathlib.Path(graph_file).parent/row['relative'];file.parent.mkdir(parents=True,exist_ok=True);file.write_text(json.dumps(row['record'],ensure_ascii=False))
 guard=f.project/pathlib.Path(graph_file).parent/next(r['relative'] for r in copied['records'] if r['id']==('frame/' if nested else '')+'calculate')
 root=implementation_id+'/body:common';parent=root+('/graph:frame' if nested else '');child=parent+'/graph:calculate'
 (f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+feature+' as Flow '+call_signature+' in '+owner+';body common "Main.csbody";}')
 if '--shared' in sys.argv:
  file=f.project/'Vitals.celem';file.write_text(file.read_text().replace('Vitals {','Vitals {module '+module+';provide '+feature+' with '+implementation_id+';',1))
x.physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts}
def original():assert all(p.read_bytes()==v for p,v in x.physical.items())
def owner_binding():
 if not copy_mode:return {}
 schema=f.invoke('schema',{'id':owner})['state']['schema'];return {'owner':owner,'ownerHash':schema['textHash'],'ownerRevision':schema['revision']}

def source_path(node):return f.project/pathlib.Path(graph_file).parent/node['implementation']
def at(g):return next(n for n in g['nodes'] if n['id']=='frame')['graph'] if nested else g
def rpc(action,ok=True,**kw):return f.invoke('blueprint',{'action':action,'id':parent,**owner_binding(),**kw},ok)['result'].get('result')
def read(id=parent):return rpc('read',id=id)
def request(data,nonce=None,body=None,helper=None):
 import uuid
 row=next(r for r in data['nodes'] if r['id']=='calculate');item=next(r for r in data['sources'] if r['id']==row['sourceId']);binding={'graph':parent,'root':root,'node':'calculate','source':row['sourceId'],'definitionHash':row['definitionHash'],'sourceHash':item['hash']};plan={'nonce':nonce or uuid.uuid4().hex,'binding':binding}
 if body is not None:plan['source']=body
 if helper is not None:plan['helpers']=helper
 return {'id':parent,'attempt':uuid.uuid4().hex,'sourceProof':x.proof(data),'checkpointHash':data['checkpointHash'],'edits':[{'action':'internalizeNode','node':'calculate','definition':plan}]}
def build(name,increment=0,selection=None):
 run=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(x.manifest),'portable'],capture_output=True,text=True,env=f.env);(f.case/(name+'-build.log')).write_text(run.stdout+run.stderr);assert run.returncode==0,run.stdout[-4000:]+run.stderr[-4000:];report=json.loads(run.stdout);done=subprocess.run(report['run'],capture_output=True,text=True,env=f.env);(f.case/(name+'-run.json')).write_text(json.dumps({'exit':done.returncode,'stdout':done.stdout,'stderr':done.stderr}));assert done.returncode==7,(done.returncode,done.stderr)
 wanted=(str((41 if selection==-2 else 42)+increment)+'\n'+str((41 if selection==-2 else 42)+increment)+'\n'+('11' if selection==-2 else '12')+',16,'+str(26+increment) if refs else '\n'.join(str(mode)+':42,'+str(mode+i+increment)+':'+','.join(map(str,[i,i if (mode if selection is None else selection)==17 else 0,i if (mode if selection is None else selection)==99 else 0,i])) for mode in [-2,17,99] for i in [1,2]));assert done.stdout.strip()==wanted,(done.stdout,wanted);return done.stdout
