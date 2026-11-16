"""Explicit nominal input transitions along Main -> selected A -> selected B."""
import copy,hashlib,json,re
import v666_native_type_shared_fixture as _base
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)
callers[second]=bodies[first];consumer_body=f.n+'MainBody'
(f.project/(first.split('::')[1]+'Body.celem')).write_text('implementation '+first+'Body for '+first+' (int amount) -> int {import '+second+' as Selected (int) -> int;body common "'+paths[bodies[first]]+'";}')
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+first+' as Connected (int) -> int;body common "Main.csbody";}')
sources[bodies[first]]='return calls.Selected.Invoke(amount)+30; // 원래 선택 함수 호출 😀\r\n'
sources[callers[first]]='int result=calls.Connected.Invoke(40);Console.WriteLine(result);return result; // 원래 시작 호출자 😀\r\n'
for id,text in sources.items():(f.project/paths[id]).write_bytes((b'\xef\xbb\xbf'if id in [bodies[second],callers[first]]else b'')+text.encode())
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};c.x.original=snapshot

def request(catalog=None):
 catalog=catalog or catalogs();units={}
 for row in f.metadata('describe',project=str(f.manifest))['units']:
  raw=(f.project/row['path']).read_bytes();text=raw.decode('utf-8-sig');units[row['id']]={**row,'draft':text,'original':text,'revision':1,'baseline':hashlib.sha256(raw).hexdigest()}
 choices={fn:next(v for v in cat['nativeTypes']if v['id']==f.n+'Payload')for fn,cat in catalog.items()};payload=choices[first]['clrType'];leaf=next(v['clrType']for v in catalog[first]['nativeTypes']if v['id']==f.n+'Leaf');signatures={fn:dict(args=[dict(name='amount',type=choice['clrType'])],**{'return':'int'})for fn,choice in choices.items()}
 texts={bodies[first]:'return calls.Selected.Invoke(amount)+31; // 직접 작성한 구조체 함수 호출 😀\r\n',bodies[second]:'return checked((int)amount.Value.Count+2); // 직접 작성한 구조체 callee 😀\r\n',callers[first]:'int result=calls.Connected.Invoke(new '+payload+' {Value=new '+leaf+' {Count=40}});Console.WriteLine(result);return result; // 직접 작성한 시작 호출자 😀\r\n'};changes=[]
 for index,fn in enumerate(functions):
  choice=choices[fn];signature=signatures[fn];own=catalog[fn]['functionBodies'];assert set(own)=={bodies[fn],callers[fn]},own
  plans={id:{k:entry[k]for k in ['hash','path']}|dict(beforeSignature=entry['signature'],signature=signatures.get(entry['function'],entry['signature']),contract=signature,text=texts[id])for id,entry in own.items()}
  changes.append(dict(type='function-edit',id=fn,hash=hashlib.sha256(units[fn]['draft'].encode()).hexdigest(),name=labels[index],description='',signature=signature,nativeTypes={choice['clrType']:copy.deepcopy(choice['proof']),'$function:'+fn:copy.deepcopy(catalog[fn]['nativeFunctionEdit']['proof'])},mapping=dict(before=copy.deepcopy(old),args=dict(amount=None),bodies=plans)))
 return dict(operation='informationDefinitions',project=str(f.manifest),manifest=f.manifest.read_text(),id=owner,text=(f.project/'FreeInfo.celem').read_text(),changes=changes,units=units,drafts=[dict(id=id,text=row['draft'])for id,row in units.items()if row['kind']in['object','schema','function','implementation','module','category','concept','enum']and id!=owner])

def unchanged(except_names=()):
 for path,raw in snapshot.items():
  if path not in except_names:assert(f.project/path).read_bytes()==raw,path

def apply_request(catalog=None):
 catalog=catalog or catalogs();r=request(catalog);return dict(action='applySlots',id=owner,rows=[],basis=catalog[first]['basis'],declaration=dict(id=owner,hash=f.state()['schema']['textHash'],changes=r['changes']))
def verify(checkpoint):
 ids=_base._base.verify(checkpoint);rows={r['id']:r for r in json.loads(checkpoint.read_text())['changes']};assert ids.count(bodies[first])==1 and ids.count(first+'Body')==1;header=rows[first+'Body']['draft'];assert ' as Selected ('in header and 'Confectory.Information.'in header;return ids

def verify_live():
 allowed={'FreeInfo.celem'}|set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{'MainBody.celem'};unchanged(allowed);execute(73,'nominal-selected-chain');f.checked('two explicitly selected nominal functions execute73 through their original C# import; unchanged Main ABI, aliases, unrelated sources and permissions retained')
