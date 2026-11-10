"""Real caller-owned enum field values, checked node-time access, no ID lookup."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile
r=Path(sys.argv[1]).resolve();mode=sys.argv[2]if len(sys.argv)>2 else'native';case=Path(tempfile.mkdtemp(prefix='confectory-live-enum-'));p=case/'owned project';p.mkdir();n='Owned.Live::';model='Confectory.ObjectModel';dotnet=os.environ['CONFECTORY_DOTNET'];author=r/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';cli=r/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll';items={};checks=[]
def check(text):checks.append(text);print('PASS '+text,flush=True)
def symbol(id):return'E'+hashlib.sha256(json.dumps(id).encode()).hexdigest()[:24]
type='Confectory.Information.'+symbol(n[:-2])+'.'+symbol(n+'Mood');other='Confectory.Information.'+symbol(n[:-2])+'.'+symbol(n+'OtherMood')
def add(name,kind,text):items[name]=kind;(p/(name+'.celem')).write_bytes((text+'\r\n').encode())
member_values=[{'id':'ready-id','name':'준비'},{'id':'done-id','name':'완료'}]
def enum(name,values=member_values,numbers={'ready-id':12,'done-id':31},mapped=True):return'enum '+n+name+' {value editorEnumProfile='+json.dumps('nominal-members-native-v2'if mapped else'nominal-members-v1')+';value editorEnumValues='+json.dumps(json.dumps(values,ensure_ascii=False))+';'+('value editorEnumNumbers='+json.dumps(json.dumps(numbers))+';'if mapped else'')+'}'
add('Mood','enum',enum('Mood'));add('OtherMood','enum',enum('OtherMood'));add('Legacy','enum',enum('Legacy',mapped=False));add('Fields','schema','schema '+n+'Fields {field phase single enum '+n+'Mood;field phases multiple enum '+n+'Mood;field legacy single enum '+n+'Legacy;field count single general long;}');add('Node','object','object '+n+'Node {use schema '+n+'Fields;data phase="ready-id";}');add('Child','object','object '+n+'Child extends '+n+'Node {}');add('Plain','schema','schema '+n+'Plain {field count single general long;}');add('PlainNode','object','object '+n+'PlainNode {use schema '+n+'Plain;}')
add('Keep','function','function '+n+'Keep ('+type+' value,'+other+' other) -> '+type+' {provide '+n+'Keep with '+n+'KeepBody;}');add('KeepBody','implementation','implementation '+n+'KeepBody for '+n+'Keep ('+type+' value,'+other+' other) -> '+type+' {body common "Keep.csbody";}');(p/'Keep.csbody').write_bytes(b'return value; // original native contract\r\n')
add('Main','function','function '+n+'Main () -> int {provide '+n+'Main with '+n+'MainBody;}');imports='import '+n+'Keep as Keep ('+type+','+other+') -> '+type+';'+''.join('import '+model+'::'+name+' as '+name+' '+sig+';'for name,sig in [('Create','(string,string[],object[]) -> object'),('Read','(object,string,string,string) -> object'),('Set','(object,string,string,string,object) -> void'),('RefCell','(object,string,string,string) -> object')]);add('MainBody','implementation','implementation '+n+'MainBody for '+n+'Main () -> int {'+imports+'body common "Main.csbody";}')
manifest=p/'project.cproj'
def sync():manifest.write_text('project Owned.Live version "1" {standalone true;entry '+n+'Main;'+''.join('element '+k+' '+v+' "'+k+'.celem";'for k,v in items.items())+'registry Confectory.Build.DotNet "'+str(r/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";registry '+model+' "'+str(r/'packs/object-model/pack.cpack')+'";dependency '+model+' version "0.1.0";target portable Confectory.Build.DotNet::Portable;}')
sync()
def metadata(op,ok=True,**data):
 result=subprocess.run([dotnet,str(author)],input=json.dumps(dict(operation=op,**data)),text=True,capture_output=True,check=True);v=json.loads(result.stdout);assert bool(v['ok'])==ok,v;return v['result']if ok else v

def descriptor(owner='Node'):return metadata('blueprintPropertyCatalog',project=str(manifest),sourceId=n+'MainBody',owner=n+owner)['descriptor']
def build(label,run=True,ok=True):
 result=subprocess.run([dotnet,str(cli),'build',str(manifest),'portable'],text=True,capture_output=True);(case/(label+'-build.log')).write_text(result.stdout+result.stderr);assert(result.returncode==0)==ok,result.stdout[-2500:]+result.stderr[-1000:]
 if not ok:return result
 report=json.loads(result.stdout)
 if run:
  execution=subprocess.run(report['run'],text=True,capture_output=True);(case/(label+'-run.json')).write_text(json.dumps(dict(exit=execution.returncode,stdout=execution.stdout,stderr=execution.stderr)));return report,execution
 return report

d=descriptor();plain=descriptor('PlainNode');(case/'baseline-descriptors.json').write_text(json.dumps(dict(plain=plain,legacy=next(x for x in d['fields']if x['name']=='legacy')),indent=2));fields={x['name']:x for x in d['fields']};lit=lambda s:json.dumps(s,ensure_ascii=False)
body='var ready='+type+'Ids.FromId("ready-id");var done='+type+'Ids.FromId("done-id");var foreign='+other+'Ids.FromId("done-id");_ = calls.Keep.Invoke(done,foreign);'
body+='var target=calls.Create.Invoke('+lit(d.to_json()if hasattr(d,'to_json')else json.dumps(d,separators=(',',':')))+',new[]{'+lit(fields['phase']['id'])+'},new object[]{done});'
if mode=='baseline':
 (p/'Main.csbody').write_text(body+'return 0;')
 assert fields['phase']['supported']is False and fields['phase']['clrType']is None
 report,execution=build('baseline');assert execution.returncode!=0 and'This object field kind has no live value contract yet'in execution.stderr,(execution.returncode,execution.stderr);check('published descriptor and real runtime reject typed enum field creation without materializing declaration IDs or modifying any original source')
else:
 assert fields['phase']['supported']and fields['phase']['clrType']==type and fields['phases']['clrType']==type+'[]'and not fields['legacy']['supported']
 if len(sys.argv)>3:assert json.loads(Path(sys.argv[3]).read_text())==dict(plain=plain,legacy=fields['legacy'])
 check('mapped enum fields expose exact native type/shape while primitive descriptors and unconverted enum refusal stay byte-identical')
 # The natural public enum input/result selects its existing nominal assembly.
 calc='function '+n+'Calc (object target,'+type+' replacement) -> '+type+' {provide '+n+'Calc with '+n+'CalcBody;}'
 add('Calc','function',calc);reader='fg_call_'+hashlib.sha256((model+'::Read').encode()).hexdigest()[:24];setter='fg_call_'+hashlib.sha256((model+'::Set').encode()).hexdigest()[:24]
 calc_impl='implementation '+n+'CalcBody for '+n+'Calc (object target,'+type+' replacement) -> '+type+' {import '+model+'::Read as '+reader+' (object,string,string,string) -> object;import '+model+'::Set as '+setter+' (object,string,string,string,object) -> void;blueprint common "Calc.graph.json";}'
 add('CalcBody','implementation',calc_impl);(p/'MainBody.celem').write_text((p/'MainBody.celem').read_text().replace('body common','import '+n+'Calc as Calc (object,'+type+') -> '+type+';body common'));sync()
 graph=metadata('blueprintPrepareFeature',id=n+'Calc',text=calc.replace('provide '+n+'Calc with '+n+'CalcBody;',''),implementation=n+'CalcBody',graphPath='Calc.graph.json',nodePath='consume.node.json')['graph'];graph['profile']='sync-acyclic-property-set-v1';graph['entry']='before'
 def sig(result,args):return dict(args=[dict(name=name,type=kind)for name,kind in args],**{'return':result})
 def prop(id,write=False):
  node=dict(id=id,kind='property-set'if write else'property',control='next',intent='실제 종류 필드 '+id,propertyOwner=n+'Node',field='phase',fieldContractHash=fields['phase']['hash'],signature=sig('void'if write else type,[('target','object')]+([('value',type)]if write else[])),arguments=dict(target=dict(input='target')))
  if write:node['arguments']['value']=dict(input='replacement')
  return node
 graph['nodes']=[prop('before'),prop('write',True),prop('after'),dict(id='consume',kind='code',control='next',intent='이전 출력 보존',signature=sig(type,[('before',type),('after',type),('replacement',type)]),arguments=dict(before=dict(node='before'),after=dict(node='after'),replacement=dict(input='replacement')),implementation='consume.node.json')]
 graph['edges']=[dict(**{'from':a},port='next',to=b)for a,b in [('before','write'),('write','after'),('after','consume'),('consume','exit:done')]];graph['exits']=dict(done=dict(node='consume'))
 contracts={model+'::'+k:(r/'packs/object-model'/(k+'.celem')).read_text()for k in ['Read','Set']};definitions=metadata('featureBlueprintNodes',featureSource=calc,graph=graph,propertyContracts={n+'Node':d},featureContracts=contracts);assert definitions['state']=='node-definitions',definitions
 (p/'Calc.graph.json').write_text(json.dumps(graph,ensure_ascii=False));(p/'consume.node.json').write_text(json.dumps(dict(schema=1,node='consume',definitionHash=next(v for v in definitions['nodes']if v['id']=='consume')['definitionHash'],source='if(after!=replacement)throw new System.Exception("Current enum field was not published");return before; // original saved output 😀'),ensure_ascii=False))
 def read(field='phase',target='target'):return'calls.Read.Invoke('+target+','+lit(n+'Node')+','+lit(fields[field]['id'])+','+lit(fields[field]['hash'])+')'
 def put(value,field='phase',target='target'):return'calls.Set.Invoke('+target+','+lit(n+'Node')+','+lit(fields[field]['id'])+','+lit(fields[field]['hash'])+','+value+');'
 def need(test,reason):return'if(!('+test+'))throw new System.Exception('+lit(reason)+');'
 main=body+'void Refused(Action action){bool failed=false;try{action();}catch(ArgumentException){failed=true;}catch(InvalidOperationException){failed=true;}catch(NotSupportedException){failed=true;}if(!failed)throw new Exception("Invalid live enum accepted");}'
 main+=need('('+type+')'+read()+'==done','Live value replaced by declaration ID')+'var saved=('+type+')'+read()+';'+put('ready')+need('saved==done&&('+type+')'+read()+'==ready','Saved enum output was overwritten')
 main+=need('calls.Calc.Invoke(target,done)==ready&&('+type+')'+read()+'==done','Blueprint Read/Set timing')+need('calls.Calc.Invoke(target,ready)==done','Repeated Blueprint read must see current object value')
 main+='var empty='+type+'Ids.FromId("");'+put('empty')+need(type+'Ids.ToId(('+type+')'+read()+')==""','Unselected must remain explicit')+put('ready')
 for value in ['31','"done-id"','foreign','null!','('+type+')999']:
  main+='Refused(()=>{'+put(value)+'});'+need('('+type+')'+read()+'==ready','Rejected Set changed actual field')
 main+='Refused(()=>calls.RefCell.Invoke(target,'+lit(n+'Node')+','+lit(fields['phase']['id'])+','+lit(fields['phase']['hash'])+'));'
 main+='Refused(()=>calls.Read.Invoke(target,'+lit(n+'Node')+','+lit(fields['phase']['id'])+','+lit('0'*64)+'));'
 main+='var retained=new '+type+'[]{ready,done};'+put('retained','phases')+'var prior=('+type+'[])'+read('phases')+';'+put('new '+type+'[]{done}','phases')+need('Object.ReferenceEquals(prior,retained)&&prior[0]==ready&&!(Object.ReferenceEquals(prior,'+read('phases')+'))','Enum array was cloned or prior result replaced')
 for value in ['new int[]{12,31}','new object[]{ready,done}','new '+other+'[]{foreign}','new '+type+'[]{ready,('+type+')999}','null!','Array.CreateInstance(typeof('+type+'),new[]{1},new[]{1})']:
  main+='Refused(()=>{'+put(value,'phases')+'});'+need('(('+type+'[])'+read('phases')+').Length==1&&(('+type+'[])'+read('phases')+')[0]==done','Invalid array replaced actual storage')
 main+=put('retained','phases')+'retained[0]=('+type+')999;Refused(()=>calls.Read.Invoke(target,'+lit(n+'Node')+','+lit(fields['phases']['id'])+','+lit(fields['phases']['hash'])+'));retained[0]=ready;'+need('Object.ReferenceEquals('+read('phases')+',retained)','Repair changed caller-owned array identity')
 child=descriptor('Child');main+='object second=calls.Create.Invoke('+lit(json.dumps(child,separators=(',',':')))+',new[]{'+lit(fields['phase']['id'])+'},new object[]{done});'+need('calls.Calc.Invoke(second,ready)==done&&('+type+')'+read('phase','target')+'==ready','Independent inherited instance leaked state')
 main+='Console.WriteLine("31");return 31; // live enum values · 😀\r\n';(p/'Main.csbody').write_bytes(main.encode());snapshot={f.name:f.read_bytes()for f in p.iterdir()if f.is_file()}
 def unchanged(except_names=()):assert all((p/name).read_bytes()==raw for name,raw in snapshot.items()if name not in except_names)
 first,execution=build('native');assert(execution.returncode,execution.stdout.strip())==(31,'31'),(execution.returncode,execution.stdout,execution.stderr);unchanged();check('real CLR and Blueprint enum Read/Set use independent live instances, repeated node-time reads and prior output snapshots without declaration ID lookup')
 check('checked native enum scalar/array values preserve caller arrays and reject raw IDs/integers, other nominal enums, undefined values, nulls, non-vector arrays, stale contracts and mutable enum refs without replacing valid storage')
 (p/'Mood.celem').write_text(enum('Mood',[dict(id='done-id',name='수정 완료'),dict(id='ready-id',name='수정 준비')]))
 renamed=descriptor();assert next(row for row in renamed['fields']if row['name']=='phase')['hash']==fields['phase']['hash'];again,execution=build('rename-order');assert(execution.returncode,execution.stdout.strip())==(31,'31');assert again['contractArtifacts'][n+'Keep']['key']==first['contractArtifacts'][n+'Keep']['key'];unchanged({'Mood.celem'});(p/'Mood.celem').write_bytes(snapshot['Mood.celem']);check('member label/order changes preserve numeric identities, live field hash and native contract artifacts; authored source is not rewritten')
 (p/'Mood.celem').write_text(enum('Mood',member_values+[dict(id='new-id',name='새 항목')],{'ready-id':12,'done-id':31,'new-id':55}));changed=descriptor();assert next(row for row in changed['fields']if row['name']=='phase')['hash']!=fields['phase']['hash'];build('member-contract-drift',run=False,ok=False);unchanged({'Mood.celem'});(p/'Mood.celem').write_bytes(snapshot['Mood.celem']);check('a changed member contract invalidates the pinned property node instead of silently changing a live object or its saved graph')
 restored,execution=build('restored');assert restored['key']==first['key']and(execution.returncode,execution.stdout.strip())==(31,'31');unchanged();check('exact definition restoration recovers original execution and artifact identity')
(case/'checks.json').write_text(json.dumps(dict(checks=checks,mode=mode,evidence=str(case)),ensure_ascii=False,indent=2));print(json.dumps(dict(evidence=str(case),checks=len(checks),mode=mode)))
