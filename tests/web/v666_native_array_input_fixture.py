"""Explicit information value-array inputs with unchanged native names and scalar returns."""
import copy,json
import v666_native_return_struct_fixture as _base
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)
multiple=True

def request(catalog=None):
 catalog=catalog or catalogs();r=_base.request(catalog);payload=r['changes'][0]['signature']['return'];leaf=next(v['clrType']for v in catalog[first]['nativeTypes']if v['id']==f.n+'Leaf');selected=payload+('[]'if multiple else'')
 if multiple:
  texts={bodies[first]:'var alias=nativeAmount;alias[0].Value.Count=checked(alias[0].Value.Count+31);return calls.Selected.Invoke(nativeAmount); // 같은 배열 입력의 명시 별칭 😀\r\n',bodies[second]:'return checked((int)nativeAmount[0].Value.Count+2); // 명시 배열 입력 소비 😀\r\n',callers[first]:'var values=new '+payload+'[] {new '+payload+' {Value=new '+leaf+' {Count=40}},new '+payload+' {Value=new '+leaf+' {Count=1}}};int result=calls.Connected.Invoke(values);if(values.Length!=2||values[0].Value.Count!=71||values[1].Value.Count!=1)throw new Exception("array input identity/order lost");Console.WriteLine(result);return result; // 호출 경계를 통과한 원래 배열 😀\r\n'}
 else:
  texts={bodies[first]:'nativeAmount.Value.Count=checked(nativeAmount.Value.Count+31);return calls.Selected.Invoke(nativeAmount); // 기존 단일 값 입력 이름 보존 😀\r\n',bodies[second]:'return checked((int)nativeAmount.Value.Count+2);',callers[first]:'var value=new '+payload+' {Value=new '+leaf+' {Count=40}};int result=calls.Connected.Invoke(value);if(value.Value.Count!=40)throw new Exception("single struct value copy lost");Console.WriteLine(result);return result;'}
 for row in r['changes']:
  row['signature']=dict(args=[dict(name='amount',type=selected)],**{'return':'int'});row['mapping']['args']['amount']=None
  for id,plan in row['mapping']['bodies'].items():
   plan['contract']=copy.deepcopy(row['signature']);plan['text']=texts[id];plan['signature']=copy.deepcopy(plan['beforeSignature'])
   if id in bodies.values():plan['signature']['args'][0]['type']=selected
 return r

def mixed(r,catalog=None):
 catalog=catalog or catalogs();r=copy.deepcopy(r);a,b=r['changes'];payload=a['signature']['args'][0]['type'].removesuffix('[]');leaf=next(v['clrType']for v in catalog[first]['nativeTypes']if v['id']==f.n+'Leaf');b['signature']=dict(args=copy.deepcopy(old['args']),**{'return':payload+'[]'});b['mapping']['args']['amount']='amount'
 shared='var values=calls.Selected.Invoke(40);return checked((int)values[0].Value.Count+31);';a['mapping']['bodies'][bodies[first]]['text']=shared;b['mapping']['bodies'][bodies[first]]['text']=shared
 for id,plan in b['mapping']['bodies'].items():
  plan['contract']=copy.deepcopy(b['signature'])
  if id==bodies[second]:plan['signature']=dict(args=[dict(name='nativeAmount',type='int')],**{'return':payload+'[]'});plan['text']='return new '+payload+'[] {new '+payload+' {Value=new '+leaf+' {Count=nativeAmount+2}}};'
 a['mapping']['bodies'][callers[first]]['text']='return calls.Connected.Invoke(new '+payload+'[0]);'
 return r

def unsupported(r,kind,catalog=None):
 catalog=catalog or catalogs();r=copy.deepcopy(r)
 for row in r['changes']:
  fn=row['id'];base=row['signature']['args'][0]['type'].removesuffix('[]')
  if kind=='reference-array':
   choice=next(v['reference']for v in catalog[fn]['nativeTypes']if v['id']==f.n+'Leaf');base=choice['clrType'];row['nativeTypes']={base:copy.deepcopy(choice['proof']),'$function:'+fn:row['nativeTypes']['$function:'+fn]}
  selected=base+('[][]'if kind=='jagged-array'else'[]');row['signature']['args'][0]['type']=selected
  for id,plan in row['mapping']['bodies'].items():
   plan['contract']=copy.deepcopy(row['signature'])
   if id in bodies.values():plan['signature']['args'][0]['type']=selected;plan['text']='return calls.Selected.Invoke(nativeAmount);'if id==bodies[first]else'return 0;'
   else:plan['text']='return calls.Connected.Invoke(System.Array.Empty<'+selected[:-2]+'>());'
 return r

def apply_request(catalog=None):
 catalog=catalog or catalogs();r=request(catalog);return dict(action='applySlots',id=owner,rows=[],basis=catalog[first]['basis'],declaration=dict(id=owner,hash=f.state()['schema']['textHash'],changes=r['changes']))
def verify(checkpoint):
 document=json.loads(checkpoint.read_text());rows={v['id']:v for v in document['changes']};receipt=rows[owner]['slotSaveReceipt'];assert document['version']==2 and document['nativeTypeProfile']=='native-type-source-guards-v1';assert{'$function:'+fn for fn in functions}<=set(receipt['nativeTypeProofs']);assert set(paths)<=set(receipt['sources']);assert all(p in receipt['readGuards']for p in paths.values());group=rows[owner]['atomicEditGroup'];assert set(functions)|set(paths)|{owner,first+'Body',second+'Body',consumer_body}<=set(group)
 for fn in functions:
  signature=f.metadata('inspect',text=rows[fn]['draft'])['signature'];args=signature['Args'];assert signature['return']=='int'and len(args)==1 and args[0]['Name']=='amount'and args[0]['Type'].startswith('Confectory.Information.')and args[0]['Type'].endswith('[]')==multiple;native=f.metadata('inspect',text=rows[fn+'Body']['draft'])['signature'];assert native['return']=='int'and native['Args'][0]['Name']=='nativeAmount'and native['Args'][0]['Type']==args[0]['Type'];base=args[0]['Type'].removesuffix('[]');assert base in receipt['nativeTypeProofs']and(base+'[]')not in receipt['nativeTypeProofs']
 for change in receipt['declaration']['changes']:
  if change.get('type')=='function-edit':
   for id,plan in change.get('mapping',{}).get('bodies',{}).items():assert rows[id]['draft']==plan['text']
 assert group.count(bodies[first])==1 and group.count(first+'Body')==1;unchanged();return group
def verify_live():
 allowed={'FreeInfo.celem'}|set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{'MainBody.celem'};unchanged(allowed);execute(73,'nominal-array-input-selected');f.checked('explicit nominal inputs execute73; array identity/order or single struct value copy, scalar returns, public/native names, Main ABI and unrelated source bytes retained')
