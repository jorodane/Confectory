"""Explicit bound information reference inputs along Main -> selected A -> selected B."""
import copy,hashlib,json
import v666_native_array_input_fixture as _base
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)
multiple=True
model='Confectory.ObjectModel';receiver=f.n+'LiveReceiver';lit=lambda v:json.dumps(v,ensure_ascii=False)
(f.project/'LiveReceiver.celem').write_text('object '+receiver+' {use schema '+f.n+'Leaf;use schema External.Fields::Leaf;}')
text=f.manifest.read_text();f.manifest.write_text(text.replace('registry Confectory.Build.DotNet','element LiveReceiver object "LiveReceiver.celem";registry '+model+' '+lit(str(f.repo/'packs/object-model/pack.cpack'))+';dependency '+model+' version "0.1.0";registry Confectory.Build.DotNet',1))
def imports(names):return ''.join('import '+model+'::'+name+' as '+name+' '+signature+';'for name,signature in names)
for fn,names in [(first,[('Read','(object,string,string,string) -> object'),('Set','(object,string,string,string,object) -> void')]),(second,[('Read','(object,string,string,string) -> object')]),(f.n+'Main',[('Create','(string,string[],object[]) -> object'),('RefCell','(object,string,string,string) -> object')])]:
 p=f.project/(fn.split('::')[1]+'Body.celem');p.write_text(p.read_text().replace('{','{'+imports(names),1))
contract=f.metadata('informationReference',project=str(f.manifest),id=f.n+'Leaf')['descriptor'];descriptor=f.metadata('blueprintPropertyCatalog',project=str(f.manifest),sourceId=first+'Body',owner=receiver)['descriptor'];field=next(v for v in descriptor['fields']if v['name']=='Count');field_args=lit(field['id'])+','+lit(field['hash'])
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};c.x.original=snapshot
def unchanged(except_names=()):
 for path,raw in snapshot.items():
  if path not in except_names:assert(f.project/path).read_bytes()==raw,path
def request(catalog=None):
 catalog=catalog or catalogs();r=_base.request(catalog);choice=next(v['reference']for v in catalog[first]['nativeTypes']if v['id']==f.n+'Leaf');q=choice['clrType'];selected=q+('[]'if multiple else'');live='nativeAmount[0]'if multiple else'nativeAmount';guard='if(nativeAmount is null)return -1;if(nativeAmount.Length==0)return -2;'if multiple else'';unbound='if(!'+live+'.IsBound)return -3;';value=live+'.Target,'+live+'.Owner,'+field_args
 texts={bodies[first]:(('if(nativeAmount is null||nativeAmount.Length==0||!nativeAmount[0].IsBound)'if multiple else'if(!nativeAmount.IsBound)')+'return calls.Selected.Invoke(nativeAmount!);var alias=nativeAmount;var handle='+live+'.Target;long value=(long)calls.Read.Invoke('+value+');calls.Set.Invoke('+value+',checked(value+31));int result=calls.Selected.Invoke(nativeAmount);if(!Object.ReferenceEquals(handle,'+live+'.Target)'+('||!Object.ReferenceEquals(alias,nativeAmount)'if multiple else'')+')throw new Exception("live reference alias lost");return result; // 명시 참조 별칭·checked 접근 😀\r\n'),bodies[second]:guard+unbound+'return checked((int)(long)calls.Read.Invoke('+value+')+2); // 같은 실제 객체의 참조 입력 소비 😀\r\n'}
 create='object receiver=calls.Create.Invoke('+lit(json.dumps(descriptor,separators=(',',':')))+',new[]{'+lit(field['id'])+'},new object[]{40L});var cell=(System.Runtime.CompilerServices.StrongBox<long>)calls.RefCell.Invoke(receiver,'+lit(receiver)+','+field_args+');var reference='+q+'.Bind(receiver,'+lit(json.dumps(contract,separators=(',',':')))+');'
 if multiple:
  create+='object peer=calls.Create.Invoke('+lit(json.dumps(descriptor,separators=(',',':')))+',new[]{'+lit(field['id'])+'},new object[]{1L});var peerCell=(System.Runtime.CompilerServices.StrongBox<long>)calls.RefCell.Invoke(peer,'+lit(receiver)+','+field_args+');var values=new '+q+'[]{reference,'+q+'.Bind(peer,'+lit(json.dumps(contract,separators=(',',':')))+')};int result=calls.Connected.Invoke(values);if(values.Length!=2||cell.Value!=71||peerCell.Value!=1||!Object.ReferenceEquals(values[0].Target,receiver)||!Object.ReferenceEquals(values[1].Target,peer)||values[0].Owner!='+lit(receiver)+')throw new Exception("reference array identity/order lost");if(calls.Connected.Invoke(null!)!=-1||calls.Connected.Invoke(System.Array.Empty<'+q+'>())!=-2||calls.Connected.Invoke(new '+q+'[1])!=-3)throw new Exception("reference default/null was normalized");'
 else:create+='int result=calls.Connected.Invoke(reference);if(cell.Value!=71||!Object.ReferenceEquals(reference.Target,receiver)||reference.Owner!='+lit(receiver)+')throw new Exception("single reference identity lost");if(calls.Connected.Invoke(default)!=-3)throw new Exception("unbound reference was normalized");'
 texts[callers[first]]=create+'Console.WriteLine(result);return result; // 실제 인스턴스를 직접 Bind한 원문 😀\r\n'
 for row in r['changes']:
  fn=row['id'];assert catalog[fn]['functionDependencies'];row['mapping']['dependencies']=copy.deepcopy(catalog[fn]['functionDependencies']);choice=next(v['reference']for v in catalog[fn]['nativeTypes']if v['id']==f.n+'Leaf');row['signature']=dict(args=[dict(name='amount',type=selected)],**{'return':'int'});row['nativeTypes']={q:copy.deepcopy(choice['proof']),'$function:'+fn:row['nativeTypes']['$function:'+fn]}
  for id,plan in row['mapping']['bodies'].items():
   plan['contract']=copy.deepcopy(row['signature']);plan['text']=texts[id]
   if id in bodies.values():plan['signature']['args'][0]['type']=selected
 return r
def mixed(r,catalog=None):
 return _base.mixed(r,catalog)
def unsupported(r,kind,catalog=None):
 if kind!='reference-return':return _base.unsupported(r,kind,catalog)
 r=copy.deepcopy(r)
 for row in r['changes']:
  q=row['signature']['args'][0]['type'].removesuffix('[]');row['signature']=dict(args=copy.deepcopy(old['args']),**{'return':q+'[]'});row['mapping']['args']['amount']='amount'
  for id,plan in row['mapping']['bodies'].items():
   plan['contract']=copy.deepcopy(row['signature']);plan['signature']=copy.deepcopy(plan['beforeSignature'])
   if id in bodies.values():plan['signature']['return']=q+'[]';plan['text']='return calls.Selected.Invoke(nativeAmount);'if id==bodies[first]else'return null;'
   else:plan['text']='return calls.Connected.Invoke(40)is null?73:0;'
 return r
def apply_request(catalog=None):
 catalog=catalog or catalogs();r=request(catalog);return dict(action='applySlots',id=owner,rows=[],basis=catalog[first]['basis'],declaration=dict(id=owner,hash=f.state()['schema']['textHash'],changes=r['changes']))
def verify(checkpoint):
 document=json.loads(checkpoint.read_text());rows={v['id']:v for v in document['changes']};receipt=rows[owner]['slotSaveReceipt'];assert document['version']==2 and document['nativeTypeProfile']=='native-type-source-guards-v1';assert{'$function:'+fn for fn in functions}<=set(receipt['nativeTypeProofs']);assert set(paths)<=set(receipt['sources']);assert all(p in receipt['readGuards']for p in paths.values());assert set(receipt['nativeBodyDependencies'])==set(functions)and receipt['nativeBodyDependencyReads'];group=rows[owner]['atomicEditGroup'];assert set(functions)|set(paths)|{owner,first+'Body',second+'Body',consumer_body}<=set(group)
 for fn in functions:
  signature=f.metadata('inspect',text=rows[fn]['draft'])['signature'];args=signature['Args'];assert signature['return']=='int'and len(args)==1 and args[0]['Name']=='amount'and args[0]['Type'].startswith('Confectory.Reference.')and args[0]['Type'].endswith('[]')==multiple;native=f.metadata('inspect',text=rows[fn+'Body']['draft'])['signature'];assert native['return']=='int'and native['Args'][0]['Name']=='nativeAmount'and native['Args'][0]['Type']==args[0]['Type'];base=args[0]['Type'].removesuffix('[]');assert base in receipt['nativeTypeProofs']and(base+'[]')not in receipt['nativeTypeProofs']
 for change in receipt['declaration']['changes']:
  if change.get('type')=='function-edit':
   for id,plan in change.get('mapping',{}).get('bodies',{}).items():assert rows[id]['draft']==plan['text']
 assert group.count(bodies[first])==1 and group.count(first+'Body')==1;unchanged();return group
def verify_live():
 allowed={'FreeInfo.celem'}|set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{'MainBody.celem'};unchanged(allowed);execute(73,'reference-input-selected');f.checked('explicit Bind and reference input chain execute73; actual handle/cell alias, array identity/order, null/empty/default carriers, native aliases and original bytes retained')
