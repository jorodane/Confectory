"""Same-contract native enum/interface body Save and transitive source CAS."""
import hashlib,json,subprocess,sys
import v666_information_struct_fixture as x
f=x.f;kind=sys.argv[3]if len(sys.argv)>3 else'enum';assert kind in ['enum','module']
root=f.project/x.schema_path;type=x.type;fn=x.fn
if kind=='enum':
 members=[dict(id='ready-id',name='준비'),dict(id='done-id',name='완료')]
 root.write_text('enum '+x.schema+' {value editorEnumProfile="nominal-members-native-v2";value editorEnumValues='+json.dumps(json.dumps(members,ensure_ascii=False))+';value editorEnumNumbers="{\\"ready-id\\":12,\\"done-id\\":31}";}')
 f.manifest.write_text(f.manifest.read_text().replace('element StructValue schema','element StructValue enum'))
 original='return data; // 원래 종류 · 😀\r\n';selected='return '+type+'Ids.FromId("done-id"); // 명시 종류 반환 · 😀\r\n'
 main='int value=(int)calls.TypedValue.Invoke('+type+'Ids.FromId("ready-id"));Console.WriteLine(value);return value;'
 peer=lambda raw:raw.replace(b'12,',b'17,')
else:
 # Keep the selected module declaration unchanged: only its included parent
 # changes between observation/Save and Review/Confirm.
 slot=f.n+'TypedSlot';parent=f.n+'TypedParent';method='Call_'+('E'+hashlib.sha256(json.dumps(slot).encode()).hexdigest()[:24])
 root.write_text('module '+x.schema+' extends '+parent+' {}')
 f.manifest.write_text(f.manifest.read_text().replace('element StructValue schema','element StructValue module').replace('registry Confectory.Build.DotNet','element TypedParent module "TypedParent.celem";element TypedSlot function "TypedSlot.celem";registry Confectory.Build.DotNet',1))
 (f.project/'TypedSlot.celem').write_text('function '+slot+' (int input) -> int {}')
 x.schema_path='TypedParent.celem';root=f.project/x.schema_path;root.write_text('module '+parent+' {require '+slot+' (int) -> int;}')
 original='return data; // 원래 모듈 · 😀\r\n';selected='var same=data;return same; // 명시 interface 반환 · 😀\r\n'
 main='''var a=System.Reflection.Emit.AssemblyBuilder.DefineDynamicAssembly(new System.Reflection.AssemblyName("Owned"),System.Reflection.Emit.AssemblyBuilderAccess.Run);var m=a.DefineDynamicModule("Owned");var t=m.DefineType("OwnedValue",System.Reflection.TypeAttributes.Public);t.AddInterfaceImplementation(typeof(TYPE));t.DefineDefaultConstructor(System.Reflection.MethodAttributes.Public);var method=t.DefineMethod("METHOD",System.Reflection.MethodAttributes.Public|System.Reflection.MethodAttributes.Virtual,typeof(int),new[]{typeof(int)});var il=method.GetILGenerator();il.Emit(System.Reflection.Emit.OpCodes.Ldarg_1);il.Emit(System.Reflection.Emit.OpCodes.Ret);t.DefineMethodOverride(method,typeof(TYPE).GetMethod("METHOD")!);var value=calls.TypedValue.Invoke((TYPE)Activator.CreateInstance(t.CreateType()!)!).METHOD(31);Console.WriteLine(value);return value;'''.replace('TYPE',type).replace('METHOD',method)
 peer=lambda raw:raw.replace(b'require ',b'description "peer";require ',1)
(f.project/x.body_path).write_bytes(original.encode());(f.project/'Main.csbody').write_text(main);x.selected=selected
x.snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
try:
 f.start(0);f.invoke('select',dict(id=x.owner));f.invoke('saveDraft',{});f.invoke('schema',dict(id=x.owner));checkpoint=next(f.project.glob('.confectory/edit-workspaces/*/draft.json'));request=x.change();before=checkpoint.read_bytes();raw=root.read_bytes();changed=peer(raw);assert changed!=raw;root.write_bytes(changed);f.invoke('blueprint',request,False);assert checkpoint.read_bytes()==before and root.read_bytes()==changed;x.unchanged({x.schema_path});root.write_bytes(raw);f.checked(kind+' source-only change after observation rejects Save, preserving original body, consumer contracts and checkpoint')
 f.stop();f.start(1);f.invoke('select',dict(id=x.owner));f.invoke('schema',dict(id=x.owner));reply=f.invoke('blueprint',x.change())['result']['result'];assert reply['atomic']and reply['checkpointSaved'];ids,receipt=x.verify(checkpoint);x.unchanged();f.checked(kind+' same-contract body validates and saves with its exact nominal/transitive read guards')
 f.stop();f.start(2);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==(ids,receipt);f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready',review;before=checkpoint.read_bytes();root.write_bytes(changed);outcome=f.invoke('confirmGroup',dict(ids=ids,token=review['token']))['result']['result'];assert outcome['sourceConfirmed']is False,outcome;assert root.read_bytes()==changed and checkpoint.read_bytes()==before;x.unchanged({x.schema_path});f.checked(kind+' dependency change after Review rejects final Confirm with exact pending body and peer preserved')
 root.write_bytes(raw);f.stop();f.start(3);f.invoke('select',dict(id=x.owner));assert x.verify(checkpoint)==(ids,receipt);f.invoke('reviewGroup',dict(ids=ids,target='portable'));review=f.state()['review'];assert review['status']=='ready';f.invoke('confirmGroup',dict(ids=ids,token=review['token']));assert(f.project/x.body_path).read_bytes()==selected.encode();x.unchanged({x.body_path,x.function_path});x.execute();f.checked(kind+' exact dependency restoration, cold retry and fresh Review/Confirm publish only the authored body and execute31')
finally:(f.case/'checks.json').write_text(json.dumps(f.checks,ensure_ascii=False,indent=2));f.stop()
