"""Flat code branch/switch copy: retain identity, routes and opaque source; reject bad candidates."""
import copy,hashlib,json,os,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-branch-copy-metadata-'));source=root/'registered';source.mkdir();owned=root/'owned';owned.mkdir();dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet');dll=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'
def call(operation,ok=True,**args):
 p=subprocess.run([dotnet,str(dll)],input=json.dumps({'operation':operation,**args}),capture_output=True,text=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,(operation,v);return v.get('result')
fn='function Source.Branch::Run (long amount) -> long {provide Source.Branch::Run with Source.Branch::Body;}'
(source/'Run.celem').write_text(fn);(source/'pack.cpack').write_text('pack Source.Branch version "1" {element Run function "Run.celem";element Body implementation "Body.celem";}')
owner='schema Owned.Branch::Info {}';(owned/'Info.celem').write_text(owner);project=owned/'project.cproj';project.write_text('project Owned.Branch version "1" {standalone true;entry Source.Branch::Run;element Info schema "Info.celem";registry Source.Branch "../registered/pack.cpack";dependency Source.Branch version "1";}')
req={'action':'prepare','project':str(project),'owner':'Owned.Branch::Info','ownerText':owner,'feature':'Source.Branch::Run','source':'Source.Branch::Body','target':'common','implementation':'Owned.Branch::Chosen'}
checks=[]
def checked(text):checks.append(text);print('PASS '+text,flush=True)
for control in ['switch']:
 prepared=call('blueprintPrepareFeature',id='Source.Branch::Run',text=fn.replace('provide Source.Branch::Run with Source.Branch::Body;',''),implementation='Source.Branch::Body',graphPath='body.graph.json',nodePath='body.node.json');g=prepared['graph'];g['profile']='sync-acyclic-switch-v1';g['entry']='decision';g['locals']=[{'id':'kept','name':'정확한 보관 값','type':'long','initial':{'constant':9223372036854775806}}]
 node={'id':'decision','kind':'code','control':control,'intent':'원래 분기 😀','signature':{'args':[{'name':'amount','type':'long'}],'return':'bool' if control=='branch' else 'void'},'arguments':{'amount':{'input':'amount'}},'implementation':'decision.node.json'}
 if control=='switch':node['executionEnum']={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0},{'id':'positive','name':'Positive','value':7}]}
 g['nodes'].insert(0,node)
 if control=='branch':g['edges'] += [{'from':'decision','port':port,'to':'body'} for port in ['true','false']]
 else:
  g['nodes'].append({'id':'positive','kind':'code','control':'next','branchOwner':'decision','intent':'원래 enum 실행 줄','signature':{'args':[],'return':'void'},'arguments':{},'implementation':'positive.node.json'})
  g['edges'] += [{'from':'decision','port':'case:positive','to':'positive'},{'from':'positive','port':'next','to':'return:decision'},{'from':'decision','port':'next','to':'body'}]
 definitions=call('featureBlueprintNodes',featureSource=fn,graph=g);assert definitions['state']=='node-definitions',definitions
 records={}
 for row in definitions['nodes']:
  if row['definition']['kind']!='code':continue
  name=row['id'];text='return amount+7; // 원문 9223372036854775806\r\n' if name=='body' else ('return amount>0;' if control=='branch' else 'return amount>0?Result.Positive:Result.NoBranch;')+' // 원문 😀\r\n'
  if name=='positive':text='// 원래 실행 줄 😀\r\n'
  records[name]={'schema':1,'node':name,'definitionHash':row['definitionHash'],'source':text,'helpers':'private static long Keep(long x){return x;} // 보조 원문\r\n'}
  (source/(name+'.node.json')).write_text(json.dumps(records[name]))
 (source/'Body.celem').write_text(prepared['implementation']);(source/'body.graph.json').write_text(json.dumps(g))
 before={p:p.read_bytes() for p in root.rglob('*') if p.is_file()};plan=call('implementationCopy',**req);assert all(p.read_bytes()==v for p,v in before.items())
 after=plan['graph'];assert plan['sourceWritten'] is False and after['entry']==g['entry'] and after['edges']==g['edges'] and after['exits']==g['exits'] and after['locals']==g['locals']
 assert after['feature']==g['feature'] and after['contractHash']==g['contractHash'];assert after['copySource']=={'implementation':req['source'],'target':'common','bodyOrigin':req['source'],'sourceKind':'blueprint'}
 assert [(n['id'],n['kind'],n['control']) for n in after['nodes']]==[(n['id'],n['kind'],n['control']) for n in g['nodes']]
 for row in plan['records']:
  original=records[row['id']];assert row['record']['source']==original['source'] and row['record']['helpers']==original['helpers'];assert row['relative']!=next(n['implementation'] for n in g['nodes'] if n['id']==row['id'])
 copied=next(n for n in after['nodes'] if n['id']=='decision');assert copied['signature']==node['signature'] and copied['arguments']==node['arguments'];assert copied.get('executionEnum')==node.get('executionEnum')
 checked('code '+control+' 복사는 원래 FQN 공개 계약·핀/분기 ID·enum 순서/값·route·정확한64비트 값과 C#/보조 원문을 보존하고 source를 쓰지 않는다')
 bad=['bad-id','foreign-owner','stale-record','unknown-route','cycle','unsupported-kind','wrong-control','wrong-branch-type' if control=='branch' else 'duplicate-enum']
 for boundary in bad:
  q=copy.deepcopy(req);broken=copy.deepcopy(g)
  try:
   if boundary=='bad-id':q['implementation']='Source.Branch::Chosen'
   elif boundary=='foreign-owner':q['owner']='Other::Info'
   elif boundary=='stale-record':p=source/'decision.node.json';p.write_text(json.dumps({**records['decision'],'definitionHash':'0'*64}))
   elif boundary=='unknown-route':broken['edges'][0]['to']='missing'
   elif boundary=='cycle':broken['edges'].append({'from':'body','port':'next','to':'decision'})
   elif boundary=='unsupported-kind':broken['nodes'][0]['kind']='graph'
   elif boundary=='wrong-control':broken['nodes'][0]['control']='guess'
   elif boundary=='wrong-branch-type':broken['nodes'][0]['signature']['return']='void'
   else:broken['nodes'][0]['executionEnum']['members'][1]['value']=0
   (source/'body.graph.json').write_text(json.dumps(broken));call('implementationCopy',False,**q)
  finally:
   for p,data in before.items():p.write_bytes(data)
  assert all(p.read_bytes()==v for p,v in before.items())
 checked('code '+control+'의 외부 소유·오래된 record·불명 route·순환·범위 밖 kind·잘못된 실행 계약 8경계는 전체 거절하고 원본을 보존한다')
(root/'result.json').write_text(json.dumps({'checks':checks,'evidence':str(root),'pureMetadata':True,'nativeWindows':False},ensure_ascii=False,indent=2));print(json.dumps({'checks':checks,'evidence':str(root),'pureMetadata':True,'nativeWindows':False},ensure_ascii=False))
