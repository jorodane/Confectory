"""Immutable private selection/current ABI candidate; isolated source fixture, no host/account/run."""
import copy,json,os,pathlib,subprocess,sys,tempfile,hashlib
repo=pathlib.Path(sys.argv[1]).resolve();dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet');dll=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-private-seed-'));n='Owned.Private::'
def call(operation,ok=True,**data):
 p=subprocess.run([dotnet,str(dll)],input=json.dumps({'operation':operation,**data}),text=True,capture_output=True,check=True);v=json.loads(p.stdout);assert bool(v['ok'])==ok,(operation,v);return v.get('result') if ok else v
nested='nested' in sys.argv[2:];general='remap' in sys.argv[2:];closure='closure' in sys.argv[2:];assert not closure or nested and general
registered='registered' in sys.argv[2:];callee='Lib::Native' if registered else n+'Native'
fn='function '+n+'Calc (long amount) -> long {provide '+n+'Calc with '+n+'Donor;}'
old='function '+callee+' (ref long amount) -> long {}';new='function '+callee+' (int step,double renamed,out long total) -> bool {}';owner='object '+n+'Owner {}'
base=call('blueprintPrepareFeature',id=n+'Calc',text='function '+n+'Calc (long amount) -> long {}',implementation=n+'Donor',graphPath='donor.graph.json',nodePath='donor.node.json');base=call('blueprintPrepareCall',id=n+'Donor',text=base['implementation'],targetText=old,graph=base['graph'],definition={'id':'native','feature':callee,'intent':'호출','control':'next'})
g=base['graph'];g['profile']='sync-acyclic-switch-v1';g['entry']='native';g['edges'].append({'from':'native','port':'next','to':'body'});node=next(v for v in g['nodes'] if v['id']=='native');node['arguments']={'amount':{'input':'amount'}};next(v for v in g['nodes'] if v['id']=='body')['arguments']={'amount':{'node':'native'}}
enum={'primary':'next','members':[{'id':'next','name':'NoBranch','value':0}]};wrapper=call('blueprintCallWrapper',functionText=old,executionEnum=enum,returnMapping='native-return-out-v1',source='return Result.NoBranch;');node.update(control='switch',executionEnum=enum,postCall={'mode':'execution-enum','returnMapping':'native-return-out-v1','contractHash':wrapper['contractHash'],'source':wrapper['source'],'helpers':''})
if nested:
 new=new if general else old.replace('(ref long','(long');private_sig={'args':[{'name':'amount','type':'long'}],'return':'long'};child={'schema':1,'profile':'sync-acyclic-switch-v1','entry':'native','nodes':[copy.deepcopy(node)],'edges':[{'from':'native','port':'next','to':'exit:return'}],'exits':{'return':{'node':'native'}},'locals':[{'id':'kept','name':'정확한 값','type':'long','initial':{'constant':9223372036854775806}}]};g['profile']='sync-acyclic-nested-v1';g['nodes']=[{'id':'frame','kind':'graph','control':'next','intent':'원래 내부 호출','signature':private_sig,'arguments':{'amount':{'input':'amount'}},'graph':child},next(v for v in g['nodes'] if v['id']=='body')];g['nodes'][1]['arguments']['amount']={'node':'frame'};g['entry']='frame';g['edges']=[{'from':'frame','port':'next','to':'body'},{'from':'body','port':'next','to':'exit:return'}]
if closure:
 other=copy.deepcopy(g['nodes'][0]);other['id']='other';g['nodes'].insert(1,other);g['edges']=[{'from':'frame','port':'next','to':'other'},{'from':'other','port':'next','to':'body'},{'from':'body','port':'next','to':'exit:return'}]
defs=call('featureBlueprintNodes',featureSource=fn,graph=g,featureContracts={callee:old});record={'schema':1,'node':'body','definitionHash':next(v for v in defs['nodes'] if v['id']=='body')['definitionHash'],'source':'return amount+7;'}
texts={'Calc.celem':fn,'Native.celem':old,'Owner.celem':owner,'Donor.celem':base['implementation'].replace('\n}', '\nbody windows "donor.windows.csbody";\n}'),'donor.graph.json':json.dumps(g),'donor.node.json':json.dumps(record),'donor.windows.csbody':'return amount+101;'}
for f,v in texts.items():(root/f).write_text(v)
project=root/'project.cproj';project.write_text('project Owned.Private version "1" {standalone true;entry '+n+'Calc;'+''.join('element '+name+' '+kind+' "'+name+'.celem";' for name,kind in [('Calc','function'),('Native','function'),('Owner','object'),('Donor','implementation')])+'registry Confectory.Build.DotNet \"'+str(repo/'targets/dotnet/pack.cpack')+'\";dependency Confectory.Build.DotNet version \"0.1.0\";target linux Confectory.Build.DotNet::Linux;}')
callee_path=root/'Native.celem'
if registered:
 lib=root/'Lib';lib.mkdir();callee_path=lib/'Native.celem';callee_path.write_text(old);(lib/'pack.cpack').write_text('pack Lib version "1" {element Native function "Native.celem";}');project.write_text(project.read_text().replace('element Native function "Native.celem";','').replace('registry Confectory.Build.DotNet','registry Lib "Lib/pack.cpack";dependency Lib version "1";registry Confectory.Build.DotNet'))
request={'action':'prepare','project':str(project),'owner':n+'Owner','ownerText':owner,'feature':n+'Calc','source':n+'Donor','target':'common','implementation':n+'NewCopy'}
original=call('implementationCopy',**request);snapshot=copy.deepcopy(original['snapshot']);seed={'schema':1,'identity':'A'*64,'scopeGuard':'b'*64,'contentFingerprint':'c'*64,'legacyFingerprint':'d'*64,'snapshot':snapshot}
query={**request,'seed':seed,'identity':'A'*64,'ownerBasisHash':snapshot['ownerHash'],'scopeGuard':'b'*64,'contextGuard':'e'*64,'initialize':True,'preview':True,**({'privatePath':'frame'} if nested else {})};selected=call('implementationCopy',**query);query.update(seed=selected['seed'],initialize=False);sealed=json.dumps(query['seed'],sort_keys=True);call('privateCopySeed',seed=query['seed'],identity=query['identity'],project=str(project));same=call('implementationCopy',**{**query,'preview':False});assert next(r for r in same['records'] if r['id']=='body')['record']['source']=='return amount+7;';print('PASS general ABI immutable seed validates and unchanged current-source candidate preserves original body/provenance')
# Advance only fixture current files. The private immutable bytes remain generation zero.
callee_path.write_text(new);before={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()};fresh=call('implementationCopy',**query);row=next(r for r in fresh['preview']['nodes'] if r['id']=='native');assert row['postCallStale'] and row['callAbiAvailable'],row
if nested:
 strict=call('featureBlueprintNodes',featureSource=fn,graph=snapshot['graph'],featureContracts={callee:new});assert strict['state']=='invalid';inspection=call('featureBlueprintNodes',featureSource=fn,graph=snapshot['graph'],featureContracts={callee:new},inspectStalePostCalls=True);assert inspection['state']=='node-definitions';assert next(r for r in inspection['nestedNodes'] if r['id']=='frame/native')['postCallStale']
 other=copy.deepcopy(snapshot['graph']);frame=copy.deepcopy(other['nodes'][0]);frame['id']='elsewhere';other['nodes'].append(frame);call('blueprintCallAbi',False,id=n+'NewCopy',text=snapshot['implementationText'],graph=other,privatePath='frame',node='native',signature=row['currentCallSignature'],contractHash=row['postCallEditor']['contractHash'],previewRemap=True);assert all((root/k).read_bytes()==v for k,v in before.items());print('PASS private stale inspection never relaxes ordinary validation; the single-use API cannot acquire a multi-frame scope or change either frame')
plan={'source':row['postCall']['source'],'helpers':row['postCall'].get('helpers',''),'executionEnum':row['executionEnum'],'contractHash':row['postCallEditor']['contractHash'],'refreshFrom':row['postCall']['contractHash'],'returnMapping':row['postCall']['returnMapping'],'abi':{'signature':row['currentCallSignature'],'sourceHash':row['callAbiSourceHash'],'privateCopyBinding':row['privateCopyAbiBinding'],'receipt':row['callAbiReceipt'],'remap':{'inputs':{'step':{'valueJson':'3'},'renamed':'amount'},'outputs':{'return':'total'}}}}
if nested and not general:plan['abi'].pop('remap')
if closure:
 assert set(row['callAbiUseGroupPlans'])=={'frame/native','other/native'} and row['privateCopyAbiBinding']['useGroup']==row['callAbiUseGroupBinding']
 plans=copy.deepcopy(row['callAbiUseGroupPlans'])
 for key,p in plans.items():p['remap']={'inputs':{'step':{'valueJson':'5' if key=='other/native' else '3'},'renamed':'amount'},'outputs':{'return':'total'}}
 plan['abi'].update(useGroup=row['callAbiUseGroupBinding'],usePlans=plans)
command={**query,'preview':False,'edits':[{'type':'wrapper','node':'frame/native' if nested else 'native','text':json.dumps(plan)},{'type':'source','node':'body','text':'return amount+9007199254740993L;'}]};unchanged=call('implementationCopy',**{**command,'edits':command['edits'][:1]});assert unchanged['records']==snapshot['records'];prepared=call('implementationCopy',**command);assert next(r for r in prepared['records'] if r['id']=='body')['record']['source'].endswith('9007199254740993L;');assert prepared['graph']['copySource']==snapshot['graph']['copySource'];assert '(ref long)' not in prepared['implementation'];assert json.dumps(query['seed'],sort_keys=True)==sealed;assert all((root/k).read_bytes()==v for k,v in before.items());print('PASS explicit private ABI plan joins original snapshot/body edit, current typed import and wrapper in a pure candidate; donor/other target untouched')
if nested:
 expected=copy.deepcopy(snapshot['graph']);selected=expected['nodes'][0]['graph']['nodes'][0];selected['signature']=copy.deepcopy(row['currentCallSignature']);selected['postCall']['contractHash']=row['postCallEditor']['contractHash'];
 if general:selected['arguments']={'step':{'constant':3},'renamed':{'input':'amount'}};expected['nodes'][0]['graph']['exits']['return']={'node':'native','output':'total'}
 if closure:
  other=expected['nodes'][1]['graph']['nodes'][0];other['signature']=copy.deepcopy(row['currentCallSignature']);other['postCall']['contractHash']=row['postCallEditor']['contractHash'];other['arguments']={'step':{'constant':5},'renamed':{'input':'amount'}};expected['nodes'][1]['graph']['exits']['return']={'node':'native','output':'total'}
 assert prepared['graph']==expected;assert row['privateCopyAbiBinding']['node']=='frame/native' and row['privateCopyAbiBinding']['privatePath']=='frame';print('PASS entire root/private graph, exact int64/locals/ports and provenance preserve all bytes outside the explicitly selected signature/hash/input/output correspondence')
validation=subprocess.run([dotnet,str(repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'validate',str(project),'linux'],text=True,capture_output=True);diagnostics=json.loads(validation.stdout);assert validation.returncode==1 and diagnostics['ok'] is False and any(d['code']=='CONTRACT_MISMATCH' and pathlib.Path(d['location']['file']).name=='Donor.celem' for d in diagnostics['diagnostics']),diagnostics;assert all((root/k).read_bytes()==v for k,v in before.items());print('PASS real compiler validation still rejects the unchanged stale donor with CONTRACT_MISMATCH; pure private candidate never auto-repairs it')
for boundary in ['no-explicit-plan','binding','seed','identity','owner','project','source-change','plan-unknown','stale-wrapper','provenance']:
 q=copy.deepcopy(command)
 if boundary=='no-explicit-plan':q['edits']=q['edits'][1:]
 elif boundary=='binding':v=json.loads(q['edits'][0]['text']);v['abi']['privateCopyBinding']['guard']='0'*64;q['edits'][0]['text']=json.dumps(v)
 elif boundary=='seed':q['seed']['snapshot']['records'][0]['record']['source']='return 1;'
 elif boundary=='identity':q['identity']='B'*64
 elif boundary=='owner':q['ownerBasisHash']='0'*64
 elif boundary=='project':q['project']=str(root/'other.cproj')
 elif boundary=='source-change':(root/'donor.windows.csbody').write_text('return amount+202;');(root/'donor.node.json').write_text(json.dumps({**record,'source':'return amount+99;'}))
 elif boundary=='plan-unknown':v=json.loads(q['edits'][0]['text']);v['abi']['autoApprove']=True;q['edits'][0]['text']=json.dumps(v)
 elif boundary=='stale-wrapper':v=json.loads(q['edits'][0]['text']);v['refreshFrom']='0'*64;q['edits'][0]['text']=json.dumps(v)
 elif boundary=='provenance':q['seed']['snapshot']['graph']['copySource']['implementation']=n+'Other'
 call('implementationCopy',False,**q)
 if boundary=='source-change':
  for k,v in before.items():(root/k).write_bytes(v)
assert all((root/k).read_bytes()==v for k,v in before.items());print('PASS ten missing/forged/stale/foreign/source-change boundaries reject without writes or seed rebasing; cold JSON seed retains original identity')
if closure:
 for boundary in ['no-use-group','no-use-plans','missing-use','unknown-use','wrong-path','stale-group','last-output','selected-mismatch','overlap']:
  q=copy.deepcopy(command);v=json.loads(q['edits'][0]['text'])
  if boundary=='no-use-group':v['abi'].pop('useGroup')
  elif boundary=='no-use-plans':v['abi'].pop('usePlans')
  elif boundary=='missing-use':v['abi']['usePlans'].pop('other/native')
  elif boundary=='unknown-use':v['abi']['usePlans']['foreign/native']=copy.deepcopy(v['abi']['usePlans']['other/native'])
  elif boundary=='wrong-path':v['abi']['usePlans']['other/native']['privatePath']='frame'
  elif boundary=='stale-group':v['abi']['useGroup']['recordsHash']='0'*64
  elif boundary=='last-output':v['abi']['usePlans']['other/native']['remap']['outputs']['return']='return'
  elif boundary=='selected-mismatch':v['abi']['remap']['inputs']['step']['valueJson']='7'
  elif boundary=='overlap':q['edits'].insert(1,copy.deepcopy(q['edits'][0]))
  q['edits'][0]['text']=json.dumps(v);call('implementationCopy',False,**q)
  assert all((root/k).read_bytes()==v for k,v in before.items()) and json.dumps(query['seed'],sort_keys=True)==sealed
 print('PASS complete new-copy use plans reject nine missing/stale/path/last-output/overlap requests atomically without seed or source changes')
if registered:
 for fault in ['no-receipt','receipt-id','binding-receipt','registry-manifest','callee-text','dependency']:
  q=copy.deepcopy(command);v=json.loads(q['edits'][0]['text'])
  if fault=='no-receipt':v['abi'].pop('receipt')
  elif fault=='receipt-id':v['abi']['receipt']['id']='Lib::Other'
  elif fault=='binding-receipt':v['abi']['privateCopyBinding']['receipt']['manifestHash']='0'*64
  elif fault=='registry-manifest':(lib/'pack.cpack').write_bytes(before['Lib/pack.cpack']+b' ')
  elif fault=='callee-text':callee_path.write_text(new.replace('{}','{description "same ABI, different source";}'))
  else:project.write_text(project.read_text().replace('dependency Lib version "1";',''))
  q['edits'][0]['text']=json.dumps(v);call('implementationCopy',False,**q)
  for path,value in before.items():(root/path).write_bytes(value)
  assert json.dumps(query['seed'],sort_keys=True)==sealed
 print('PASS registered receipt/identity/manifest/source/dependency changes reject the complete immutable candidate without source writes or seed rebasing')
print(json.dumps({'pureMetadata':True,'compilerValidation':True,'actualEngine':False,'nativeWindows':False,'accountOrInference':False,'evidence':str(root)}))
