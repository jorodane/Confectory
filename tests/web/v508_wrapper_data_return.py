"""Fixed native data output mapping stays separate from enum execution outcomes.
Actual generated C# compiler and isolated fake originals; no provider/account/project Run.
"""
import copy,hashlib,json,os,pathlib,re,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();dotnet='/workspace/toolchains/dotnet-10.0.401/dotnet';host=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-wrapper-data-return-'));checks=[]
env=os.environ.copy();env.update(DOTNET_CLI_HOME='/tmp/confectory-dotnet10-final',NUGET_PACKAGES='/tmp/confectory-site-nuget')
def sdk(op,ok=True,**body):
 p=subprocess.run([dotnet,str(host)],input=json.dumps({'operation':op,**body}),text=True,capture_output=True,env=env,check=True);v=json.loads(p.stdout);assert v['ok']==ok,v;return v.get('result') if ok else v
def check(text):checks.append(text);print('PASS '+text,flush=True)
execution={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0},{'id':'done','name':'완료','value':17}]};mapping='native-return-out-v1'
def source(typ):return 'function Known::Original (ref long value,out long count) -> '+typ+' {value blueprintPublishedOutputs = '+json.dumps(json.dumps(['return','count']))+';}'
units=[]
for i,(typ,result,assertion) in enumerate([
 ('bool','true','!returned || !context.@return'),
 ('long','9223372036854775700L','returned!=9223372036854775700L || context.@return!=returned'),
 ('string','"한글 \\" \\n 😀"','returned!="한글 \\" \\n 😀" || context.@return!=returned'),
 ('long[]','new long[]{9223372036854775700L}','returned[0]!=9223372036854775700L || context.@return[0]!=returned[0]'),
 ('object','identity','!object.ReferenceEquals(returned,identity) || !object.ReferenceEquals(context.@return,identity)'),
 ('long','9223372036854775700L','returned!=9223372036854775700L || context.@return!=returned'),
]):
 text=source(typ).replace('ref long value','ref long nativeReturn') if i==5 else source(typ);prepared=sdk('blueprintCallWrapper',functionText=text,executionEnum=execution,returnMapping=mapping,source='if(originalBranch!=OriginalResult.NoBranch || context.@count!=5)throw new System.Exception();return Result.완료;')
 assert prepared['returnMapping']==mapping and prepared['originalOutcome']=='native-data-completion-only' and [b['port'] for b in prepared['outputBindings']]==['return','count'] and prepared['outputBindings'][0]['type']==typ
 fields=prepared['snapshot'];args='ref value,out long count,out '+typ+' returned';parts=''.join(p['text'] for p in prepared['parts']);capture=fields['contextVariable'];readonly=''
 if typ=='long[]':readonly='var clone=context.@return;clone[0]=0;if(returned[0]!=9223372036854775700L||context.@return[0]!=9223372036854775700L)throw new System.Exception("snapshot aliases native data output");'
 units.append('namespace Data'+str(i)+' {\n'+parts+'\npublic class Fake:IOriginal {public static int calls;public static object identity=new object();public '+typ+' Invoke(ref long value,out long count){calls++;value++;count=5;return '+result+';}}\npublic static class Test {public static void Run(){long value=3;var branch=Function.Execute(new Fake(),'+args+');var identity=Fake.identity;var context=new Function.SourceContext(returned,count);if((int)branch!=17||value!=4||count!=5||Fake.calls!=1||'+assertion+')throw new System.Exception("native storage/outcome mismatch");'+readonly+'}}\n}')
check('explicit data mapping preserves declared return/out port identities and native types; execution outcome is never inferred from native data')
(case/'Test.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><Nullable>enable</Nullable><TreatWarningsAsErrors>true</TreatWarningsAsErrors></PropertyGroup></Project>');(case/'NuGet.Config').write_text('<configuration><packageSources><clear /></packageSources></configuration>')
def compile(code,restore=False):
 (case/'Program.cs').write_text(code);p=subprocess.run([dotnet,'build',str(case/'Test.csproj'),'--nologo']+(['--configfile',str(case/'NuGet.Config')] if restore else ['--no-restore']),text=True,capture_output=True,env=env);(case/'compile-last.log').write_text(p.stdout+p.stderr);return p
def run():
 p=subprocess.run([dotnet,str(case/'bin/Debug/net10.0/Test.dll')],text=True,capture_output=True,env=env);assert p.returncode==0,(p.stdout,p.stderr)
code='\n'.join(units)+'\npublic static class Program{public static void Main(){'+''.join('Data'+str(i)+'.Test.Run();' for i in range(6))+'}}';p=compile(code,True);assert p.returncode==0,p.stdout;run();check('real warning-strict C# runs bool/64-bit/string Unicode/array/object native returns once with ref/out, collision-safe nativeReturn parameter, separate enum17 and read-only array context copies')
for supplied in (None,'unknown','execution-enum',''):
 sdk('blueprintCallWrapper',False,functionText=source('long'),executionEnum=execution,**({} if supplied is None else {'returnMapping':supplied}))
sdk('blueprintCallWrapper',False,functionText='function Known::Original (ref long value,out long count) -> void {}',executionEnum=execution,returnMapping=mapping)
check('missing/unknown/empty native mapping and mapping on a void source fail before source writes or invocation')
args=[{'type':'long','name':'value','mode':'ref'},{'type':'long','name':'count','mode':'out'}];rootargs=[args[0],{'type':'long[]','name':'trace'}];sig={'args':rootargs,'return':'long'};fingerprint=hashlib.sha256(json.dumps({'feature':'Known::Caller','signature':sig},sort_keys=True,separators=(',',':')).encode()).hexdigest();fn=source('long');prepared=sdk('blueprintCallWrapper',functionText=fn,executionEnum=execution,returnMapping=mapping,source='return Result.완료;')
graph={'schema':1,'profile':'sync-acyclic-switch-v1','feature':'Known::Caller','contractHash':fingerprint,'entry':'wrapped','nodes':[{'id':'wrapped','kind':'call','control':'switch','intent':'Native data + independent enum','feature':'Known::Original','signature':{'args':args,'return':'long'},'arguments':{'value':{'input':'value'}},'executionEnum':execution,'postCall':{'mode':'execution-enum','returnMapping':mapping,'contractHash':prepared['contractHash'],'source':'return Result.완료;'}},{'id':'case','kind':'code','control':'next','branchOwner':'wrapped','intent':'Consume native return inside case','signature':{'args':[{'type':'long','name':'number'},{'type':'long[]','name':'trace'}],'return':'void'},'arguments':{'number':{'node':'wrapped'},'trace':{'input':'trace'}},'implementation':'case.node.json'},{'id':'tail','kind':'code','control':'next','intent':'Consume same native result/out after case','signature':{'args':[{'type':'long','name':'number'},{'type':'long','name':'count'},{'type':'long[]','name':'trace'}],'return':'long'},'arguments':{'number':{'node':'wrapped'},'count':{'node':'wrapped','output':'count'},'trace':{'input':'trace'}},'implementation':'tail.node.json'}],'edges':[{'from':'wrapped','port':'next','to':'tail'},{'from':'wrapped','port':'case:done','to':'case'},{'from':'case','port':'next','to':'return:wrapped'},{'from':'tail','port':'next','to':'exit:return'}],'exits':{'return':{'node':'tail'}}}
request={'featureSource':'function Known::Caller (ref long value,long[] trace) -> long {}','featureContracts':{'Known::Original':fn},'graph':graph};defs=sdk('featureBlueprintNodes',**request);assert defs['state']=='node-definitions',defs
node=next(n for n in defs['nodes'] if n['id']=='wrapped');assert node['outputs'][0]['name']=='return' and node['outputs'][0]['type']=='long';records={n['id']:{'schema':1,'node':n['id'],'definitionHash':n['definitionHash'],'source':'if(number!=9223372036854775700L)throw new System.Exception();trace[0]+=100;' if n['id']=='case' else 'trace[0]+=1000;return number+count;'} for n in defs['nodes'] if n['id']!='wrapped'}
assembled=sdk('featureBlueprintAssemble',implementations=records,**request);assert assembled['state']=='source-assembled',assembled;alias=assembled['imports'][0]['alias'];iface=re.search(r'Execute\((\S+) @original',assembled['members'])[1];ns,local=iface.removeprefix('global::').rsplit('.',1)
code='namespace '+ns+' {public interface '+local+' {long Invoke(ref long value,out long count);}}\npublic class Fake:'+iface+' {public static int count;public long Invoke(ref long value,out long result){count++;value++;result=5;return 9223372036854775700L;}}\npublic class Calls {public '+iface+' '+alias+'=new Fake();}\npublic class Graph {public Calls calls=new();public long Invoke(ref long value,long[] trace){\n'+assembled['body']+'\n}\n'+assembled['members']+'}\npublic static class Program{public static void Main(){long value=3;var trace=new long[1];long result=new Graph().Invoke(ref value,trace);if(result!=9223372036854775705L||value!=4||trace[0]!=1100||Fake.count!=1)throw new System.Exception("graph native output overwritten by enum or repeated call");}}'
p=compile(code);assert p.returncode==0,p.stdout;run();check('actual graph assembly compiles and runs: preserved native return/out feeds both case and continuation consumers while enum selects existing region and original runs once')
for kind in ('missing','unknown','native-type-change','stale-publication','bad-consumer-type'):
 req=copy.deepcopy(request)
 if kind=='missing':del req['graph']['nodes'][0]['postCall']['returnMapping']
 elif kind=='unknown':req['graph']['nodes'][0]['postCall']['returnMapping']='enum-is-data'
 elif kind=='native-type-change':req['featureContracts']['Known::Original']=fn.replace('-> long','-> bool')
 elif kind=='stale-publication':req['graph']['nodes'][0]['postCall']['contractHash']='0'*64
 else:req['graph']['nodes'][1]['signature']['args'][0]['type']='bool'
 bad=sdk('featureBlueprintAssemble',implementations=records,**req);assert bad['state']=='invalid',bad
check('actual assembler rejects unmapped/forged data mapping, changed source type/publication and incompatible existing consumer without coercing or removing any binding')
record={'checks':checks,'evidence':str(case),'actualCSharpCompiler':True,'fakeOriginalsOnly':True,'actualEngine':False,'nativeWindows':False,'accountOrInference':False,'projectRun':False};(case/'evidence.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
