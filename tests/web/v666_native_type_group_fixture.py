"""Two independently owned native input plans retain per-function nominal proofs."""
import copy,hashlib,json,subprocess
import v666_connected_native_fixture as c
f,owner=c.f,c.owner
first=c.fn;second=owner+'_Function_'+'f'*32;functions=[first,second];labels=['첫 구조체 계약','둘째 구조체 계약'];old=dict(args=[dict(name='amount',type='int')],**{'return':'int'})
second_local=second.split('::')[1];consumer=f.n+'SecondConsumer';consumer_body=consumer+'Body';bodies={first:c.body_id,second:second+'Body/body:common'};callers={first:c.caller_id,second:consumer_body+'/body:common'};paths={bodies[first]:c.body_path,bodies[second]:'second-native.csbody',callers[first]:'Main.csbody',callers[second]:'second-consumer.csbody'}
(f.project/'FreeInfo.celem').write_text((f.project/'FreeInfo.celem').read_text().replace('{','{contain function '+second+';',1))
rows=[(second_local,'function','elements/'+second_local+'.celem','function '+second+' (int amount) -> int {provide '+second+' with '+second+'Body;value editorName="둘째 구조체 계약";}'),(second_local+'Body','implementation',second_local+'Body.celem','implementation '+second+'Body for '+second+' (int amount) -> int {body common "second-native.csbody";}'),('SecondConsumer','function','SecondConsumer.celem','function '+consumer+' () -> int {provide '+consumer+' with '+consumer_body+';}'),('SecondConsumerBody','implementation','SecondConsumerBody.celem','implementation '+consumer_body+' for '+consumer+' () -> int {import '+second+' as Selected (int) -> int;body common "second-consumer.csbody";}')]
for name,kind,path,text in rows:
 (f.project/path).write_text(text);f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element '+name+' '+kind+' "'+path+'";registry Confectory.Build.DotNet',1))
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+first+' as Connected (int) -> int;import '+consumer+' as SecondConsumer () -> int;body common "Main.csbody";}')
sources={bodies[first]:c.original,bodies[second]:'return amount; // 둘째 원래 본문 😀\r\n',callers[first]:'int result=calls.Connected.Invoke(30)+calls.SecondConsumer.Invoke();Console.WriteLine(result);return result; // 원래 호출자 😀\r\n',callers[second]:'return calls.Selected.Invoke(40); // 둘째 원래 호출자 😀\r\n'}
for id,text in sources.items():(f.project/paths[id]).write_bytes((b'\xef\xbb\xbf'if id==bodies[second]else b'')+text.encode())
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};c.x.original=snapshot

def unchanged(except_names=()):c.x.unchanged(except_names)
def catalogs():
 result={}
 for fn in functions:
  f.invoke('schema',dict(id=owner));s=f.state()['schema'];result[fn]=f.invoke('blueprint',dict(action='readOwnerEdits',id=owner,hash=s['textHash'],includeNativeTypes=True,nativeFunction=fn,includeFunctionInputs=fn,includeFunctionBodies=True))['result']['result']
 return result

def request(catalog=None):
 catalog=catalog or catalogs();units={}
 for row in f.metadata('describe',project=str(f.manifest))['units']:
  raw=(f.project/row['path']).read_bytes();text=raw.decode('utf-8-sig');units[row['id']]={**row,'draft':text,'original':text,'revision':1,'baseline':hashlib.sha256(raw).hexdigest()}
 changes=[]
 for index,fn in enumerate(functions):
  cat=catalog[fn];choice=next(v for v in cat['nativeTypes']if v['id']==f.n+'Payload');payload=choice['clrType'];leaf=next(v['clrType']for v in cat['nativeTypes']if v['id']==f.n+'Leaf');signature=dict(args=[dict(name='amount',type=payload)],**{'return':'int'});texts={bodies[fn]:'return checked((int)amount.Value.Count+'+str(index+1)+'); // 직접 작성한 구조체 본문 😀\r\n',callers[fn]:('int result=calls.Connected.Invoke(new '+payload+' {Value=new '+leaf+' {Count=30}})+calls.SecondConsumer.Invoke();Console.WriteLine(result);return result; // 직접 작성한 구조체 호출자 😀\r\n'if index==0 else'return calls.Selected.Invoke(new '+payload+' {Value=new '+leaf+' {Count=40}}); // 직접 작성한 둘째 호출자 😀\r\n')}
  own=cat['functionBodies'];assert set(own)==set(texts),own
  plans={id:{k:entry[k]for k in ['hash','path']}|dict(beforeSignature=entry['signature'],signature=entry['signature']if entry['caller']else signature,contract=signature,text=texts[id])for id,entry in own.items()}
  changes.append(dict(type='function-edit',id=fn,hash=hashlib.sha256(units[fn]['draft'].encode()).hexdigest(),name=labels[index],description='',signature=signature,nativeTypes={payload:copy.deepcopy(choice['proof']),'$function:'+fn:copy.deepcopy(cat['nativeFunctionEdit']['proof'])},mapping=dict(before=copy.deepcopy(old),args=dict(amount=None),bodies=plans)))
 return dict(operation='informationDefinitions',project=str(f.manifest),manifest=f.manifest.read_text(),id=owner,text=(f.project/'FreeInfo.celem').read_text(),changes=changes,units=units,drafts=[dict(id=id,text=row['draft'])for id,row in units.items()if row['kind']in['object','schema','function','implementation','module','category','concept','enum']and id!=owner])

def prepare(request,ok=True):
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),env=f.env,text=True,capture_output=True,check=True);value=json.loads(p.stdout);assert bool(value['ok'])==ok,value;return value

def execute(expected,label):c.execute(expected,label)

def apply_request(catalog=None):
 catalog=catalog or catalogs();r=request(catalog);return dict(action='applySlots',id=owner,rows=[],basis=catalog[first]['basis'],declaration=dict(id=owner,hash=f.state()['schema']['textHash'],changes=r['changes']))
def verify(checkpoint):
 document=json.loads(checkpoint.read_text());units={r['id']:r for r in document['changes']};receipt=units[owner]['slotSaveReceipt'];assert document['version']==2 and document['nativeTypeProfile']=='native-type-source-guards-v1';assert{'$function:'+fn for fn in functions}<=set(receipt['nativeTypeProofs']);assert set(paths)<=set(receipt['sources']);assert all(path in receipt['readGuards']for path in paths.values());assert len(receipt['nativeTypeReads'])>=2;group=units[owner]['atomicEditGroup'];assert set(functions)|set(paths)|{owner}<=set(group)
 for fn in functions:
  signature=f.metadata('inspect',text=units[fn]['draft'])['signature'];assert signature['return']=='int'and len(signature['Args'])==1 and signature['Args'][0]['Type'].startswith('Confectory.Information.')
 unchanged();return group

def verify_live():
 allowed={str((f.project/'FreeInfo.celem').relative_to(f.project))}|set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{'MainBody.celem','SecondConsumerBody.celem'};unchanged(allowed);execute(73,'nominal-selected');f.checked('two explicitly authored native nominal input plans execute73 through independent original C# callers; unselected definitions, helpers and external sources retained')
