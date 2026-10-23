"""원본 별칭은 기존 저장소의 이름이며 함수 계약이나 값 복사가 아니다."""
import copy,json,os,pathlib,subprocess,sys,tempfile
r=pathlib.Path(sys.argv[1]).resolve();dotnet='/workspace/toolchains/dotnet-10.0.401/dotnet';host=r/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';case=pathlib.Path(tempfile.mkdtemp(prefix='confectory-alias-contract-'));checks=[]
def sdk(ok=True,**data):
 p=subprocess.run([dotnet,str(host)],input=json.dumps({'operation':'blueprintAliases',**data}),text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert v['ok']==ok,v;return v.get('result') if ok else v

def check(t):checks.append(t);print('PASS '+t,flush=True)
fixture=r.parent/'scratch/v508-elements/actual13-source-fixture/owned project';g=json.loads(next((fixture/'blueprints').glob('*.graph.json')).read_text());feature=(fixture/'elements/Serial.celem').read_text();alias={'id':'result_alias','name':'단계 결과','type':'long','sourceJson':json.dumps({'node':'body','output':'return'})};q={'featureSource':feature,'graph':g,'plan':{'aliases':[alias],'bindings':[{'kind':'exit','name':'return','valueJson':'{"local":"result_alias"}'}]}};before=copy.deepcopy(q);v=sdk(**q);assert q==before and v['graph']['profile']=='sync-acyclic-alias-locals-v1' and v['graph']['exits']['return']=={'local':'result_alias'} and v['graph']['nodes']==g['nodes'];check('이름 부여·별칭 사용·필요한 기존 프로필 전환을 하나의 후보에 준비하며 입력 그래프/원래 노드/핀 계약은 보존한다')
renamed=copy.deepcopy(q);renamed['graph']=v['graph'];renamed['plan']['bindings']=[];renamed['plan']['aliases'][0]['name']='이름 수정';v2=sdk(**renamed);assert v2['graph']['locals'][0]['id']=='result_alias' and v2['graph']['locals'][0]['source']==v['graph']['locals'][0]['source'] and v2['graph']['exits']==v['graph']['exits'];check('저장된 별칭 이름만 바꿀 때 기존 ID·원본 저장소·이미 연결된 소비자를 유지한다')
for changes in [{'name':''},{'name':'x\ny'},{'type':'int'},{'sourceJson':'{"node":"없는노드","output":"return"}'},{'sourceJson':'{"constant":3}'},{'sourceJson':'{"input":"없는입력"}'},{'sourceJson':'{"node":"body","output":"없는출력"}'}]:
 bad=copy.deepcopy(q);bad['plan']['aliases'][0].update(changes);sdk(False,**bad);assert q==before
bad=copy.deepcopy(renamed);bad['plan']['aliases'][0]['sourceJson']='{"input":"seed"}';sdk(False,**bad);check('빈/제어문자 이름·없는/외부 저장소·잘못된 타입·리터럴 별칭·저장된 별칭의 임의 재지정은 거부한다')
for second in [{'id':'other','name':'단계 결과','type':'long','sourceJson':'{"input":"seed"}'},{'id':'other','name':'같은 저장소','type':'long','sourceJson':'{"node":"body"}'}]:
 bad=copy.deepcopy(q);bad['plan']['aliases'].append(second);sdk(False,**bad)
bad=copy.deepcopy(q);bad['plan']['bindings'][0]={'kind':'argument','node':'다른요소','name':'seed','valueJson':'{"local":"result_alias"}'};sdk(False,**bad);check('동일한 이름/저장소의 중복 별칭과 다른 그래프의 바인딩 조작은 전체 후보를 거부한다')
bad=copy.deepcopy(q);bad['graph']['nodes'][0]['implementationContext']={};sdk(False,**bad);assert not v['sourceWritten'] and not v['compiled'] and not v['executed'];check('고급 호출자 문맥을 몰래 포함하지 않고 준비 단계에서 파일·컴파일·실행·권한을 변경하지 않는다')
record={'checks':checks,'evidence':str(case),'actualEngine':False,'nativeWindows':False,'accountOrInference':False};(case/'evidence.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(json.dumps(record,ensure_ascii=False,indent=2))
