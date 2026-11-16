"""Explicit scalar -> information value array returns along selected C# imports."""
import copy,json
import v666_native_return_struct_fixture as _base
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)

def request(catalog=None):
 catalog=catalog or catalogs();r=_base.request(catalog);payload=r['changes'][0]['signature']['return'];leaf=next(v['clrType']for v in catalog[first]['nativeTypes']if v['id']==f.n+'Leaf')
 texts={bodies[first]:'var values=calls.Selected.Invoke(nativeAmount);var alias=values;alias[0].Value.Count=checked(alias[0].Value.Count+31);return values; // 직접 작성한 배열 반환과 같은 배열 별칭 😀\r\n',bodies[second]:'return new '+payload+'[] {new '+payload+' {Value=new '+leaf+' {Count=nativeAmount+2}},new '+payload+' {Value=new '+leaf+' {Count=1}}}; // 순서를 보존한 두 구조체 값 😀\r\n',callers[first]:'var values=calls.Connected.Invoke(40);if(values.Length!=2||values[1].Value.Count!=1)throw new Exception("array shape/order lost");int result=checked((int)values[0].Value.Count);Console.WriteLine(result);return result; // 직접 작성한 배열 소비자 😀\r\n'}
 for row in r['changes']:
  row['signature']['return']+='[]'
  for id,plan in row['mapping']['bodies'].items():
   plan['contract']=copy.deepcopy(row['signature'])
   if id in bodies.values():plan['signature']['return']+='[]'
   plan['text']=texts[id]
 return r

def mixed(r,catalog=None):
 catalog=catalog or catalogs();r=copy.deepcopy(r);a,b=r['changes'];payload=a['signature']['return'][:-2];leaf=next(v['clrType']for v in catalog[first]['nativeTypes']if v['id']==f.n+'Leaf');b['signature']=dict(args=[dict(name='amount',type=payload)],**{'return':'int'});b['mapping']['args']['amount']=None;body='int value=calls.Selected.Invoke(new '+payload+' {Value=new '+leaf+' {Count=nativeAmount}});return new '+payload+'[] {new '+payload+' {Value=new '+leaf+' {Count=value+31}},new '+payload+' {Value=new '+leaf+' {Count=1}}};'
 a['mapping']['bodies'][bodies[first]]['text']=body;b['mapping']['bodies'][bodies[first]]['text']=body
 for id,plan in b['mapping']['bodies'].items():
  plan['contract']=copy.deepcopy(b['signature'])
  if id==bodies[second]:plan['signature']=dict(args=[dict(name='nativeAmount',type=payload)],**{'return':'int'});plan['text']='return checked((int)nativeAmount.Value.Count+2);'
 return r

def unsupported(r,kind,catalog=None):
 catalog=catalog or catalogs();r=copy.deepcopy(r)
 if kind=='array-input':
  payload=r['changes'][0]['signature']['return'][:-2];leaf=next(v['clrType']for v in catalog[first]['nativeTypes']if v['id']==f.n+'Leaf')
  texts={bodies[first]:'return calls.Selected.Invoke(nativeAmount)+31;',bodies[second]:'return checked((int)nativeAmount[0].Value.Count+2);',callers[first]:'int result=calls.Connected.Invoke(new '+payload+'[] {new '+payload+' {Value=new '+leaf+' {Count=40}}});Console.WriteLine(result);return result;'}
  for row in r['changes']:
   row['signature']=dict(args=[dict(name='amount',type=payload+'[]')],**{'return':'int'});row['mapping']['args']['amount']=None
   for id,plan in row['mapping']['bodies'].items():
    plan['contract']=copy.deepcopy(row['signature']);plan['text']=texts[id]
    if id in bodies.values():plan['signature']=dict(args=[dict(name='nativeAmount',type=payload+'[]')],**{'return':'int'})
  return r
 for row in r['changes']:
  fn=row['id'];base=row['signature']['return'][:-2]
  if kind=='reference-array':
   choice=next(v['reference']for v in catalog[fn]['nativeTypes']if v['id']==f.n+'Leaf');base=choice['clrType'];row['nativeTypes']={base:copy.deepcopy(choice['proof']),'$function:'+fn:row['nativeTypes']['$function:'+fn]}
  selected=base+('[][]'if kind=='jagged-array'else'[]');row['signature']['return']=selected
  for id,plan in row['mapping']['bodies'].items():
   plan['contract']=copy.deepcopy(row['signature'])
   if id in bodies.values():plan['signature']['return']=selected;plan['text']='return System.Array.Empty<'+selected[:-2]+'>();'
   else:plan['text']='return 0;'
 return r

def apply_request(catalog=None):
 catalog=catalog or catalogs();r=request(catalog);return dict(action='applySlots',id=owner,rows=[],basis=catalog[first]['basis'],declaration=dict(id=owner,hash=f.state()['schema']['textHash'],changes=r['changes']))
def verify(checkpoint):
 ids=_base.verify(checkpoint);rows={v['id']:v for v in json.loads(checkpoint.read_text())['changes']};receipt=rows[owner]['slotSaveReceipt']
 for fn in functions:
  signature=f.metadata('inspect',text=rows[fn]['draft'])['signature'];assert signature['return'].endswith('[]')and not signature['return'].endswith('[][]');assert signature['return'][:-2]in receipt['nativeTypeProofs']and signature['return']not in receipt['nativeTypeProofs']
 return ids
def verify_live():
 allowed={'FreeInfo.celem'}|set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{'MainBody.celem'};unchanged(allowed);execute(73,'nominal-array-return-selected');f.checked('two explicitly authored value array returns execute73; element order, shared array alias, scalar inputs, Main ABI, native aliases and unrelated source bytes retained')
