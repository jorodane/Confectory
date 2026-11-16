"""Main -> selected A -> selected B, explicitly authored nominal value returns."""
import copy,hashlib,json
import v666_native_type_chain_fixture as _base
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)
for fn in functions:
 p=f.project/(fn.split('::')[1]+'Body.celem');p.write_text(p.read_text().replace('(int amount)','(int nativeAmount)',1));id=bodies[fn];sources[id]=sources[id].replace('amount','nativeAmount');raw=(f.project/paths[id]).read_bytes();(f.project/paths[id]).write_bytes((b'\xef\xbb\xbf'if raw.startswith(b'\xef\xbb\xbf')else b'')+sources[id].encode())
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};_base.snapshot=snapshot;c.x.original=snapshot

def request(catalog=None):
 catalog=catalog or catalogs();units={}
 for row in f.metadata('describe',project=str(f.manifest))['units']:
  raw=(f.project/row['path']).read_bytes();text=raw.decode('utf-8-sig');units[row['id']]={**row,'draft':text,'original':text,'revision':1,'baseline':hashlib.sha256(raw).hexdigest()}
 choices={fn:next(v for v in cat['nativeTypes']if v['id']==f.n+'Payload')for fn,cat in catalog.items()};payload=choices[first]['clrType'];leaf=next(v['clrType']for v in catalog[first]['nativeTypes']if v['id']==f.n+'Leaf');signatures={fn:dict(args=copy.deepcopy(old['args']),**{'return':choice['clrType']})for fn,choice in choices.items()}
 texts={bodies[first]:'var value=calls.Selected.Invoke(nativeAmount);value.Value.Count=checked(value.Value.Count+31);return value; // 직접 작성한 구조체 반환 caller 😀\r\n',bodies[second]:'return new '+payload+' {Value=new '+leaf+' {Count=nativeAmount+2}}; // 직접 작성한 구조체 반환 callee 😀\r\n',callers[first]:'var value=calls.Connected.Invoke(40);int result=checked((int)value.Value.Count);Console.WriteLine(result);return result; // 직접 작성한 반환 소비자 😀\r\n'};changes=[]
 for index,fn in enumerate(functions):
  choice=choices[fn];signature=signatures[fn];own=catalog[fn]['functionBodies'];assert set(own)=={bodies[fn],callers[fn]},own
  plans={id:{k:entry[k]for k in ['hash','path']}|dict(beforeSignature=entry['signature'],signature=dict(args=copy.deepcopy(entry['signature']['args']),**{'return':signatures[entry['function']]['return']})if entry['function']in signatures else entry['signature'],contract=signature,text=texts[id])for id,entry in own.items()}
  changes.append(dict(type='function-edit',id=fn,hash=hashlib.sha256(units[fn]['draft'].encode()).hexdigest(),name=labels[index],description='',signature=signature,nativeTypes={choice['clrType']:copy.deepcopy(choice['proof']),'$function:'+fn:copy.deepcopy(catalog[fn]['nativeFunctionEdit']['proof'])},mapping=dict(before=copy.deepcopy(old),args=dict(amount='amount'),bodies=plans)))
 return dict(operation='informationDefinitions',project=str(f.manifest),manifest=f.manifest.read_text(),id=owner,text=(f.project/'FreeInfo.celem').read_text(),changes=changes,units=units,drafts=[dict(id=id,text=row['draft'])for id,row in units.items()if row['kind']in['object','schema','function','implementation','module','category','concept','enum']and id!=owner])

def mixed(request):
 r=copy.deepcopy(request);a,b=r['changes'];payload=a['signature']['return'];leaf=next(v['clrType']for v in catalogs()[first]['nativeTypes']if v['id']==f.n+'Leaf');b['signature']=dict(args=[dict(name='amount',type=payload)],**{'return':'int'});b['mapping']['args']['amount']=None;body='var value=calls.Selected.Invoke(new '+payload+' {Value=new '+leaf+' {Count=nativeAmount}});return new '+payload+' {Value=new '+leaf+' {Count=value+31}}; // explicit mixed transition';a['mapping']['bodies'][bodies[first]]['text']=body;b['mapping']['bodies'][bodies[first]]['text']=body
 for id,plan in b['mapping']['bodies'].items():
  plan['contract']=copy.deepcopy(b['signature'])
  if id==bodies[second]:plan['signature']=dict(args=[dict(name='nativeAmount',type=payload)],**{'return':'int'});plan['text']='return checked((int)nativeAmount.Value.Count+2);'
 return r

def apply_request(catalog=None):
 catalog=catalog or catalogs();r=request(catalog);return dict(action='applySlots',id=owner,rows=[],basis=catalog[first]['basis'],declaration=dict(id=owner,hash=f.state()['schema']['textHash'],changes=r['changes']))
def verify(checkpoint):
 document=json.loads(checkpoint.read_text());rows={v['id']:v for v in document['changes']};receipt=rows[owner]['slotSaveReceipt'];assert document['version']==2 and document['nativeTypeProfile']=='native-type-source-guards-v1';assert{'$function:'+fn for fn in functions}<=set(receipt['nativeTypeProofs']);assert set(paths)<=set(receipt['sources']);assert all(p in receipt['readGuards']for p in paths.values());group=rows[owner]['atomicEditGroup'];assert set(functions)|set(paths)|{owner,first+'Body',second+'Body',consumer_body}<=set(group)
 for fn in functions:
  signature=f.metadata('inspect',text=rows[fn]['draft'])['signature'];assert signature['return'].startswith('Confectory.Information.')and[(v['Name'],v['Type'],v.get('Mode','in'))for v in signature['Args']]==[('amount','int','in')]
 for change in receipt['declaration']['changes']:
  if change.get('type')=='function-edit':
   for id,plan in change.get('mapping',{}).get('bodies',{}).items():assert rows[id]['draft']==plan['text']
 for fn in functions:assert f.metadata('inspect',text=rows[fn+'Body']['draft'])['signature']['Args'][0]['Name']=='nativeAmount'
 assert group.count(bodies[first])==1 and group.count(first+'Body')==1;unchanged();return group

def verify_live():
 allowed={'FreeInfo.celem'}|set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{'MainBody.celem'};unchanged(allowed);execute(73,'nominal-return-selected');f.checked('two explicitly authored nominal C# returns execute73 through the original selected import; scalar inputs, Main ABI, aliases and unrelated source bytes retained')
