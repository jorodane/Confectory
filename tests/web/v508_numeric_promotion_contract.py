"""원본 정수→실수 값 호환: 타입/참조 경계와 정확한 정수 보존을 검사한다."""
import copy,json,os,pathlib,subprocess,sys,tempfile
r=pathlib.Path(sys.argv[1]).resolve();dotnet='/workspace/toolchains/dotnet-10.0.401/dotnet';host=r/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-numeric-promotion-'));checks=[];env=os.environ.copy();env.update(DOTNET_CLI_HOME='/tmp/confectory-dotnet10-final',NUGET_PACKAGES='/tmp/confectory-site-nuget')
def sdk(op,**data):
 p=subprocess.run([dotnet,str(host)],input=json.dumps({'operation':op,**data}),text=True,capture_output=True,check=True,env=env);v=json.loads(p.stdout);assert v['ok'],v;return v['result']
def check(t):checks.append(t);print('PASS '+t,flush=True)
def request(source,target,binding):
 v=sdk('blueprintPrepareFeature',id='Promote.Case::F',text='function Promote.Case::F ('+source+' a) -> '+target+' {}',implementation='Promote.Case::Body',graphPath='f.graph.json',nodePath='n.node.json');g=v['graph'];g.update(nodes=[],edges=[],entry='exit:return',exits={'return':binding});return {'featureSource':v['function'],'graph':g,'implementations':{}}
def assemble(q):return sdk('featureBlueprintAssemble',**q)
functions=[]
for source,target,value in [('int','float',16777216),('int','double',2147483647),('long','float',16777216),('long','double',9007199254740992)]:
 q=request(source,target,{'input':'a'});before=copy.deepcopy(q);v=assemble(q);assert v['state']=='source-assembled' and q==before;functions.append((source,target,value,v['body']))
check('원본의 정수→실수 값 연결만 허용하며 입력 문서와 함수 ABI를 변경하지 않는다')
for source,target in [('long','int'),('double','long'),('double','float'),('int[]','double[]'),('bool','double'),('string','double')]:assert assemble(request(source,target,{'input':'a'}))['state']=='invalid'
q=request('long','double',{'node':'n'});q['graph'].update(profile='sync-acyclic-ref-nodes-v1',entry='n',nodes=[{'id':'n','kind':'code','control':'next','intent':'ref 경계','signature':{'args':[{'name':'value','type':'double','mode':'ref'}],'return':'double'},'arguments':{'value':{'input':'a'}}}],edges=[{'from':'n','port':'next','to':'exit:return'}]);v=assemble(q);assert v['state']=='invalid' and v['diagnostics'][0]['code']=='GRAPH_INPUT_TYPE'
check('정수/실수 역방향·축소·배열·다른 타입과 ref 저장소의 암묵 변환은 거부한다')
for target,bad in [('float',16777217),('double',9007199254740993),('double',9223372036854775807)]:
 v=assemble(request('long',target,{'constant':bad,'type':'long'}));assert v['state']=='invalid' and v['diagnostics'][0]['code']=='GRAPH_NUMERIC_PRECISION',v
v=assemble(request('long','double',{'binary':{'operator':'+','operands':[{'constant':9007199254740992,'type':'long'},{'input':'a'}]}}));assert v['state']=='source-assembled';functions.append(('long','double',2,v['body']))
check('기존 정수 리터럴의 타입/64비트 원문을 유지하고 이미 알려진 정밀도 손실은 어셈블 단계에서 거부한다')
q=request('long','double',{'local':'saved'});q['graph'].update(profile='sync-acyclic-alias-locals-v1',locals=[{'id':'saved','name':'기존 이름','type':'long','source':{'input':'a'}}]);v=assemble(q);assert v['state']=='source-assembled';functions.append(('long','double',123,v['body']));assert q['graph']['locals'][0]['type']=='long';check('별칭의 선언 타입과 원본 저장소를 바꾸지 않고 사용 지점에서만 검증된 승격을 적용한다')
q=request('long','double',{'node':'n'});q['graph'].update(entry='n',nodes=[{'id':'n','kind':'code','control':'next','intent':'정수 출력','signature':{'args':[{'name':'value','type':'long'}],'return':'long'},'arguments':{'value':{'input':'a'}}}],edges=[{'from':'n','port':'next','to':'exit:return'}]);node=sdk('featureBlueprintNodes',featureSource=q['featureSource'],graph=q['graph'])['nodes'][0];q['implementations']={'n':{'schema':1,'node':'n','definitionHash':node['definitionHash'],'source':'return value;'}};v=assemble(q);assert v['state']=='source-assembled';functions.append(('long','double',99,v['body']));check('실제 정수 노드 출력도 기존 실행 가용성 검사 뒤에만 실수 값으로 승격한다')
(case/'Test.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><Nullable>enable</Nullable><TreatWarningsAsErrors>true</TreatWarningsAsErrors></PropertyGroup></Project>');(case/'NuGet.Config').write_text('<configuration><packageSources><clear /></packageSources></configuration>');code='using System;static class Program {\n'
for i,(source,target,value,body) in enumerate(functions):code+='static '+target+' F'+str(i)+'('+source+' a){\n'+body+'}\n'
code+='static void Main(){\n'
for i,(source,target,value,body) in enumerate(functions):
 wanted=value if i!=4 else 9007199254740994;code+='if(F'+str(i)+'('+str(value)+('L' if source=='long' else '')+')!='+str(wanted)+('F' if target=='float' else 'D')+')throw new Exception("value'+str(i)+'");\n'
for call in ['F0(16777217)','F2(16777217L)','F3(9007199254740993L)','F3(long.MaxValue)']:code+='try{'+call+';throw new Exception("rounded integer accepted");}catch(ArithmeticException){}\n'
code+='if(F3(long.MinValue)!=(double)long.MinValue)throw new Exception("exact minimum");Console.WriteLine("PASS exact promotions and precision guards");}}';(case/'Program.cs').write_text(code);p=subprocess.run([dotnet,'build',str(case/'Test.csproj'),'--configfile',str(case/'NuGet.Config'),'--nologo'],env=env,text=True,capture_output=True);(case/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr;p=subprocess.run([dotnet,str(case/'bin/Debug/net10.0/Test.dll')],env=env,text=True,capture_output=True);assert p.returncode==0 and 'PASS exact promotions' in p.stdout,p.stdout+p.stderr;check('격리 실제 C# 컴파일/실행으로 정확한 int/long→float/double·별칭·혼합 식과 런타임 반올림 거부를 확인한다')
record={'checks':checks,'evidence':str(case),'actualEngine':False,'controlledCSharpExecution':True,'nativeWindows':False,'accountOrInference':False};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
