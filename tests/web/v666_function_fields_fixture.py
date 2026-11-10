"""Existing owned native body with an exact user-supplied function handle."""
import json
import v666_information_struct_fixture as x
f=x.f;slot=f.n+'CallbackSlot';symbol=lambda id:__import__('hashlib').sha256(json.dumps(id).encode()).hexdigest()[:24];contract='Confectory.Contracts.E'+symbol(slot)
(f.project/'StructValue.celem').write_text('schema '+x.schema+' {field Invoke single function '+slot+';}')
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element CallbackSlot function "CallbackSlot.celem";registry Confectory.Build.DotNet',1));(f.project/'CallbackSlot.celem').write_bytes(('function '+slot+' (long value) -> long {}\r\n').encode())
x.schema_path='CallbackSlot.celem';x.original='return data; // 원래 함수 값 · 😀\r\n';x.selected='var result=data.Invoke.Invoke(31);if(result!=31)throw new Exception("caller function lost");return data; // 명시 함수 필드 · 😀\r\n';(f.project/x.body_path).write_bytes(x.original.encode())
main='''var a=System.Reflection.Emit.AssemblyBuilder.DefineDynamicAssembly(new System.Reflection.AssemblyName("CallerOwnedFunction"),System.Reflection.Emit.AssemblyBuilderAccess.Run);var m=a.DefineDynamicModule("Owned");var t=m.DefineType("CallerOwnedFunction",System.Reflection.TypeAttributes.Public);t.AddInterfaceImplementation(typeof(CONTRACT.IInvoke));t.DefineDefaultConstructor(System.Reflection.MethodAttributes.Public);var method=t.DefineMethod("Invoke",System.Reflection.MethodAttributes.Public|System.Reflection.MethodAttributes.Virtual,typeof(long),new[]{typeof(long)});var il=method.GetILGenerator();il.Emit(System.Reflection.Emit.OpCodes.Ldarg_1);il.Emit(System.Reflection.Emit.OpCodes.Ret);t.DefineMethodOverride(method,typeof(CONTRACT.IInvoke).GetMethod("Invoke")!);var callback=(CONTRACT.IInvoke)Activator.CreateInstance(t.CreateType()!)!;var result=calls.TypedValue.Invoke(new MTYPE {Invoke=callback});if(!Object.ReferenceEquals(callback,result.Invoke))throw new Exception("function identity lost");long value=result.Invoke.Invoke(31);Console.WriteLine(value);return checked((int)value);'''.replace('CONTRACT',contract).replace('MTYPE',x.type)
(f.project/'Main.csbody').write_text(main)
x.snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts};previous=x.verify
def verify(checkpoint):
 ids,receipt=previous(checkpoint);assert {'StructValue.celem','CallbackSlot.celem'}<=set(receipt['readGuards']);return ids,receipt
x.verify=verify
