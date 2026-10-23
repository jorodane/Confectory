"""다중 구현/대상 문맥의 읽기 전용 계약. 선택·본문 읽기·변환은 수행하지 않는다."""
import copy,hashlib,json,os,pathlib,subprocess,sys,tempfile
r=pathlib.Path(sys.argv[1]).resolve();host=r/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';dotnet='/workspace/toolchains/dotnet-10.0.401/dotnet';case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-feature-context-'));checks=[]
def sdk(data,success=True):
 p=subprocess.run([dotnet,str(host)],input=json.dumps({'operation':'blueprintFeatureBodies',**data}),text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok']) is success,v;return v.get('result')
def row(id,text,dirty=False):return {'id':'Owned.Context::'+id,'text':text,'revision':3,'hash':hashlib.sha256(text.encode()).hexdigest(),'dirty':dirty}
def impl(id,bodies='',parent=None,feature='F',signature='(long value) -> long'):return row(id,'implementation Owned.Context::'+id+' for Owned.Context::'+feature+' '+signature+(' extends Owned.Context::'+parent if parent else '')+' {'+bodies+'}')
def checked(t):checks.append(t);print('PASS '+t,flush=True)
a=impl('A','body common "must-not-read.csbody";blueprint windows "must-not-read.graph.json";');b=impl('B','blueprint common "also-must-not-read.graph.json";');child=impl('Child','body linux "never-read.csbody";',parent='A');other=impl('Other','body common "other.csbody";',feature='G');q={'namespace':'Owned.Context','featureSource':'function Owned.Context::F (long value) -> long {}','sources':[a,b,child,other]};before=copy.deepcopy(q);v=sdk(q);assert q==before and len(v['rows'])==6 and not v['selectionMade'] and not v['sourceWritten'] and not v['compiled'];assert len({x['id'] for x in v['rows']})==6
checked('여러 구현·대상과 C#/Blueprint를 정확히 열거하고 하나를 임의 선택하거나 본문 파일을 읽지 않는다')
declared=sdk({**q,'featureSource':'function Owned.Context::F (long value) -> long {provide Owned.Context::F with Owned.Context::B;}'});assert declared['declaredImplementation']=='Owned.Context::B' and not declared['selectionMade'] and len(declared['rows'])==6
checked('원본 기능의 명시적 provide 연결을 메타데이터로 반환하며 후보가 여러 개여도 임의 provider로 대체하지 않는다')
rows={x['id']:x for x in v['rows']};assert rows['Owned.Context::Child/body:common']['bodyOrigin']=='Owned.Context::A' and rows['Owned.Context::Child/body:common']['inherited'] and rows['Owned.Context::Child/body:linux']['bodyOrigin']=='Owned.Context::Child';assert not v['unresolvedParents']
checked('상속 본문과 로컬 대상의 출처·편집 문맥을 분리하고 서로 다른 구현의 같은 common 이름을 합치지 않는다')
x=copy.deepcopy(q);x['sources'][0]['dirty']=True;v=sdk(x);assert all(z['dirty'] for z in v['rows'] if z['implementation'] in ['Owned.Context::A','Owned.Context::Child']) and not next(z['dirty'] for z in v['rows'] if z['implementation']=='Owned.Context::B')
checked('부모의 미저장 변경을 자식 문맥에도 표시하고 다른 구현 상태에 섞지 않는다')
x=copy.deepcopy(q);x['sources'].append(impl('ExternalChild','body local "local.csbody";',parent='Unresolved'));v=sdk(x);assert v['unresolvedParents'] and any(z['implementation']=='Owned.Context::ExternalChild' for z in v['rows']) and not v['selectionMade']
checked('현재 소유 스냅샷에서 확인할 수 없는 부모는 누락된 대상으로 추측하지 않고 불확실성을 반환한다')
for patch in [{'namespace':'Other.Context'},{'sources':[a,a]},{'sources':[{**a,'hash':'0'*64}]},{'sources':[impl('Bad','',signature='(double value) -> long')]},{'sources':[impl('Loop1','',parent='Loop2'),impl('Loop2','',parent='Loop1')]},{'sources':[a,impl('WrongChild','',parent='A',feature='G')]}]:sdk({**q,**patch},False)
checked('다른 namespace·중복/위조 관찰·잘못된 계약·상속 순환/기능 변경을 거부한다')
record={'checks':checks,'actualEngine':False,'nativeWindows':False,'accountOrInference':False,'bodyRead':False,'evidence':str(case)};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
