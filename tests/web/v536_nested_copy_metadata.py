"""Qualified private-copy records preserve duplicate leaf identity and opaque body."""
import copy,hashlib,json,os,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-nested-copy-metadata-'));source=root/'registered';source.mkdir();owned=root/'owned';owned.mkdir();dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet');dll=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'
def call(operation,ok=True,**args):
 p=subprocess.run([dotnet,str(dll)],input=json.dumps({'operation':operation,**args}),capture_output=True,text=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,(operation,v);return v.get('result')
fn='function Source.Nested::Run (long amount) -> long {provide Source.Nested::Run with Source.Nested::Body;}'
(source/'Run.celem').write_text(fn);(source/'pack.cpack').write_text('pack Source.Nested version "1" {element Run function "Run.celem";element Body implementation "Body.celem";}')
owner='schema Owned.Nested::Info {}';(owned/'Info.celem').write_text(owner);project=owned/'project.cproj';project.write_text('project Owned.Nested version "1" {standalone true;entry Source.Nested::Run;element Info schema "Info.celem";registry Source.Nested "../registered/pack.cpack";dependency Source.Nested version "1";}')
req={'action':'prepare','project':str(project),'owner':'Owned.Nested::Info','ownerText':owner,'feature':'Source.Nested::Run','source':'Source.Nested::Body','target':'common','implementation':'Owned.Nested::Chosen'}
prepared=call('blueprintPrepareFeature',id=req['feature'],text=fn.replace('provide Source.Nested::Run with Source.Nested::Body;',''),implementation=req['source'],graphPath='body.graph.json',nodePath='body.node.json');g=prepared['graph'];sig=copy.deepcopy(g['nodes'][0]['signature'])
def leaf(name):return {'schema':1,'profile':'sync-acyclic-methods-v1','entry':'body','nodes':[{'id':'body','kind':'code','control':'next','intent':'원래 '+name,'signature':copy.deepcopy(sig),'arguments':{'amount':{'input':'amount'}},'implementation':name+'.node.json'}],'edges':[{'from':'body','port':'next','to':'exit:return'}],'exits':{'return':{'node':'body'}},'locals':[{'id':'kept','name':'정확한 값','type':'long','initial':{'constant':9223372036854775806}}]}
def box(name,child):return {'id':name,'kind':'graph','control':'next','intent':'내부 '+name,'signature':copy.deepcopy(sig),'arguments':{'amount':{'input':'amount'}},'graph':child}
left=leaf('left');right={'schema':1,'profile':'sync-acyclic-nested-v1','entry':'deep','nodes':[box('deep',leaf('right'))],'edges':[{'from':'deep','port':'next','to':'exit:return'}],'exits':{'return':{'node':'deep'}},'locals':[]}
g.update(profile='sync-acyclic-nested-v1',entry='left',nodes=[box('left',left),box('right',right)],edges=[{'from':'left','port':'next','to':'right'},{'from':'right','port':'next','to':'exit:return'}],exits={'return':{'binary':{'operator':'+','type':'long','operands':[{'node':'left'},{'node':'right'}]}}})
context={'implementation':req['source'],'feature':req['feature'],'signature':sig,'imports':{}}
defs=call('featureBlueprintNodes',featureSource=fn,implementationContext=context,bodyTarget='common',graph=g);assert defs['state']=='node-definitions',defs
records={}
for row in defs['nestedNodes']:
 if row['definition']['kind']!='code':continue
 key=row['id'];name='left' if key=='left/body' else 'right';record={'schema':1,'node':'body','definitionHash':row['definitionHash'],'source':'return amount+'+('1' if name=='left' else '7')+'; // '+name+' 😀 9223372036854775806\r\n','helpers':'private static long Keep(long value){return value;} // '+name+' 원문\r\n'};records[key]=record;(source/(name+'.node.json')).write_text(json.dumps(record))
(source/'Body.celem').write_text(prepared['implementation']);(source/'body.graph.json').write_text(json.dumps(g));before={p:p.read_bytes() for p in root.rglob('*') if p.is_file()}
plan=call('implementationCopy',**req);assert plan['sourceWritten'] is False and all(p.read_bytes()==v for p,v in before.items());assert set(r['id'] for r in plan['records'])==set(records)
for row in plan['records']:
 assert row['record']['node']=='body' and row['record']['source']==records[row['id']]['source'] and row['record']['helpers']==records[row['id']]['helpers']
 assert row['record']['definitionHash']!=records[row['id']]['definitionHash']
assert len({r['relative'] for r in plan['records']})==2 and plan['graph']['edges']==g['edges'] and plan['graph']['exits']==g['exits']
checks=[]
def checked(text):checks.append(text);print('PASS '+text,flush=True)
checked('깊이1/2 동명 leaf는 전체경로·별도파일·copy 소유 해시를 갖고 원계약·route·정확한 값·C#/helpers와 원본을 보존한다')
seed={'schema':1,'identity':'isolated-fixture','scopeGuard':'fixture-scope','contentFingerprint':'fixture-source','snapshot':copy.deepcopy(plan['snapshot'])}
private={**req,'identity':'isolated-fixture','ownerBasisHash':seed['snapshot']['ownerHash'],'seed':seed,'scopeGuard':'fixture-scope','contextGuard':'fixture-owned','initialize':True,'preview':True,'privatePath':'right/deep'}
preview=call('implementationCopy',**private);assert preview['preview']['privatePath']=='right/deep' and preview['preview']['signature']==sig
assert next(n for n in preview['preview']['nodes'] if n['id']=='body')['source']==records['right/deep/body']['source']
assert preview['seed']['snapshot']==seed['snapshot'];sealed=preview['seed'];assert json.loads(json.dumps(sealed))==sealed
mid=call('implementationCopy',**{**private,'seed':sealed,'initialize':False,'privatePath':'right'});assert mid['preview']['nodes'][0]['id']=='deep'
private.update(seed=sealed,initialize=False,privatePath='left');again=call('implementationCopy',**private);assert next(n for n in again['preview']['nodes'] if n['id']=='body')['source']==records['left/body']['source']
call('implementationCopy',False,**{**private,'privatePath':'right/missing'});assert all(p.read_bytes()==v for p,v in before.items())
checked('미등록 copy seed의 cold JSON·qualified preview 이동은 원래 snapshot/출처를 유지하고 불명 private 경로를 거절한다')
changed=call('implementationCopy',**req,edits=[{'node':'left/body','type':'source','text':'return Keep(amount)+3; // 명시 편집\n'}]);assert next(r for r in changed['records'] if r['id']=='left/body')['record']['source']=='return Keep(amount)+3; // 명시 편집\n';assert next(r for r in changed['records'] if r['id']=='right/deep/body')['record']==next(r for r in plan['records'] if r['id']=='right/deep/body')['record']
checked('명시한 qualified leaf 본문만 후보에서 바꾸고 동명 형제·부모·원본은 그대로 유지한다')
values=call('implementationCopy',**req,edits=[{'node':'left/body','type':'source','text':'return Keep(amount)+3; // 値候補\n'},{'node':'left/body','type':'argument:amount','text':'{"constant":9223372036854775804}'},{'node':'right/deep/body','type':'argument:amount','text':'{"local":"kept"}'}])
left_node=values['graph']['nodes'][0]['graph']['nodes'][0];right_node=values['graph']['nodes'][1]['graph']['nodes'][0]['graph']['nodes'][0]
assert left_node['arguments']['amount']=={'constant':9223372036854775804} and right_node['arguments']['amount']=={'local':'kept'}
assert values['signature']==plan['signature'] and values['implementation']==plan['implementation'] and values['graph']['edges']==plan['graph']['edges'] and values['graph']['exits']==plan['graph']['exits'];assert all(p.read_bytes()==v for p,v in before.items())
checked('qualified 하위 값/기존 local 연결과 명시 본문은 같은 후보에서 원계약·순서·route·정확한64비트 값과 다른 프레임을 보존한다')
for key,name,value in [('left/body','amount','{"constant":"wrong"}'),('left/body','amount','{"constant":9223372036854775808}'),('left/body','amount','{"node":"right/deep/body"}'),('left/body','missing','{"constant":1}'),('right/deep/body','amount','{"local":"outside"}'),('left/body','amount','null')]:
 call('implementationCopy',False,**req,edits=[{'node':'left/body','type':'source','text':'return 100; // 적용되면 안 되는 첫 편집'},{'node':key,'type':'argument:'+name,'text':value}]);assert all(p.read_bytes()==v for p,v in before.items())
checked('타입/범위/64비트 overflow/미선언 핀·local·미완성 연결의 마지막 편집이 잘못되면 본문도 반환하지 않고 전체거절한다')
for bad in [ {'node':'body','type':'source','text':'guess'}, {'node':'right/body','type':'source','text':'guess'}, {'node':'../left/body','type':'source','text':'guess'}, {'node':'left/body','type':'parameters','text':'{}'}, {'node':'left','type':'source','text':'guess'} ]:
 call('implementationCopy',False,**req,edits=[bad]);assert all(p.read_bytes()==v for p,v in before.items())
checked('불완전/위조 경로·경계넘기·불완전 private 핀 계획·graph 본문 추측은 전체거절하고 원문을 보존한다')
if 'pins' in sys.argv[2:]:
 pin_plan={'args':[{'name':'received','type':'long'},{'name':'extra','type':'string'}],'returnType':'long','remap':{'amount':'received'}}
 pin_edits=[{'node':'left/body','type':'parameters','text':json.dumps(pin_plan)},{'node':'left/body','type':'argument:extra','text':json.dumps({'constant':'새 입력 😀'})},{'node':'left/body','type':'source','text':'return Keep(received)+3; // 명시 새 본문\n'}]
 pins=call('implementationCopy',**req,edits=pin_edits);node=pins['graph']['nodes'][0]['graph']['nodes'][0]
 assert node['signature']=={'args':pin_plan['args'],'return':'long'} and node['arguments']=={'received':{'input':'amount'},'extra':{'constant':'새 입력 😀'}}
 assert pins['signature']==plan['signature'] and pins['graph']['edges']==plan['graph']['edges'] and pins['graph']['exits']==plan['graph']['exits'];assert next(r for r in pins['records'] if r['id']=='right/deep/body')==next(r for r in plan['records'] if r['id']=='right/deep/body')
 private_pins=call('implementationCopy',**{**private,'preview':False},edits=pin_edits);assert private_pins['graph']['nodes'][0]['graph']['nodes'][0]['signature']==node['signature'] and private_pins['seedHash']==private['seed']['snapshot']['hash']
 checked('원래 private 동작 핀 이름/추가와 명시 값·C# 본문을 한 후보로 묶고 seed·원계약·프레임·연결·정확한 원문을 보존한다')
 dropped={'args':[{'name':'newValue','type':'long'}],'returnType':'long','remap':{'amount':None}}
 changed=call('implementationCopy',**req,edits=[{'node':'left/body','type':'argument:amount','text':'null'},{'node':'left/body','type':'parameters','text':json.dumps(dropped)},{'node':'left/body','type':'argument:newValue','text':'{"local":"kept"}'},{'node':'left/body','type':'source','text':'return Keep(newValue);'}]);assert changed['graph']['nodes'][0]['graph']['nodes'][0]['arguments']=={'newValue':{'local':'kept'}}
 checked('기존 사용 입력의 삭제는 명시 해제·새 핀/값 대응과 본문이 모두 있을 때만 원자 후보에서 처리한다')
 for edits in [pin_edits[:-1], [{'node':'left/body','type':'parameters','text':json.dumps({**pin_plan,'args':[{'name':'received','type':'string'}]})}], [{'node':'left/body','type':'parameters','text':json.dumps(dropped)},{'node':'left/body','type':'source','text':'return Keep(newValue);'}],pin_edits+[{'node':'right/deep/body','type':'parameters','text':'{}'}], [{'node':'left/body','type':'parameters','text':json.dumps({'args':[{'name':'amount','type':'long'}],'returnType':'void','remap':{'amount':'amount'}})},{'node':'left/body','type':'source','text':'return;'}]]:
  call('implementationCopy',False,**req,edits=edits);assert all(p.read_bytes()==v for p,v in before.items())
 checked('stale 본문·호환불가 매핑·사용 중인 입력/반환 제거·마지막 형제 핀 오류는 원본을 보존하고 전체 미적용한다')
(root/'result.json').write_text(json.dumps({'checks':checks,'evidence':str(root),'pureMetadata':True,'nativeWindows':False},ensure_ascii=False,indent=2));print(json.dumps({'checks':checks,'evidence':str(root),'pureMetadata':True},ensure_ascii=False))
