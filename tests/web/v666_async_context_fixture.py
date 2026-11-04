"""Confirmed owned native whole-body, scoped import and an explicit graph caller."""
import copy,json,hashlib,subprocess,uuid
import v536_wide_mixed as f
feature=f.n+'Flow';impl=f.n+'FlowBody';graph=impl+'/body:common';caller=f.n+'MainBody/body:common';manifest=f.project/'project.cproj'
function='function '+feature+' (object state,long amount,out long count) -> long {provide '+feature+' with '+impl+';}'
implementation='implementation '+impl+' for '+feature+' (object marker,long input,out long copied) -> long {import '+f.n+'CtxDouble as Scoped (long) -> long in '+f.n+'CtxScope;body common "whole original.csbody";}'
source='// 원래 whole-body 😀\r\nif(input<0)return this.Invoke(marker,-input,out copied);\r\nIImports same=this.calls;\r\nstring File([global::System.Runtime.CompilerServices.CallerFilePath] string file="")=>global::System.IO.Path.GetFileName(file);\r\nstring Member([global::System.Runtime.CompilerServices.CallerMemberName] string name="")=>name;\r\nstring literal=@"a\r\nb";\r\nif(GetType()!=typeof(IImports).DeclaringType||File()!="whole original.csbody"||Member()!="Invoke"||!literal.Contains("\\r\\n"))throw new global::System.Exception("original context changed");\r\ncopied=input*10;\r\n((global::System.Collections.Generic.List<long>)marker).Add(input);\r\nreturn same.Scoped.Invoke(input);\r\n'
items={'Flow':('function',function),'FlowBody':('implementation',implementation),'CtxDouble':('function','function '+f.n+'CtxDouble (long input) -> long {}'),'CtxDoubleBody':('implementation','implementation '+f.n+'CtxDoubleBody for '+f.n+'CtxDouble (long input) -> long {body common "ctx-double.csbody";}'),'CtxScope':('object','object '+f.n+'CtxScope {provide '+f.n+'CtxDouble with '+f.n+'CtxDoubleBody;}')}
for name,(kind,text)in items.items():
 (f.project/(name+'.celem')).write_text(text);manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' '+kind+' "'+name+'.celem";registry Confectory.Build.DotNet',1))
(f.project/'whole original.csbody').write_bytes(source.encode());(f.project/'ctx-double.csbody').write_text('return input+3;')
prepared=f.metadata('blueprintConversion',project=str(manifest),id=impl,text=implementation,target='common',graphPath='Flow.graph.json',nodePath='Flow.node.json');root=prepared['graph'];context=prepared['context'];assert prepared['node']['source']==source
for name,text in [('FlowBody.celem',prepared['implementation']),('Flow.graph.json',json.dumps(root,ensure_ascii=False)),('Flow.node.json',json.dumps(prepared['node'],ensure_ascii=False))]:(f.project/name).write_text(text)
main=(f.project/'Main.celem').read_text();main_id=f.n+'Main';signature={'args':[{'type':'object','name':'state'},{'type':'long','name':'amount'},{'type':'long','name':'count','mode':'out'}],'return':'long'}
cg={'schema':1,'profile':'sync-acyclic-switch-v1','feature':main_id,'contractHash':f.metadata('blueprintPrepareFeature',id=main_id,text='function '+main_id+' () -> int {}',implementation=f.n+'MainBody',graphPath='Main.graph.json',nodePath='Create.node.json')['graph']['contractHash'],'entry':'create','nodes':[
 {'id':'create','kind':'code','control':'next','intent':'Create original receiver','signature':{'args':[],'return':'object'},'arguments':{},'implementation':'Create.node.json'},
 {'id':'invoke','kind':'call','control':'next','intent':'Original direct caller','feature':feature,'signature':signature,'arguments':{'state':{'node':'create'},'amount':{'constant':-2}}},
 {'id':'after','kind':'code','control':'next','intent':'Read outputs after call','signature':{'args':[{'type':'long','name':'value'},{'type':'long','name':'count'},{'type':'object','name':'state'}],'return':'void'},'arguments':{'value':{'node':'invoke'},'count':{'node':'invoke','output':'count'},'state':{'node':'create'}},'implementation':'After.node.json'}],
 'edges':[{'from':'create','port':'next','to':'invoke'},{'from':'invoke','port':'next','to':'after'},{'from':'after','port':'next','to':'exit:return'}],'exits':{'return':{'constant':7}}}
definitions=f.metadata('featureBlueprintNodes',featureSource=main,graph=cg,featureContracts={feature:function});assert definitions['state']=='node-definitions',definitions
for node,path,text in [('create','Create.node.json','return new global::System.Collections.Generic.List<long>();'),('after','After.node.json','global::System.Console.WriteLine(value+","+count+","+((global::System.Collections.Generic.List<long>)state).Count);')]:
 (f.project/path).write_text(json.dumps({'schema':1,'node':node,'definitionHash':next(n['definitionHash']for n in definitions['nodes']if n['id']==node),'source':text}))
alias='fg_call_'+hashlib.sha256(feature.encode()).hexdigest()[:24]
(f.project/'Main.graph.json').write_text(json.dumps(cg));(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+main_id+' () -> int {import '+feature+' as '+alias+' (object,long,out long) -> long;blueprint common "Main.graph.json";}')
physical={p:p.read_bytes()for p in f.project.rglob('*')if p.is_file()and '.confectory'not in p.parts};initial_edges=copy.deepcopy(root['edges'])
def original():assert all(p.read_bytes()==v for p,v in physical.items())
def unchanged():
 assert (f.project/'whole original.csbody').read_bytes()==source.encode();assert json.loads((f.project/'Flow.node.json').read_text())['source']==source;assert(f.project/'CtxScope.celem').read_bytes()==physical[f.project/'CtxScope.celem'];assert(f.project/'ctx-double.csbody').read_bytes()==physical[f.project/'ctx-double.csbody']
def read(id=graph):return f.invoke('blueprint',{'action':'read','id':id})['result']['result']
def proof(d):return json.dumps(sorted([[r['id'],r['revision'],r['hash']]for r in d['sources']]),separators=(',',':'))
def rpc(action,success=True,**body):return f.invoke('blueprint',{'action':action,**body},success)['result'].get('result')
def request(d,id=graph,enabled=True,nodes=None):return {'id':id,'attempt':uuid.uuid4().hex,'checkpointHash':d['checkpointHash'],'sourceProof':proof(d),'edits':[{'action':'asyncTransition','node':'$root','definition':{'enabled':enabled,'nodes':nodes or []}}]}
def checkpoint():return {str(p):p.read_bytes()for p in f.project.glob('.confectory/edit-workspaces/*/draft.json')}
def build(name):
 r=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(manifest),'portable'],env=f.env,text=True,capture_output=True);(f.case/(name+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout[-5000:]+r.stderr
 result=subprocess.run(json.loads(r.stdout)['run'],env=f.env,text=True,capture_output=True);(f.case/(name+'-run.json')).write_text(json.dumps({'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr}));assert(result.returncode,result.stdout.strip())==(7,'5,20,1'),(result.returncode,result.stdout,result.stderr)
