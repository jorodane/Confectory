"""Two explicit nominal input plans share one original C# caller body."""
import copy,hashlib,json,re
import v666_native_type_group_fixture as _base
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)
old_consumer_body=consumer_body;old_caller=callers[second]
for path in ['SecondConsumer.celem','SecondConsumerBody.celem','second-consumer.csbody']:(f.project/path).unlink()
text=f.manifest.read_text()
for line in ['element SecondConsumer function "SecondConsumer.celem";','element SecondConsumerBody implementation "SecondConsumerBody.celem";']:assert line in text;text=text.replace(line,'')
f.manifest.write_text(text);paths.pop(old_caller);sources.pop(old_caller);callers[second]=callers[first];consumer_body=f.n+'MainBody'
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+first+' as Connected (int) -> int;import '+second+' as SecondSelected (int) -> int;body common "Main.csbody";}')
sources[callers[first]]='int result=calls.Connected.Invoke(30)+calls.SecondSelected.Invoke(40);Console.WriteLine(result);return result; // 원래 공유 C# 호출자 😀\r\n'
(f.project/'Main.csbody').write_bytes(b'\xef\xbb\xbf'+sources[callers[first]].encode())
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_base.snapshot=snapshot;c.x.original=snapshot

def request(catalog=None):
 catalog=catalog or catalogs();units={}
 for row in f.metadata('describe',project=str(f.manifest))['units']:
  raw=(f.project/row['path']).read_bytes();text=raw.decode('utf-8-sig');units[row['id']]={**row,'draft':text,'original':text,'revision':1,'baseline':hashlib.sha256(raw).hexdigest()}
 choices={fn:next(v for v in cat['nativeTypes']if v['id']==f.n+'Payload')for fn,cat in catalog.items()};leaf=next(v['clrType']for v in catalog[first]['nativeTypes']if v['id']==f.n+'Leaf');payload=choices[first]['clrType'];shared='int result=calls.Connected.Invoke(new '+payload+' {Value=new '+leaf+' {Count=30}})+calls.SecondSelected.Invoke(new '+payload+' {Value=new '+leaf+' {Count=40}});Console.WriteLine(result);return result; // 직접 작성한 같은 공유 본문 😀\r\n';changes=[]
 for index,fn in enumerate(functions):
  choice=choices[fn];signature=dict(args=[dict(name='amount',type=choice['clrType'])],**{'return':'int'});texts={bodies[fn]:'return checked((int)amount.Value.Count+'+str(index+1)+'); // 직접 작성한 구조체 본문 😀\r\n',callers[fn]:shared};own=catalog[fn]['functionBodies'];assert set(own)==set(texts),own
  plans={id:{k:entry[k]for k in ['hash','path']}|dict(beforeSignature=entry['signature'],signature=entry['signature']if entry['caller']else signature,contract=signature,text=texts[id])for id,entry in own.items()}
  changes.append(dict(type='function-edit',id=fn,hash=hashlib.sha256(units[fn]['draft'].encode()).hexdigest(),name=labels[index],description='',signature=signature,nativeTypes={choice['clrType']:copy.deepcopy(choice['proof']),'$function:'+fn:copy.deepcopy(catalog[fn]['nativeFunctionEdit']['proof'])},mapping=dict(before=copy.deepcopy(old),args=dict(amount=None),bodies=plans)))
 return dict(operation='informationDefinitions',project=str(f.manifest),manifest=f.manifest.read_text(),id=owner,text=(f.project/'FreeInfo.celem').read_text(),changes=changes,units=units,drafts=[dict(id=id,text=row['draft'])for id,row in units.items()if row['kind']in['object','schema','function','implementation','module','category','concept','enum']and id!=owner])

def apply_request(catalog=None):
 catalog=catalog or catalogs();r=request(catalog);return dict(action='applySlots',id=owner,rows=[],basis=catalog[first]['basis'],declaration=dict(id=owner,hash=f.state()['schema']['textHash'],changes=r['changes']))
def verify(checkpoint):
 ids=_base.verify(checkpoint);rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};assert ids.count(callers[first])==1 and ids.count(consumer_body)==1;assert 'SecondSelected'in rows[consumer_body]['draft'];return ids
def verify_live():
 allowed={'FreeInfo.celem'}|set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{'MainBody.celem'};unchanged(allowed);execute(73,'nominal-shared-selected');f.checked('one explicitly authored shared C# caller and two nominal native bodies execute73; caller ABI, original aliases, definitions, external bytes and permissions retained')
