"""v508 post-call output snapshot/source contract preparation; isolated SDK/compiler only.
This is not acceptance of the call-wrapper UI or actual provider/account execution.
"""
import copy,json,os,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();dotnet='/workspace/toolchains/dotnet-10.0.401/dotnet'
host=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'
case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-public-output-contract-'));checks=[]
env=os.environ.copy();env.update(DOTNET_CLI_HOME='/tmp/confectory-dotnet10-final',NUGET_PACKAGES='/tmp/confectory-site-nuget')
def sdk(op,good=True,**body):
 p=subprocess.run([dotnet,str(host)],input=json.dumps({'operation':op,**body}),text=True,capture_output=True,env=env,check=True)
 r=json.loads(p.stdout);assert (r.get('ok') is not False)==good,r;return r.get('result') if good else r
def check(text):checks.append(text);print('PASS '+text,flush=True)
fixture=repo.parent/'scratch/v508-elements/actual13-source-fixture/owned project'
fn=(fixture/'elements/Serial.celem').read_text();impl=(fixture/'elements/SerialBlueprintBody.celem').read_text();graph=json.loads(next((fixture/'blueprints').glob('*.graph.json')).read_text())
sig=sdk('inspect',text=fn)['signature'];args=[{'name':a['Name'],'type':a['Type'],**({'mode':a['Mode']} if a.get('Mode') else {})} for a in sig['Args']]
plan={'args':args,'returnType':sig['return'],'remap':{a['name']:a['name'] for a in args}}
def prepare(p,good=True,function=fn,implementation=impl,g=graph):return sdk('blueprintRootContract',good,functionText=function,text=implementation,bodyTarget='common',graph=g,plan=p)
ref=copy.deepcopy(plan);ref['args'][0]['mode']='ref'
sdk0=prepare(ref,False)
ref['inputModes']={'seed':'ref'};prepared=prepare(ref)
assert prepared['graph']['profile']=='sync-acyclic-ref-v1' and prepared['graph']['nodes'][0]['arguments']==graph['nodes'][0]['arguments']
reverse=copy.deepcopy(plan);reverse['inputModes']={'seed':'value'}
back=prepare(reverse,function=prepared['function'],implementation=prepared['implementation'],g=prepared['graph'])
assert sdk('inspect',text=back['function'])['signature']==sig
check('explicit same-input value/ref preparation preserves all storage/value uses and matching implementation; implicit mode change refuses')
for edits in [{'seed':'out'},{'missing':'ref'},{'seed':None}]:
 bad=copy.deepcopy(ref);bad['inputModes']=edits;prepare(bad,False)
bad=copy.deepcopy(ref);bad['remap']['seed']=None;prepare(bad,False)
bad=copy.deepcopy(ref);bad['args'][0]['type']='int';prepare(bad,False)
check('unknown/out/null mode, missing remap and incompatible type cannot use the explicit input-mode route')
pub=copy.deepcopy(plan);pub['publicOutputs']=['return'];p=prepare(pub)
contract=sdk('blueprintOutputSnapshot',functionText=p['function'])
assert [f['name'] for f in contract['fields']]==['return'] and 'seed' not in contract['contextSource'] and not contract['executed']
assert sdk('blueprintOutputSnapshot',functionText=fn)['fields']==[]
sdk('blueprintOutputSnapshot',False,functionText=fn,expected=contract['contractHash'])
assert sdk('blueprintOutputSnapshot',functionText=p['function'],expected=contract['contractHash'])==contract
check('published contract selects only declared output fields; missing publication grants nothing and revocation invalidates the exact consumer receipt')
for selected in [['seed'],['return','return'],['missing'],[None],['return']*66]:
 bad=copy.deepcopy(plan);bad['publicOutputs']=selected;prepare(bad,False)
for malformed in ['value blueprintPublishedOutputs = true;','value blueprintPublishedOutputs = "{}";','value blueprintPublishedOutputs = "[null]";']:
 sdk('blueprintOutputSnapshot',False,functionText=fn.replace('{','{ '+malformed,1))
check('input-as-output, duplicate/unknown/null/overbudget publication and malformed legacy metadata fail closed')
# Generated fixed context is compiled and exercised without an engine/provider.
extra='function Snapshot.Case::Source (out long[] values, out string privateText, out int SourceContext, out long[] snapshot0) -> long {'
extra+='value blueprintPublishedOutputs = '+json.dumps(json.dumps(['return','values','SourceContext','snapshot0']))+';}'
capture=sdk('blueprintOutputSnapshot',functionText=extra);fields=capture['fields'];assert [f['name'] for f in fields]==['return','values','SourceContext','snapshot0'];assert fields[2]['member']!='SourceContext' and 'privateText' not in capture['contextSource']
(case/'Test.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><Nullable>disable</Nullable></PropertyGroup></Project>')
(case/'NuGet.Config').write_text('<configuration><packageSources><clear /></packageSources></configuration>')
refsource='function Snapshot.Case::Ref (ref long original, out long context) -> long {value blueprintPublishedOutputs = '+json.dumps(json.dumps(['return','context']))+';}'
refcapture=sdk('blueprintOutputSnapshot',functionText=refsource)
assert refcapture['sourceParameter']=='_original' and refcapture['contextVariable']=='_context'
code="""using System;
static class Program {
 static int calls;
 sealed class Original : IOriginal { public long Invoke(out long[] values,out string privateText,out int SourceContext,out long[] snapshot0) { calls++;values=new long[]{9223372036854775804};privateText="kept";SourceContext=11;snapshot0=null;return 7; } }
 static SourceContext Capture(IOriginal @original,out long[] values,out string privateText,out int SourceContext,out long[] snapshot0) {
"""+capture['originalCall']+'return @'+capture['contextVariable']+""";}
 static void Main(){ long[] data;var c=Capture(new Original(),out data,out var privateText,out _,out _);
 data[0]=0;if(c.@values[0]!=9223372036854775804)throw new Exception("capture aliases source array");
 var read=c.@values;read[0]=1;if(c.@values[0]!=9223372036854775804)throw new Exception("getter aliases captured array");
 if(c.@return!=7||c.@SourceContext_2!=11||c.@snapshot0!=null||calls!=1||privateText!="kept")throw new Exception("snapshot values/call count");
 foreach(var prop in typeof(SourceContext).GetProperties())if(prop.CanWrite)throw new Exception("writable context");
 RefCase.Test.Run();Console.WriteLine("PASS snapshot scalar/array/null/readonly/collision");
 }
}
"""+capture['contextSource']+capture['originalInterface']
code+='namespace RefCase {\n'+refcapture['contextSource']+refcapture['originalInterface']+"""
public static class Test {
 static int calls;
 sealed class Original : IOriginal { public long Invoke(ref long original,out long context){calls++;original+=2;context=original+1;return original+2;} }
 static SourceContext Capture(IOriginal @_original,ref long original,out long context) {
"""+refcapture['originalCall']+'return @'+refcapture['contextVariable']+""";}
 public static void Run(){long input=3;var c=Capture(new Original(),ref input,out long value);if(input!=5||value!=6||c.@return!=7||c.@context!=6||calls!=1)throw new Exception("ref/out post-call capture");}
}}"""
(case/'Program.cs').write_text(code)
p=subprocess.run([dotnet,'build',str(case/'Test.csproj'),'--configfile',str(case/'NuGet.Config'),'--nologo'],text=True,capture_output=True,env=env);(case/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,(p.stdout,p.stderr)
p=subprocess.run([dotnet,str(case/'bin/Debug/net10.0/Test.dll')],text=True,capture_output=True,env=env);assert p.returncode==0 and 'PASS snapshot' in p.stdout,(p.stdout,p.stderr)
check('generated post-call context compiles and executes in isolation: selected scalar, capture/read array copies, null, readonly properties and member collisions')
for fragment in ['c.@return=99;','_ = c.privateText;']:
 (case/'Program.cs').write_text(code.replace('Console.WriteLine("PASS snapshot',fragment+'\n Console.WriteLine("PASS snapshot'))
 p=subprocess.run([dotnet,'build',str(case/'Test.csproj'),'--no-restore','--nologo'],text=True,capture_output=True,env=env);assert p.returncode!=0 and ('CS0200' in p.stdout if 'return' in fragment else 'CS1061' in p.stdout),p.stdout
check('actual C# compiler refuses snapshot writes and referencing a non-published output')
(case/'Program.cs').write_text(code)
record={'checks':checks,'evidence':str(case),'actualEngine':False,'nativeWindows':False,'callWrapperUiConnected':False,'accountOrInference':False};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
