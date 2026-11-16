"""Explicit bound information reference returns along Main -> selected A -> selected B."""
import copy,hashlib,json
import v666_native_reference_input_fixture as _base
import v666_native_return_struct_fixture as _return
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)
multiple=True
p=f.project/(second.split('::')[1]+'Body.celem');p.write_text(p.read_text().replace('{','{'+imports([('Create','(string,string[],object[]) -> object')]),1))
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};c.x.original=snapshot
def unchanged(except_names=()):
 for path,raw in snapshot.items():
  if path not in except_names:assert(f.project/path).read_bytes()==raw,path
def request(catalog=None):
 catalog=catalog or catalogs();r=_return.request(catalog);choice=next(v['reference']for v in catalog[first]['nativeTypes']if v['id']==f.n+'Leaf');q=choice['clrType'];selected=q+('[]'if multiple else'');live='values[0]'if multiple else'values';value=live+'.Target,'+live+'.Owner,'+field_args
 guard=('if(values is null||values.Length==0||!values[0].IsBound)return values!;'if multiple else'if(!values.IsBound)return values;')
 shared='var values=calls.Selected.Invoke(nativeAmount);'+guard+'var alias=values;var target='+live+'.Target;GC.Collect();GC.WaitForPendingFinalizers();long value=(long)calls.Read.Invoke('+value+');calls.Set.Invoke('+value+',checked(value+31));if(!Object.ReferenceEquals(target,'+live+'.Target)'+('||!Object.ReferenceEquals(alias,values)'if multiple else'')+')throw new Exception("returned reference alias lost");return values; // 명시 반환 handle·같은 셀·CLR strong 참조 😀\r\n'
 create='object receiver=calls.Create.Invoke('+lit(json.dumps(descriptor,separators=(',',':')))+',new[]{'+lit(field['id'])+'},new object[]{checked((long)nativeAmount+2)});var reference='+q+'.Bind(receiver,'+lit(json.dumps(contract,separators=(',',':')))+');'
 if multiple:
  create='if(nativeAmount==-1)return null!;if(nativeAmount==-2)return System.Array.Empty<'+q+'>();if(nativeAmount==-3)return new '+q+'[1];'+create+'object peer=calls.Create.Invoke('+lit(json.dumps(descriptor,separators=(',',':')))+',new[]{'+lit(field['id'])+'},new object[]{1L});return new '+q+'[]{reference,'+q+'.Bind(peer,'+lit(json.dumps(contract,separators=(',',':')))+')};'
 else:create='if(nativeAmount==-3)return default;'+create+'return reference;'
 consume='var values=calls.Connected.Invoke(40);var reference='+live+';var copy=reference;GC.Collect();GC.WaitForPendingFinalizers();var cell=(System.Runtime.CompilerServices.StrongBox<long>)calls.RefCell.Invoke(reference.Target,reference.Owner,'+field_args+');if(!reference.IsBound||reference.Owner!='+lit(receiver)+'||!Object.ReferenceEquals(copy.Target,reference.Target)||cell.Value!=73)throw new Exception("returned reference target/cell lost");'
 if multiple:consume+='if(values.Length!=2||!values[1].IsBound||Object.ReferenceEquals(values[1].Target,reference.Target)||((System.Runtime.CompilerServices.StrongBox<long>)calls.RefCell.Invoke(values[1].Target,values[1].Owner,'+field_args+')).Value!=1)throw new Exception("reference array shape/order lost");var empty=calls.Connected.Invoke(-2);var unbound=calls.Connected.Invoke(-3);if(calls.Connected.Invoke(-1)is not null||empty is null||empty.Length!=0||unbound.Length!=1||unbound[0].IsBound)throw new Exception("null/empty/default reference return was normalized");'
 else:consume+='if(calls.Connected.Invoke(-3).IsBound)throw new Exception("default reference return was normalized");'
 texts={bodies[first]:shared,bodies[second]:create+' // 직접 생성·Bind한 참조 반환 😀\r\n',callers[first]:consume+'int result=checked((int)cell.Value);Console.WriteLine(result);return result; // 명시 반환 소비자 😀\r\n'}
 for row in r['changes']:
  fn=row['id'];choice=next(v['reference']for v in catalog[fn]['nativeTypes']if v['id']==f.n+'Leaf');assert catalog[fn]['functionDependencies'];row['mapping']['dependencies']=copy.deepcopy(catalog[fn]['functionDependencies']);row['signature']=dict(args=copy.deepcopy(old['args']),**{'return':selected});row['nativeTypes']={q:copy.deepcopy(choice['proof']),'$function:'+fn:row['nativeTypes']['$function:'+fn]}
  for id,plan in row['mapping']['bodies'].items():
   plan['contract']=copy.deepcopy(row['signature']);plan['text']=texts[id]
   if id in bodies.values():plan['signature']['return']=selected
 return r
def mixed(r,catalog=None):
 r=copy.deepcopy(r);a,b=r['changes'];q=a['signature']['return'].removesuffix('[]');b['signature']=dict(args=[dict(name='amount',type=q+'[]')],**{'return':'int'});b['mapping']['args']['amount']=None
 shared='int result=calls.Selected.Invoke(System.Array.Empty<'+q+'>());return System.Array.Empty<'+q+'>();'
 for row in r['changes']:
  for id,plan in row['mapping']['bodies'].items():
   plan['contract']=copy.deepcopy(row['signature'])
   if id==bodies[first]:plan['text']=shared
   elif id==bodies[second]:plan['signature']=dict(args=[dict(name='nativeAmount',type=q+'[]')],**{'return':'int'});plan['text']='return nativeAmount.Length;'
 return r
def unsupported(r,kind,catalog=None):
 r=copy.deepcopy(r)
 for row in r['changes']:
  selected=row['signature']['return'].removesuffix('[]')+'[][]';row['signature']['return']=selected
  for id,plan in row['mapping']['bodies'].items():
   plan['contract']=copy.deepcopy(row['signature'])
   if id in bodies.values():plan['signature']['return']=selected;plan['text']='return calls.Selected.Invoke(nativeAmount);'if id==bodies[first]else'return null!;'
   else:plan['text']='return calls.Connected.Invoke(40)is null?73:0;'
 return r
def apply_request(catalog=None):
 catalog=catalog or catalogs();r=request(catalog);return dict(action='applySlots',id=owner,rows=[],basis=catalog[first]['basis'],declaration=dict(id=owner,hash=f.state()['schema']['textHash'],changes=r['changes']))
def verify(checkpoint):
 document=json.loads(checkpoint.read_text());rows={v['id']:v for v in document['changes']};receipt=rows[owner]['slotSaveReceipt'];assert document['version']==2 and document['nativeTypeProfile']=='native-type-source-guards-v1';assert{'$function:'+fn for fn in functions}<=set(receipt['nativeTypeProofs']);assert set(paths)<=set(receipt['sources']);assert all(p in receipt['readGuards']for p in paths.values());assert set(receipt['nativeBodyDependencies'])==set(functions)and receipt['nativeBodyDependencyReads'];group=rows[owner]['atomicEditGroup'];assert set(functions)|set(paths)|{owner,first+'Body',second+'Body',consumer_body}<=set(group)
 for fn in functions:
  signature=f.metadata('inspect',text=rows[fn]['draft'])['signature'];args=signature['Args'];selected=signature['return'];assert selected.startswith('Confectory.Reference.')and selected.endswith('[]')==multiple and not selected.endswith('[][]')and len(args)==1 and args[0]['Name']=='amount'and args[0]['Type']=='int';native=f.metadata('inspect',text=rows[fn+'Body']['draft'])['signature'];assert native['return']==selected and native['Args'][0]['Name']=='nativeAmount'and native['Args'][0]['Type']=='int';base=selected.removesuffix('[]');assert base in receipt['nativeTypeProofs']and(base+'[]')not in receipt['nativeTypeProofs']
 for change in receipt['declaration']['changes']:
  if change.get('type')=='function-edit':
   for id,plan in change.get('mapping',{}).get('bodies',{}).items():assert rows[id]['draft']==plan['text']
 assert group.count(bodies[first])==1 and group.count(first+'Body')==1;unchanged();return group
def verify_live():
 allowed={'FreeInfo.celem'}|set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{'MainBody.celem'};unchanged(allowed);execute(73,'reference-return-selected');f.checked('explicit Bind and reference returns execute73 through selected imports; returned actual target/cell aliases, array identity/order, null/empty/default, scalar inputs/native names and original bytes retained')
