"""원본 이항 연산 의미를 순수 어셈블러와 격리 C# 실행으로 검사한다."""
import copy,json,os,pathlib,subprocess,sys,tempfile
r=pathlib.Path(sys.argv[1]).resolve();dotnet='/workspace/toolchains/dotnet-10.0.401/dotnet';host=r/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-expression-contract-'));checks=[];env=os.environ.copy();env.update(DOTNET_CLI_HOME='/tmp/confectory-dotnet10-final',NUGET_PACKAGES='/tmp/confectory-site-nuget')
def sdk(op,**data):
 p=subprocess.run([dotnet,str(host)],input=json.dumps({'operation':op,**data}),text=True,capture_output=True,env=env,check=True);v=json.loads(p.stdout);assert v['ok'],v;return v['result']
def check(text):checks.append(text);print('PASS '+text,flush=True)
def binary(op,a,b):return {'binary':{'operator':op,'operands':[a,b]}}
def request(type,value):
 text='function Expr.Case::F ('+type+' a,'+type+' b) -> '+type+' {}';v=sdk('blueprintPrepareFeature',id='Expr.Case::F',text=text,implementation='Expr.Case::Body',graphPath='f.graph.json',nodePath='n.node.json');g=v['graph'];g.update(nodes=[],edges=[],entry='exit:return',exits={'return':value});return {'featureSource':v['function'],'graph':g,'implementations':{}}
def query(q):return sdk('featureBlueprintAssemble',**q)
functions=[]
for t,op,a,b,expected in [('long','+',9223372036854775700,7,9223372036854775707),('int','/',-7,2,-3),('int','%',7,3,1),('float','+',3.5,2.0,5.5),('double','*',1.25,2,2.5),('bool','AND',True,False,False),('bool','OR',False,True,True),('bool','XOR',True,True,False),('string','+','한글 "문장" ','😀','한글 "문장" 😀')]:
 q=request(t,binary(op,{'input':'a'},{'input':'b'}));v=query(q);assert v['state']=='source-assembled',v;i=len(functions);functions.append((t,v['body'],a,b,expected))
check('정수·실수·글자·조건의 원본 연산자 집합을 기존 타입/노드 가용성 검사와 함께 어셈블한다')
q=request('long',binary('+',{'constant':9223372036854775700},binary('*',{'input':'a'},{'constant':7})));v=query(q);assert v['state']=='source-assembled' and '9223372036854775700L' in v['body'];functions.append(('long',v['body'],3,0,9223372036854775721));check('중첩 표현식과 64비트 숫자 원문이 반올림 없이 C# 본문에 보존된다')
for t,val in [('string',binary('-',{'input':'a'},{'input':'b'})),('long[]',binary('+',{'input':'a'},{'input':'b'})),('int',binary('/',{'input':'a'},{'constant':0})),('bool',binary('&&',{'input':'a'},{'input':'b'})),('int',binary('+',{'input':'a'},None)),('int',binary('+',{'input':'a'},{'constant':'잘못된 타입'})),('int',binary('+',{'input':'a'},{'node':'없는노드'}))]:
 result=query(request(t,val));assert result['state']=='invalid',result
value={'input':'a'}
for _ in range(14):value=binary('+',value,{'constant':1})
assert query(request('int',value))['state']=='invalid'
check('배열/타입 불일치·미완성·상수 0 나눗셈·허용되지 않은 연산자·없는 노드·과도한 깊이는 실패한다')
q=request('int',binary('+',{'input':'a'},{'input':'b'}));q['graph'].update(profile='sync-acyclic-ref-nodes-v1',entry='n',nodes=[{'id':'n','kind':'code','control':'next','intent':'참조 보호','signature':{'args':[{'name':'x','type':'int','mode':'ref'}],'return':'int'},'arguments':{'x':binary('+',{'input':'a'},{'constant':1})}}],edges=[{'from':'n','port':'next','to':'exit:return'}],exits={'return':{'node':'n'}});refusal=query(q);assert refusal['state']=='invalid' and refusal['diagnostics'][0]['code']=='GRAPH_REF_STORAGE';check('표현식 결과를 참조 저장소로 위장할 수 없으며 기존 ref 보호를 유지한다')
(case/'Test.csproj').write_text('<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><Nullable>enable</Nullable><TreatWarningsAsErrors>true</TreatWarningsAsErrors></PropertyGroup></Project>');(case/'NuGet.Config').write_text('<configuration><packageSources><clear /></packageSources></configuration>')
def literal(value,t):
 if t=='long':return str(value)+'L'
 if t=='float':return repr(value)+'F'
 if t=='double':return repr(value)+'D'
 return json.dumps(value,ensure_ascii=False)
source='using System;\nstatic class Program {\n'
for i,(t,body,a,b,expected) in enumerate(functions):source+='static '+t+' F'+str(i)+'('+t+' a,'+t+' b){\n'+body+'}\n'
source+='static void Main(){\n'
for i,(t,body,a,b,expected) in enumerate(functions):source+='if(F'+str(i)+'('+literal(a,t)+','+literal(b,t)+')!='+literal(expected,t)+')throw new Exception("case'+str(i)+'");\n'
source+='try{F0(long.MaxValue,1);throw new Exception("overflow not rejected");}catch(OverflowException){}\ntry{F1(1,0);throw new Exception("zero not rejected");}catch(DivideByZeroException){}\ntry{F3(float.MaxValue,float.MaxValue);throw new Exception("finite not rejected");}catch(ArithmeticException){}\nConsole.WriteLine("PASS values and runtime guards");}}'
(case/'Program.cs').write_text(source);p=subprocess.run([dotnet,'build',str(case/'Test.csproj'),'--configfile',str(case/'NuGet.Config'),'--nologo'],env=env,text=True,capture_output=True);(case/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr;p=subprocess.run([dotnet,str(case/'bin/Debug/net10.0/Test.dll')],env=env,text=True,capture_output=True);assert p.returncode==0 and 'PASS values' in p.stdout,p.stdout+p.stderr;check('격리 실제 C# 컴파일/실행으로 산술·논리·한글/이모지·64비트 결과와 오버플로·동적 0 나눗셈·비유한 결과 거부를 확인한다')
record={'checks':checks,'evidence':str(case),'actualEngine':False,'controlledCSharpExecution':True,'nativeWindows':False,'accountOrInference':False};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
