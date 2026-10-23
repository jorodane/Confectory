"""Bounded original enum wrapper compiler, using only isolated fake native code.
No provider/account/project Run. Normal wrapper creation UI is NOT exercised.
"""
import copy,hashlib,json,os,pathlib,re,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();dotnet='/workspace/toolchains/dotnet-10.0.401/dotnet';host=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-wrapper-enum-compiler-'));checks=[]
env=os.environ.copy();env.update(DOTNET_CLI_HOME='/tmp/confectory-dotnet10-final',NUGET_PACKAGES='/tmp/confectory-site-nuget')
def sdk(op,ok=True,**body):
 p=subprocess.run([dotnet,str(host)],input=json.dumps({'operation':op,**body}),text=True,capture_output=True,env=env,check=True);v=json.loads(p.stdout);assert v['ok']==ok,v;return v.get('result') if ok else v
def check(text):checks.append(text);print('PASS '+text,flush=True)
source='function Known::Original (ref long value,long[] trace,out long[] nums,out long hidden) -> void {value blueprintPublishedOutputs = '+json.dumps(json.dumps(['nums']))+';}'
execution={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0},{'id':'done','name':'완료','value':17}]}
body='trace[0] += 10;var local=context.nums;local[0]=99;if(originalBranch!=OriginalResult.NoBranch)throw new System.Exception();return Pick();';helpers='private static Result Pick(){return Result.완료;}'
prepared=sdk('blueprintCallWrapper',functionText=source,executionEnum=execution,source=body,helpers=helpers);assert [p.get('id') for p in prepared['parts'] if 'id' in p]==['enum','body','helpers'] and prepared['originalOutcome']=='native-void-completion-only' and not prepared['executed'] and not prepared['sourceWritten'];expected=prepared['contractHash'];check('original fixed invocation/context/OriginalResult plus editable Result/body/helper regions are prepared separately; no native data return is reinterpreted as an outcome')
for mutate in ('duplicate','primary','extra','unknown'):
 e=copy.deepcopy(execution)
 if mutate=='duplicate':e['members'][1]['value']=0
 elif mutate=='primary':e['primary']='gone'
 elif mutate=='extra':e['access']='project'
 else:e['members'][1]['name']='Result'
 sdk('blueprintCallWrapper',False,functionText=source,executionEnum=e)
sdk('blueprintCallWrapper',False,functionText=source.replace('-> void','-> long'),executionEnum=execution);sdk('blueprintCallWrapper',False,functionText=source,executionEnum=execution,expected='0'*64);check('invalid enum identity/names/values, arbitrary authority fields, stale publication and native data-return migration refuse before writing or execution')
(case/'Test.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><Nullable>disable</Nullable><TreatWarningsAsErrors>true</TreatWarningsAsErrors></PropertyGroup></Project>');(case/'NuGet.Config').write_text('<configuration><packageSources><clear /></packageSources></configuration>')
main='''using System;
public static class Test {public static int calls;
 sealed class Original:IOriginal {public void Invoke(ref long value,long[] trace,out long[] nums,out long hidden){calls++;value+=1;trace[0]++;nums=new long[]{5};hidden=6;}}
 public static void Main(){long value=3;var trace=new long[1];var result=Function.Execute(new Original(),ref value,trace,out var nums,out long hidden);if((int)result!=17||value!=4||nums[0]!=5||hidden!=6||calls!=1||trace[0]!=11)throw new Exception("wrapper changed invocation/storage/snapshot/outcome");Console.WriteLine("PASS Wrapper");}}
'''
def compile(code,restore=False):
 (case/'Program.cs').write_text(code);p=subprocess.run([dotnet,'build',str(case/'Test.csproj'),'--nologo']+(['--configfile',str(case/'NuGet.Config')] if restore else ['--no-restore']),text=True,capture_output=True,env=env);(case/'compile-last.log').write_text(p.stdout+p.stderr);return p
p=compile(main+''.join(part['text'] for part in prepared['parts']),True);assert p.returncode==0,p.stdout
p=subprocess.run([dotnet,str(case/'bin/Debug/net10.0/Test.dll')],text=True,capture_output=True,env=env);assert p.returncode==0 and 'PASS Wrapper' in p.stdout,(p.stdout,p.stderr);check('generated original enum wrapper really compiles and invokes a fake original once, preserving native ref/out outputs, read-only snapshot array copies and selected Result value')
args=[{'type':'long','name':'value','mode':'ref'},{'type':'long[]','name':'trace'},{'type':'long[]','name':'nums','mode':'out'},{'type':'long','name':'hidden','mode':'out'}];rootargs=args[:2];signature={'args':rootargs,'return':'void'};fingerprint=hashlib.sha256(json.dumps({'feature':'Known::Caller','signature':signature},sort_keys=True,separators=(',',':')).encode()).hexdigest();code_sig={'args':[{'type':'long[]','name':'trace'}],'return':'void'}
graph={'schema':1,'profile':'sync-acyclic-switch-v1','feature':'Known::Caller','contractHash':fingerprint,'entry':'wrapped','nodes':[{'id':'wrapped','kind':'call','control':'switch','intent':'Original wrapped enum','feature':'Known::Original','signature':{'args':args,'return':'void'},'arguments':{'value':{'input':'value'},'trace':{'input':'trace'}},'executionEnum':execution,'postCall':{'mode':'execution-enum','contractHash':expected,'source':body,'helpers':helpers}},{'id':'case','kind':'code','control':'next','branchOwner':'wrapped','intent':'Existing selected enum region','signature':code_sig,'arguments':{'trace':{'input':'trace'}},'implementation':'case.node.json'},{'id':'tail','kind':'code','control':'next','intent':'Existing ordinary continuation','signature':code_sig,'arguments':{'trace':{'input':'trace'}},'implementation':'tail.node.json'}],'edges':[{'from':'wrapped','port':'next','to':'tail'},{'from':'wrapped','port':'case:done','to':'case'},{'from':'case','port':'next','to':'return:wrapped'}],'exits':{}}
graph['nodes'].append({'id':'unused','kind':'code','control':'next','intent':'Preserved disconnected original action','signature':{'args':[],'return':'void'},'arguments':{},'implementation':'unused.node.json'})
request={'featureSource':'function Known::Caller (ref long value,long[] trace) -> void {}','featureContracts':{'Known::Original':source},'graph':graph};defs=sdk('featureBlueprintNodes',**request);assert defs['state']=='node-definitions',defs;assert next(n for n in defs['nodes'] if n['id']=='wrapped')['postCallEditor']['mode']=='execution-enum';records={n['id']:{'schema':1,'node':n['id'],'definitionHash':n['definitionHash'],'source':'return;' if n['id']=='unused' else 'trace[0] += '+('100' if n['id']=='case' else '1000')+';'} for n in defs['nodes'] if n['id']!='wrapped'};assembled=sdk('featureBlueprintAssemble',implementations=records,**request);assert assembled['state']=='source-assembled',assembled
alias=assembled['imports'][0]['alias'];members=assembled['members'];iface=re.search(r'Execute\((\S+) @original',members)[1];ns,local=iface.removeprefix('global::').rsplit('.',1)
# Compile the actual graph assembler output, not a hand-written dispatcher.
code='''using System;
namespace '''+ns+''' {public interface '''+local+''' {void Invoke(ref long value,long[] trace,out long[] nums,out long hidden);}}
public class Fake:'''+iface+''' {public static int count;public void Invoke(ref long value,long[] trace,out long[] nums,out long hidden){count++;value++;trace[0]++;nums=new long[]{5};hidden=6;}}
public class Calls {public '''+iface+' '+alias+'''=new Fake();}
public class Graph {public Calls calls=new();public void Invoke(ref long value,long[] trace){\n'''+assembled['body']+'\n}\n'+members+'''}
public static class Test {public static void Main(){long value=3;var trace=new long[1];new Graph().Invoke(ref value,trace);if(value!=4||trace[0]!=1111||Fake.count!=1)throw new Exception("wrong enum dispatch or sequential continuation");Console.WriteLine("PASS Graph");}}
'''
p=compile(code);assert p.returncode==0,p.stdout;p=subprocess.run([dotnet,str(case/'bin/Debug/net10.0/Test.dll')],text=True,capture_output=True,env=env);assert p.returncode==0 and 'PASS Graph' in p.stdout,(p.stdout,p.stderr);check('actual graph assembler emits and compiles the existing enum dispatch followed by main continuation, with one fake original invocation and no new execution model')
bad_records=copy.deepcopy(records);bad_records['unused']['source']='MissingMember();';bad_assembled=sdk('featureBlueprintAssemble',implementations=bad_records,**request);assert bad_assembled['state']=='source-assembled';bad_code=code.replace(assembled['members'],bad_assembled['members']).replace(assembled['body'],bad_assembled['body']);bad_code=re.sub(r'^#line ([0-9]+) \".*\"$',lambda m:'#line '+m[1]+' '+json.dumps(str(case/'source-map.cs')),bad_code,flags=re.M);p=compile(bad_code);assert p.returncode!=0 and 'CS0103' in p.stdout,p.stdout
check('omitting unreachable terminal labels does not omit disconnected node bodies: their invalid C# still fails actual warning-strict compilation')
for change in ('missing-mode','unknown-mode','stale-publication','nonvoid','next-mode'):
 g=copy.deepcopy(graph);contracts={'Known::Original':source};n=g['nodes'][0]
 if change=='missing-mode':del n['postCall']['mode']
 elif change=='unknown-mode':n['postCall']['mode']='permission'
 elif change=='stale-publication':n['postCall']['contractHash']='0'*64
 elif change=='nonvoid':contracts['Known::Original']=source.replace('-> void','-> long');n['signature']['return']='long'
 else:n['control']='next'
 invalid=sdk('featureBlueprintAssemble',inspectStalePostCalls=True,implementations=records,**{**request,'graph':g,'featureContracts':contracts});assert invalid['state']=='invalid',invalid
check('actual graph compiler rejects missing/unknown explicit enum mode, stale publication even with inspection flag, next-mode confusion and unmapped native returns')
for bad,diagnostic in [('context.nums=null;return Result.완료;','CS0200'),('return context.hidden==0?Result.완료:Result.NoBranch;','CS1061'),('return OriginalResult.완료==OriginalResult.NoBranch?Result.NoBranch:Result.완료;','CS0117')]:
 p=compile(main+''.join(x['text'] for x in sdk('blueprintCallWrapper',functionText=source,executionEnum=execution,source=bad)['parts']));assert p.returncode!=0 and diagnostic in p.stdout,p.stdout
check('C# rejects context writes/nonpublished output reads and fabricated original execution members; original native completion has only the fixed NoBranch outcome')
record={'checks':checks,'evidence':str(case),'actualGraphAssembler':True,'fakeNativeOnly':True,'normalCreationUi':False,'actualWindows':False,'accountOrInference':False,'nativeDataReturns':False};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
