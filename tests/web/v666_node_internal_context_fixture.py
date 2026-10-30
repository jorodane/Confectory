"""확정된 직접 소유 whole-body의 this/재귀/scoped import/원문 위치 fixture."""
import copy,json,pathlib,subprocess,sys
import v666_node_internal_api as x
f=x.f;feature=x.feature;root=x.graph;refs='--refs' in sys.argv;void='--void' in sys.argv
# Original UI chooses this OS's explicit body before common. The UI case keeps
# an untouched Windows body so it actually enters common on Linux; the API case
# separately executes both common/portable and the explicit Linux body.
other_target='windows' if pathlib.Path(sys.argv[0]).name.endswith('_ui.py') else 'linux'
public_args=([{'type':'object','name':'state'},{'type':'long','name':'x','mode':'ref'},{'type':'long','name':'y','mode':'ref'},{'type':'long','name':'audit','mode':'out'}] if refs else [{'type':'object','name':'state'},{'type':'long','name':'amount'}]+([] if void else [{'type':'long','name':'count','mode':'out'}]));args=copy.deepcopy(public_args)
for arg,name in zip(args,['marker','a','b','c'] if refs else ['marker','input','copied']):arg['name']=name
signature={'args':args,'return':'void' if void else 'long'}
def declaration(parameters,named=True):return '('+','.join((a.get('mode','')+' '+a['type']+(' '+a['name'] if named else '')).strip() for a in parameters)+') -> '+signature['return']
function='function '+feature+' '+declaration(public_args)+' {provide '+feature+' with '+x.impl+';}'
original_impl='implementation '+x.impl+' for '+feature+' '+declaration(args)+' {import '+f.n+'Native as Scoped (long) -> long in '+f.n+'ChosenScope;body common "whole original.csbody";body '+other_target+' "other.csbody";}'
file_check='string File([global::System.Runtime.CompilerServices.CallerFilePath] string path="")=>global::System.IO.Path.GetFileName(path);\r\nstring literal=@"a\r\nb";\r\nstring Member([global::System.Runtime.CompilerServices.CallerMemberName] string member="")=>member;\r\nlong proof=File()=="whole original.csbody"&&Member()=="Invoke"&&GetType()==typeof(IImports).DeclaringType&&literal.Contains("\\r\\n")?0:10000;\r\nIImports same=this.calls;\r\n'
if refs:
 source='// 원래 whole-body 😀\r\nvar seen=(global::System.Collections.Generic.List<long>)marker;\r\nif(seen.Count==0){seen.Add(-1);return this.Invoke(marker,ref a,ref b,out c);}\r\nseen.Add(a);\r\n'+file_check+'a=10;b+=a;c=a+b;\r\nreturn same.Scoped.Invoke(a)+b+c+proof;\r\n'
 other='c=a+b;return a+b+100;';main='var seen=new global::System.Collections.Generic.List<long>();long n=5;long v=calls.Flow.Invoke(seen,ref n,ref n,out n);global::System.Console.WriteLine(v+","+n+","+seen.Count);seen=new();long a=5,b=6;v=calls.Flow.Invoke(seen,ref a,ref b,out long c);global::System.Console.WriteLine(v+","+a+","+b+","+c+","+seen.Count);return 7;';expected='123,40,2\n55,10,16,26,2'
elif void:
 source='// 원래 void whole-body\r\nif(input<0){this.Invoke(marker,-input);return;}\r\n'+file_check+'((global::System.Collections.Generic.List<long>)marker).Add(same.Scoped.Invoke(input)+proof);\r\nreturn;\r\n';other='((global::System.Collections.Generic.List<long>)marker).Add(input+100);';main='var seen=new global::System.Collections.Generic.List<long>();calls.Flow.Invoke(seen,-2);global::System.Console.WriteLine(seen[0]+","+seen.Count);return 7;';expected='5,1'
else:
 source='// 원래 whole-body 😀\r\nif(input<0)return this.Invoke(marker,-input,out copied);\r\n'+file_check+'((global::System.Collections.Generic.List<long>)marker).Add(input);\r\ncopied=input*10;\r\nreturn same.Scoped.Invoke(input)+proof;\r\n';other='copied=input;return input+100;';main='var seen=new global::System.Collections.Generic.List<long>();long v=calls.Flow.Invoke(seen,-2,out long count);global::System.Console.WriteLine(v+","+count+","+seen.Count);return 7;';expected='5,20,1'
for name,text in [('Flow.celem',function),('FlowBody.celem',original_impl),('whole original.csbody',source),('other.csbody',other),('Native.celem','function '+f.n+'Native (long input) -> long {provide '+f.n+'Native with '+f.n+'NativeWrongBody;}'),('NativeWrongBody.celem','implementation '+f.n+'NativeWrongBody for '+f.n+'Native (long input) -> long {body common "wrong.csbody";}'),('wrong.csbody','return input+30;'),('ChosenScope.celem','object '+f.n+'ChosenScope {provide '+f.n+'Native with '+f.n+'NativeBody;}'),('MainBody.celem','implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+feature+' as Flow '+declaration(public_args,False)+';body common "Main.csbody";}'),('Main.csbody',main)]: (f.project/name).write_bytes(text.encode())
manifest=x.manifest;manifest.write_text(manifest.read_text().replace('registry Confectory.Build.DotNet','element NativeWrongBody implementation "NativeWrongBody.celem";element ChosenScope object "ChosenScope.celem";registry Confectory.Build.DotNet'))
prepared=f.metadata('blueprintConversion',project=str(manifest),id=x.impl,text=original_impl,target='common',graphPath='Flow.graph.json',nodePath='Flow.node.json');graph=prepared['graph'];assert graph['profile']=='sync-acyclic-property-v1'
graph['nodes'][0]['id']='calculate';graph['entry']='calculate'
def rename(value):
 if isinstance(value,dict):
  for key,child in value.items():
   if key in ['from','to','node'] and child=='body':value[key]='calculate'
   else:rename(child)
 elif isinstance(value,list):
  for child in value:rename(child)
rename(graph);context=prepared['context'];implementation=prepared['implementation'];definitions=f.metadata('featureBlueprintNodes',featureSource=function,featureContracts={f.n+'Native':(f.project/'Native.celem').read_text()},implementationContext=context,bodyTarget='common',graph=graph);assert definitions['state']=='node-definitions',definitions;record=copy.deepcopy(prepared['node']);record['node']='calculate';record['definitionHash']=next(row for row in definitions['nodes'] if row['id']=='calculate')['definitionHash'];assert record['source']==source
for name,text in [('FlowBody.celem',implementation),('Flow.graph.json',json.dumps(graph,ensure_ascii=False)),('Flow.node.json',json.dumps(record,ensure_ascii=False))]: (f.project/name).write_bytes(text.encode())
parent=root;child=root+'/graph:calculate';original_id=root+'/node:calculate';leaf=original_id+'/node:body';x.physical={p:p.read_bytes() for p in f.project.iterdir() if p.is_file()}
def rpc(action,ok=True,**kw):return f.invoke('blueprint',{'action':action,'id':root,**kw},ok)['result'].get('result')
def read(id=root):return rpc('read',id=id)
def request(data,nonce=None,text=None):return x.request(data,nonce,text)
def build(name,increment=0,target='portable'):
 run=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(manifest),target],capture_output=True,text=True,env=f.env);(f.case/(name+'-build.log')).write_text(run.stdout+run.stderr);assert run.returncode==0,run.stdout[-3000:]+run.stderr[-3000:];report=json.loads(run.stdout);result=subprocess.run(report['run'],capture_output=True,text=True,env=f.env);(f.case/(name+'-run.json')).write_text(json.dumps({'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr}));assert result.returncode==7,(result.returncode,result.stdout,result.stderr)
 if target=='portable':
  wanted='\n'.join(str(int(row.split(',')[0])+increment)+','+row.split(',',1)[1] for row in expected.splitlines());assert result.stdout.strip()==wanted,(result.stdout,wanted)
 return result.stdout
