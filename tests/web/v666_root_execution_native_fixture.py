"""M12 native whole-body entry: original receiver/recursion/scoped import remains native."""
import copy,json,re
import v666_root_execution_fixture as base
f=base.f
feature=base.feature;impl=base.impl;graph=base.graph;caller=base.caller
native_mode=True;data_mode=True;out_mode=True;result_code=5
initial_stdout='native:5\nafter:5';final_stdout='native:5'
function=base.function;manifest=base.manifest
native=f.n+'Native';scope=f.n+'ChosenScope'
other='function '+native+' (long value) -> long {provide '+native+' with '+f.n+'WrongBody;}'
implementation='implementation '+impl+' for '+feature+' (long input,out int copied) -> void {import '+native+' as Scoped (long) -> long in '+scope+';blueprint common "Flow.graph.json";}'
context={'implementation':impl,'feature':feature,'signature':{'args':[{'type':'long','name':'input'},{'type':'int','name':'copied','mode':'out'}],'return':'void'},'imports':{'Scoped':{'feature':native,'scope':scope,'signature':{'args':[{'type':'long','name':'arg0'}],'return':'long'}}}}
# Use the exact parsed contract, including import positional names, from the lift API.
(f.project/'FlowBody.celem').write_text(implementation.replace('blueprint common "Flow.graph.json"','body common "whole original.csbody"'))
source='// 원래 native 문맥·CRLF 😀\r\nif(input<0){this.Invoke(-input,out copied);return;}\r\nstring File([global::System.Runtime.CompilerServices.CallerFilePath] string path="")=>global::System.IO.Path.GetFileName(path);\r\nstring Member([global::System.Runtime.CompilerServices.CallerMemberName] string member="")=>member;\r\nstring literal=@"a\r\nb";\r\nIImports same=this.calls;\r\ncopied=checked((int)same.Scoped.Invoke(input));\r\nif(File()!="whole original.csbody"||Member()!="Invoke"||GetType()!=typeof(IImports).DeclaringType||!literal.Contains("\\r\\n"))throw new global::System.InvalidOperationException("native identity changed");\r\nglobal::System.Console.WriteLine("native:"+copied);\r\n'
for name,text in [('whole original.csbody',source),('Native.celem',other),('WrongBody.celem','implementation '+f.n+'WrongBody for '+native+' (long value) -> long {body common "wrong.csbody";}'),('wrong.csbody','return value+30;'),('NativeBody.celem','implementation '+f.n+'NativeBody for '+native+' (long value) -> long {body common "right.csbody";}'),('right.csbody','return value+3;'),('ChosenScope.celem','object '+scope+' {provide '+native+' with '+f.n+'NativeBody;}')]: (f.project/name).write_bytes(text.encode())
manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element WrongBody implementation "WrongBody.celem";element ChosenScope object "ChosenScope.celem";registry Confectory.Build.DotNet',1))
# Keep the declared project focused: inherited base fixture postCall consumers target its original helper signature.
manifest.write_text(re.sub(r'element (\w+) \w+ "[^"]+";',lambda m:m.group() if m[1] in {'Main','MainBody','Flow','FlowBody','Native','NativeBody','WrongBody','ChosenScope'} else '',manifest.read_text()))
lift=f.metadata('blueprintConversion',project=str(manifest),id=impl,text=(f.project/'FlowBody.celem').read_text(),target='common',graphPath='Flow.graph.json',nodePath='Native.node.json')
context=lift['context'];assert lift['node']['source']==source
root=copy.deepcopy(base.root);root['entry']='native';choose=root['nodes'][0]
choose['signature']['args']=[{'type':'long','name':'amount'}];choose['arguments']={'amount':{'input':'amount'}}
body=copy.deepcopy(lift['graph']['nodes'][0]);body['id']='native';root['nodes'].insert(0,body);root['edges'].insert(0,base.edge('native','choose'))
for node in root['nodes']:
 if node['kind']=='export':node['arguments']['value']={'node':'native','output':'copied'}
(f.project/'FlowBody.celem').write_text(lift['implementation']);(f.project/'Flow.graph.json').write_text(json.dumps(root,ensure_ascii=False))
defs=f.metadata('featureBlueprintNodes',featureSource=function,implementationContext=context,bodyTarget='common',featureContracts={native:other},graph=root);assert defs['state']=='node-definitions',defs
for id,file,cs in [('native','Native.node.json',source),('choose','Flow.node.json','return amount<0?Result.Positive:Result.Negative;')]:
 row=next(n for n in defs['nodes'] if n['id']==id);(f.project/file).write_text(json.dumps({'schema':1,'node':id,'definitionHash':row['definitionHash'],'source':cs},ensure_ascii=False))
cg=copy.deepcopy(base.cg);cg['nodes'][0]['arguments']['amount']={'constant':-2};(f.project/'Main.graph.json').write_text(json.dumps(cg))
for file in ['Native.celem','ChosenScope.celem','whole original.csbody']:(f.project/file).chmod(0o400)
physical={p:p.read_bytes() for p in f.project.rglob('*') if p.is_file() and '.confectory' not in p.parts};base.physical=physical
original=base.original;read=base.read;rpc=base.rpc;checkpoint=base.checkpoint;proof=base.proof

def build(*args,**kwargs):
 base.build(*args,**kwargs)
 for file in ['whole original.csbody','Native.node.json','Flow.node.json','Native.celem','ChosenScope.celem']:
  p=f.project/file;assert p.read_bytes()==physical[p],p

def plan(data):return base.plan(data)
def request(data,selected=None):return base.request(data,selected or plan(data))
