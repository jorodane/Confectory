"""Explicit mixed input/return contracts across Main -> selected A -> selected B."""
import copy,hashlib,json
import v666_native_reference_return_fixture as _base
for _key in dir(_base):
 if not _key.startswith('_'):globals()[_key]=getattr(_base,_key)
io_case='return-input'
for fn,names in [(first,[('Create','(string,string[],object[]) -> object')]),(second,[('Set','(object,string,string,string,object) -> void')])]:
 p=f.project/(fn.split('::')[1]+'Body.celem');p.write_text(p.read_text().replace('{','{'+imports(names),1))
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};c.x.original=snapshot
def unchanged(except_names=()):
 for path,raw in snapshot.items():
  if path not in except_names:assert(f.project/path).read_bytes()==raw,path
def request(catalog=None):
 catalog=catalog or catalogs();r=_base.request(catalog);choices={fn:next((v if io_case=='value'else v['reference'])for v in catalog[fn]['nativeTypes']if v['id']==f.n+('Payload'if io_case=='value'else'Leaf'))for fn in functions};q=choices[first]['clrType'];selected=q if io_case=='value'else q+'[]';leaf=next(v['clrType']for v in catalog[first]['nativeTypes']if v['id']==f.n+'Leaf')
 def sig(input_type='int',returns='int'):return dict(args=[dict(name='amount',type=input_type)],**{'return':returns})
 signatures={first:sig(returns=selected),second:sig(selected)}if io_case in ['return-input','value']else{first:sig(selected,selected if io_case=='both'else'int'),second:sig(returns=selected)}
 def pair(initial):return 'object receiver=calls.Create.Invoke('+lit(json.dumps(descriptor,separators=(',',':')))+',new[]{'+lit(field['id'])+'},new object[]{'+initial+'});object peer=calls.Create.Invoke('+lit(json.dumps(descriptor,separators=(',',':')))+',new[]{'+lit(field['id'])+'},new object[]{1L});var values=new '+q+'[]{'+q+'.Bind(receiver,'+lit(json.dumps(contract,separators=(',',':')))+'),'+q+'.Bind(peer,'+lit(json.dumps(contract,separators=(',',':')))+')};'
 def access(name,index=0):return name+'['+str(index)+'].Target,'+name+'['+str(index)+'].Owner,'+field_args
 sentinel='if(nativeAmount is null)return -1;if(nativeAmount.Length==0)return -2;if(!nativeAmount[0].IsBound)return -3;'
 boundaries='if(nativeAmount is -1 or -2 or -3){'+q+'[] boundary=nativeAmount==-1?null!:nativeAmount==-2?System.Array.Empty<'+q+'>():new '+q+'[1];if(calls.Selected.Invoke(boundary!)!=nativeAmount)throw new Exception("mixed boundary input changed");return boundary!;}'
 input_body=sentinel+'var alias=nativeAmount;var target=nativeAmount[0].Target;long value=(long)calls.Read.Invoke('+access('nativeAmount')+');calls.Set.Invoke('+access('nativeAmount')+',checked(value+31));if(!Object.ReferenceEquals(alias,nativeAmount)||!Object.ReferenceEquals(target,nativeAmount[0].Target))throw new Exception("mixed input alias lost");return checked((int)(long)calls.Read.Invoke('+access('nativeAmount')+')+2);'
 consume='var values=calls.Connected.Invoke(40);var reference=values[0];var copy=reference;GC.Collect();GC.WaitForPendingFinalizers();var cell=(System.Runtime.CompilerServices.StrongBox<long>)calls.RefCell.Invoke(reference.Target,reference.Owner,'+field_args+');if(values.Length!=2||cell.Value!=73||!Object.ReferenceEquals(copy.Target,reference.Target)||reference.Owner!='+lit(receiver)+'||Object.ReferenceEquals(reference.Target,values[1].Target)||((System.Runtime.CompilerServices.StrongBox<long>)calls.RefCell.Invoke(values[1].Target,values[1].Owner,'+field_args+')).Value!=1)throw new Exception("mixed returned target/cell/order lost");if(calls.Connected.Invoke(-1)is not null||calls.Connected.Invoke(-2).Length!=0||calls.Connected.Invoke(-3)[0].IsBound)throw new Exception("mixed returned boundary changed");int result=checked((int)cell.Value);Console.WriteLine(result);return result;'
 if io_case=='value':
  shared='var value=new '+q+'{Value=new '+leaf+'{Count=nativeAmount}};int result=calls.Selected.Invoke(value);if(value.Value.Count!=nativeAmount)throw new Exception("mixed value input copy lost");value.Value.Count=result;return value;'
  second_text='nativeAmount.Value.Count=checked(nativeAmount.Value.Count+31);return checked((int)nativeAmount.Value.Count+2);'
  main='var value=calls.Connected.Invoke(40);int result=checked((int)value.Value.Count);Console.WriteLine(result);return result;'
 elif io_case=='return-input':
  shared=boundaries+pair('(long)nativeAmount')+'var alias=values;var target=values[0].Target;int result=calls.Selected.Invoke(values);if(!Object.ReferenceEquals(alias,values)||!Object.ReferenceEquals(target,values[0].Target)||(long)calls.Read.Invoke('+access('values')+')!=nativeAmount+31)throw new Exception("mixed callee/caller identity lost");calls.Set.Invoke('+access('values')+',checked((long)result));return values;'
  second_text=input_body;main=consume
 else:
  second_text='if(nativeAmount==-1)return null!;if(nativeAmount==-2)return System.Array.Empty<'+q+'>();if(nativeAmount==-3)return new '+q+'[1];'+pair('checked((long)nativeAmount+2)')+'return values;'
  boundary_return='return nativeAmount!;'if io_case=='both'else'return code;'
  shared='if(nativeAmount is null||nativeAmount.Length==0||!nativeAmount[0].IsBound){int code=nativeAmount is null?-1:nativeAmount.Length==0?-2:-3;var boundary=calls.Selected.Invoke(code);if(code==-1?boundary is not null:code==-2?boundary is null||boundary.Length!=0:boundary is null||boundary.Length!=1||boundary[0].IsBound)throw new Exception("mixed callee return boundary changed");'+boundary_return+'}var input=nativeAmount;var values=calls.Selected.Invoke(40);var returned=values;var target=values[0].Target;GC.Collect();GC.WaitForPendingFinalizers();if(Object.ReferenceEquals(target,input[0].Target))throw new Exception("independent explicit instances merged");long value=(long)calls.Read.Invoke('+access('values')+');calls.Set.Invoke('+access('values')+',checked(value+31));long result=(long)calls.Read.Invoke('+access('values')+');calls.Set.Invoke('+access('input')+',result);if(!Object.ReferenceEquals(input,nativeAmount)||!Object.ReferenceEquals(returned,values)||!Object.ReferenceEquals(target,values[0].Target))throw new Exception("mixed arguments/return aliases lost");'+('return input;'if io_case=='both'else'return checked((int)result);')
  main=pair('40L')+'var input=values;var target=values[0].Target;'+('var returned=calls.Connected.Invoke(values);if(!Object.ReferenceEquals(returned,values))throw new Exception("simultaneous IO array alias lost");'if io_case=='both'else'int result=calls.Connected.Invoke(values);if(result!=73)throw new Exception("mixed scalar result lost");')+'var cell=(System.Runtime.CompilerServices.StrongBox<long>)calls.RefCell.Invoke(target,'+lit(receiver)+','+field_args+');if(!Object.ReferenceEquals(input,values)||!Object.ReferenceEquals(target,values[0].Target)||cell.Value!=73||((System.Runtime.CompilerServices.StrongBox<long>)calls.RefCell.Invoke(values[1].Target,values[1].Owner,'+field_args+')).Value!=1)throw new Exception("mixed main input cell/order lost");'+('if(calls.Connected.Invoke(null!)is not null||calls.Connected.Invoke(System.Array.Empty<'+q+'>()).Length!=0||calls.Connected.Invoke(new '+q+'[1])[0].IsBound)throw new Exception("simultaneous boundary normalization");int result=checked((int)cell.Value);'if io_case=='both'else'if(calls.Connected.Invoke(null!)!=-1||calls.Connected.Invoke(System.Array.Empty<'+q+'>())!=-2||calls.Connected.Invoke(new '+q+'[1])!=-3)throw new Exception("mixed input boundary changed");')+'Console.WriteLine(result);return result;'
 texts={bodies[first]:shared+' // 명시 혼합 caller·callee 😀\r\n',bodies[second]:second_text+' // 명시 혼합 대상 😀\r\n',callers[first]:main+' // 명시 혼합 Main 😀\r\n'}
 for row in r['changes']:
  fn=row['id'];row['signature']=copy.deepcopy(signatures[fn]);row['mapping']['args']['amount']='amount'if signatures[fn]['args'][0]['type']=='int'else None;row['nativeTypes']={q:copy.deepcopy(choices[fn]['proof']),'$function:'+fn:row['nativeTypes']['$function:'+fn]}
  for id,plan in row['mapping']['bodies'].items():
   plan['contract']=copy.deepcopy(row['signature']);plan['text']=texts[id];plan['signature']=copy.deepcopy(plan['beforeSignature'])
   if id in bodies.values():actual=next(v for v in functions if bodies[v]==id);plan['signature']=dict(args=[dict(name='nativeAmount',type=signatures[actual]['args'][0]['type'])],**{'return':signatures[actual]['return']})
 return r
def unsupported(r,kind,catalog=None):
 r=copy.deepcopy(r)
 for row in r['changes']:
  for arg in row['signature']['args']:
   if arg['type'].endswith('[]'):arg['type']+='[]'
  if row['signature']['return'].endswith('[]'):row['signature']['return']+='[]'
 return r
def apply_request(catalog=None):
 catalog=catalog or catalogs();r=request(catalog);return dict(action='applySlots',id=owner,rows=[],basis=catalog[first]['basis'],declaration=dict(id=owner,hash=f.state()['schema']['textHash'],changes=r['changes']))
def verify(checkpoint):
 document=json.loads(checkpoint.read_text());rows={v['id']:v for v in document['changes']};receipt=rows[owner]['slotSaveReceipt'];assert document['version']==2 and document['nativeTypeProfile']=='native-type-source-guards-v1';assert{'$function:'+fn for fn in functions}<=set(receipt['nativeTypeProofs']);assert set(paths)<=set(receipt['sources']);assert all(p in receipt['readGuards']for p in paths.values());assert set(receipt['nativeBodyDependencies'])==set(functions)and receipt['nativeBodyDependencyReads'];group=rows[owner]['atomicEditGroup'];assert set(functions)|set(paths)|{owner,first+'Body',second+'Body',consumer_body}<=set(group)
 directions={}
 for fn in functions:
  signature=f.metadata('inspect',text=rows[fn]['draft'])['signature'];arg=signature['Args'][0];ret=signature['return'];assert len(signature['Args'])==1 and arg['Name']=='amount';native=f.metadata('inspect',text=rows[fn+'Body']['draft'])['signature'];assert native['return']==ret and native['Args'][0]['Name']=='nativeAmount'and native['Args'][0]['Type']==arg['Type'];directions[fn]=(arg['Type']!='int',ret!='int')
  for type in [arg['Type'],ret]:
   if type=='int':continue
   assert type.startswith('Confectory.Information.'if io_case=='value'else'Confectory.Reference.')and type.endswith('[]')==(io_case!='value');base=type.removesuffix('[]');assert base in receipt['nativeTypeProofs']and base+'[]'not in receipt['nativeTypeProofs']
 assert directions==({first:(False,True),second:(True,False)}if io_case in ['return-input','value']else{first:(True,io_case=='both'),second:(False,True)})
 for change in receipt['declaration']['changes']:
  if change.get('type')=='function-edit':
   for id,plan in change.get('mapping',{}).get('bodies',{}).items():assert rows[id]['draft']==plan['text']
 assert group.count(bodies[first])==1 and group.count(first+'Body')==1;unchanged();return group
def verify_live():
 allowed={'FreeInfo.celem'}|set(paths.values())|{'elements/'+fn.split('::')[1]+'.celem'for fn in functions}|{fn.split('::')[1]+'Body.celem'for fn in functions}|{'MainBody.celem'};unchanged(allowed);execute(73,'mixed-io-selected');f.checked('explicit mixed IO '+io_case+' executes73; independent contracts, actual targets/cells/array identity or value copy, native names and original bytes retained')
