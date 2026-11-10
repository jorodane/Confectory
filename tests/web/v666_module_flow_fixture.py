"""The existing owned-body transaction consumes a module execution result."""
import json
import v666_module_nominal_fixture as m
x,f=m.x,m.f
contract='Confectory.Contracts.'+m.symbol(m.slot);branch='Branch_'+m.symbol('success')[1:]
metadata=dict(schema=1,branches=[dict(id='success',name='성공',value=12),dict(id='failure',name='실패',value=43)])
path=f.project/'MethodSlot.celem';path.write_text(path.read_text().replace('{}','{value blueprintExecutionBranches='+json.dumps(json.dumps(metadata,ensure_ascii=False))+';}'))
main=(f.project/'Main.csbody').read_text();old='var data=calls.TypedValue.Invoke'
extra='''var execution=typeof(MTYPE).GetMethod("METHODExecution")!;var ex=t.DefineMethod(execution.Name,System.Reflection.MethodAttributes.Public|System.Reflection.MethodAttributes.Virtual,execution.ReturnType,new[]{typeof(VTYPE),typeof(ETYPE).MakeByRefType(),typeof(VTYPE).MakeByRefType()});ex.DefineParameter(2,System.Reflection.ParameterAttributes.Out,"choice");ex.DefineParameter(3,System.Reflection.ParameterAttributes.Out,"__fg_native_return");var ei=ex.GetILGenerator();ei.Emit(System.Reflection.Emit.OpCodes.Ldarg_2);ei.Emit(System.Reflection.Emit.OpCodes.Ldc_I4,31);ei.Emit(System.Reflection.Emit.OpCodes.Stind_I4);ei.Emit(System.Reflection.Emit.OpCodes.Ldarg_3);ei.Emit(System.Reflection.Emit.OpCodes.Ldarg_1);ei.Emit(System.Reflection.Emit.OpCodes.Stobj,typeof(VTYPE));ei.Emit(System.Reflection.Emit.OpCodes.Ldc_I4,12);ei.Emit(System.Reflection.Emit.OpCodes.Ret);t.DefineMethodOverride(ex,execution);'''
for key,value in [('MTYPE',m.type),('METHOD',m.method),('VTYPE',m.value_type),('ETYPE',m.enum_type)]:extra=extra.replace(key,value)
assert old in main;main=main.replace(old,extra+old);(f.project/'Main.csbody').write_text(main)
x.selected='var branch=data.'+m.method+'Execution(new '+m.value_type+' {Value=new '+m.native(m.leaf)+' {Count=31}},out var choice,out var captured);if(branch!='+contract+'.ExecutionResult.'+branch+'||captured.Value.Count!=31)throw new Exception("module data/branch lost");return data; // explicit original public contract · 😀\r\n'
x.snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
