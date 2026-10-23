"""Actual fixed-call/After compiler fixture and fail-closed graph contract checks.
No live provider, account, project Run, or filesystem source publication.
"""
import copy,hashlib,json,os,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();dotnet='/workspace/toolchains/dotnet-10.0.401/dotnet';host=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-post-call-compiler-'));checks=[]
env=os.environ.copy();env.update(DOTNET_CLI_HOME='/tmp/confectory-dotnet10-final',NUGET_PACKAGES='/tmp/confectory-site-nuget')
def sdk(operation,ok=True,**body):
 p=subprocess.run([dotnet,str(host)],input=json.dumps({'operation':operation,**body}),text=True,capture_output=True,env=env,check=True);v=json.loads(p.stdout);assert v['ok']==ok,v;return v.get('result') if ok else v
def check(text):checks.append(text);print('PASS '+text,flush=True)
source='function Known::Original (ref long value,out long[] nums,out long hidden) -> long {value blueprintPublishedOutputs = '+json.dumps(json.dumps(['return','nums']))+';}'
prepared=sdk('blueprintCallAfter',functionText=source,source='var local=@context.@nums;local[0]=9;return @context.@return+@context.@nums[0];');assert [p.get('id') for p in prepared['parts'] if 'id' in p]==['body','helpers'];expected=prepared['contractHash']
sig={'args':[{'type':'long','name':'value'}],'return':'long'};contract={'feature':'Known::Caller','signature':sig};fingerprint=hashlib.sha256(json.dumps(contract,sort_keys=True,separators=(',',':')).encode()).hexdigest()
callargs=[{'type':'long','name':'value','mode':'ref'},{'type':'long[]','name':'nums','mode':'out'},{'type':'long','name':'hidden','mode':'out'}]
graph={'schema':1,'profile':'sync-acyclic-methods-v1','feature':'Known::Caller','contractHash':fingerprint,'entry':'original','nodes':[{'id':'original','kind':'call','control':'next','intent':'Call original then After','feature':'Known::Original','signature':{'args':callargs,'return':'long'},'arguments':{'value':{'input':'value'}},'postCall':{'contractHash':expected,'source':prepared['source']}}],'edges':[{'from':'original','port':'next','to':'exit:return'}],'exits':{'return':{'node':'original'}}}
request={'featureSource':'function Known::Caller (long value) -> long {}','featureContracts':{'Known::Original':source},'graph':graph}
defs=sdk('featureBlueprintNodes',**request);assert defs['state']=='node-definitions' and defs['nodes'][0]['postCallEditor']['contractHash']==expected
assembled=sdk('featureBlueprintAssemble',implementations={},**request);assert assembled['state']=='source-assembled' and 'SourceContext' in assembled['members'] and 'After(' in assembled['members']
check('real graph compiler includes the fixed original-call/After member and exact public receipt without changing ordinary ref/out signature')
for change,code in [('receipt','GRAPH_PUBLIC_OUTPUT_CONTRACT_STALE'),('shape','GRAPH_POST_CALL_SHAPE'),('kind','GRAPH_POST_CALL_PROFILE')]:
 g=copy.deepcopy(graph)
 if change=='receipt':g['nodes'][0]['postCall']['contractHash']='0'*64
 elif change=='shape':g['nodes'][0]['postCall']['ignoredPermission']=True
 else:g['nodes'][0]['kind']='code'
 invalid=sdk('featureBlueprintNodes',**{**request,'graph':g});assert invalid['state']=='invalid' and any(d['code']==code for d in invalid['diagnostics']),invalid
revoked=source.replace(json.dumps(json.dumps(['return','nums'])),json.dumps('[]'));invalid=sdk('featureBlueprintAssemble',implementations={},**{**request,'featureContracts':{'Known::Original':revoked}});assert invalid['state']=='invalid' and any(d['code']=='GRAPH_PUBLIC_OUTPUT_CONTRACT_STALE' for d in invalid['diagnostics']);sdk('blueprintCallAfter',False,functionText=revoked,expected=expected)
check('forged receipt/extra fields/wrong node kind and revoked source exposure fail in both actual graph compilation and After preparation')
inspection=sdk('featureBlueprintNodes',inspectStalePostCalls=True,**{**request,'featureContracts':{'Known::Original':revoked}});assert inspection['state']=='node-definitions' and inspection['nodes'][0]['postCallStale'] and inspection['nodes'][0]['postCallEditor']['snapshot']['fields']==[]
strict=sdk('featureBlueprintAssemble',inspectStalePostCalls=True,implementations={},**{**request,'featureContracts':{'Known::Original':revoked}});assert strict['state']=='invalid' and any(d['code']=='GRAPH_PUBLIC_OUTPUT_CONTRACT_STALE' for d in strict['diagnostics'])
check('explicit display-only stale inspection retains source and marks it stale; the same flag cannot enable assembly')
changed_type=source.replace('ref long value','ref int value');inspection=sdk('featureBlueprintNodes',inspectStalePostCalls=True,**{**request,'featureContracts':{'Known::Original':changed_type}});assert inspection['state']=='node-definitions' and inspection['nodes'][0]['postCallStale'] and not inspection['nodes'][0]['postCallSignatureMatches']
strict=sdk('featureBlueprintAssemble',inspectStalePostCalls=True,implementations={},**{**request,'featureContracts':{'Known::Original':changed_type}});assert strict['state']=='invalid' and any(d['code']=='GRAPH_CALLEE_SIGNATURE' for d in strict['diagnostics'])
check('changed native input type is marked incompatible for explicit refresh and strict compilation remains blocked')
(case/'Test.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><Nullable>disable</Nullable></PropertyGroup></Project>');(case/'NuGet.Config').write_text('<configuration><packageSources><clear /></packageSources></configuration>')
main='''using System;
public static class Test {
 static int calls;
 sealed class Original:IOriginal {public long Invoke(ref long value,out long[] nums,out long hidden){calls++;value+=1;nums=new long[]{5};hidden=6;return 7;}}
 public static void Main(){long value=3;long result=Function.Execute(new Original(),ref value,out var nums,out long hidden);if(result!=12||value!=4||nums[0]!=5||hidden!=6||calls!=1)throw new Exception("After changed source count/storage/output or aliased captured array");Console.WriteLine("PASS After");}
}
'''
def compile(p,restore=False):
 code=main+''.join(part['text'] for part in p['parts']);(case/'Program.cs').write_text(code);cmd=[dotnet,'build',str(case/'Test.csproj'),'--nologo']+(['--configfile',str(case/'NuGet.Config')] if restore else ['--no-restore']);r=subprocess.run(cmd,text=True,capture_output=True,env=env);return r
r=compile(prepared,True);(case/'compile.log').write_text(r.stdout+r.stderr);assert r.returncode==0,(r.stdout,r.stderr)
r=subprocess.run([dotnet,str(case/'bin/Debug/net10.0/Test.dll')],text=True,capture_output=True,env=env);assert r.returncode==0 and 'PASS After' in r.stdout,(r.stdout,r.stderr)
check('generated native After source compiles and executes with a fake original exactly once, preserving ref input/hidden ordinary out and snapshot array isolation')
with_helpers=sdk('blueprintCallAfter',functionText=source,expected=expected,source='return Sum(@context.@return,@context.@nums[0]);',helpers='private static long Sum(long a,long b) {return a+b;}')
r=compile(with_helpers);assert r.returncode==0,r.stdout
r=subprocess.run([dotnet,str(case/'bin/Debug/net10.0/Test.dll')],text=True,capture_output=True,env=env);assert r.returncode==0,(r.stdout,r.stderr)
check('original separate helper region compiles and is called by After while the fixed invocation, storage and snapshot rules remain intact')
for body,code in [('context.@return=0;return 0;','CS0200'),('return context.@hidden;','CS1061')]:
 r=compile(sdk('blueprintCallAfter',functionText=source,expected=expected,source=body));assert r.returncode!=0 and code in r.stdout,r.stdout
check('C# compiler rejects mutation of published context and reading a non-published context field')
record={'checks':checks,'evidence':str(case),'actualEngine':False,'nativeWindows':False,'fakeCSharpOriginalOnly':True,'accountOrInference':False};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
