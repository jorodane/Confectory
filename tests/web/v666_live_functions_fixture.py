"""Existing owned body explicitly connects a supplied function to live storage."""
import json
import v666_function_fields_fixture as fields
x,f=fields.x,fields.f
owner=f.n+'LiveReceiver';model='Confectory.ObjectModel'
(f.project/'LiveReceiver.celem').write_text('object '+owner+' {use schema '+x.schema+';}')
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element LiveReceiver object "LiveReceiver.celem";registry '+model+' '+json.dumps(str(f.repo/'packs/object-model/pack.cpack'))+';dependency '+model+' version "0.1.0";registry Confectory.Build.DotNet',1))
imports=''.join('import '+model+'::'+name+' as '+name+' '+signature+';'for name,signature in [('Create','(string,string[],object[]) -> object'),('Read','(object,string,string,string) -> object'),('Set','(object,string,string,string,object) -> void')])
p=f.project/x.implementation_path;p.write_text(p.read_text().replace('{','{'+imports,1))
descriptor=f.metadata('blueprintPropertyCatalog',project=str(f.manifest),sourceId=x.fn+'Body',owner=owner)['descriptor'];field=descriptor['fields'][0];assert field['supported']and field['clrType']=='object'
lit=lambda v:json.dumps(v,ensure_ascii=False)
selected='object actual=calls.Create.Invoke('+lit(json.dumps(descriptor,separators=(',',':')))+',new[]{'+lit(field['id'])+'},new object[]{data.Invoke});calls.Set.Invoke(actual,'+lit(owner)+','+lit(field['id'])+','+lit(field['hash'])+',data.Invoke);var callback=('+fields.contract+'.IInvoke)calls.Read.Invoke(actual,'+lit(owner)+','+lit(field['id'])+','+lit(field['hash'])+');if(!Object.ReferenceEquals(callback,data.Invoke)||callback.Invoke(31)!=31)throw new Exception("live callback lost");return data; // 명시 live 함수 속성 · 😀\r\n'
x.selected=selected
# Contract validation observes parameter metadata but never invokes the provider.
p=f.project/'Main.csbody';p.write_text(p.read_text().replace('var il=method.GetILGenerator();','method.DefineParameter(1,System.Reflection.ParameterAttributes.None,"value");var il=method.GetILGenerator();'))
x.snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}

# Registered accessor imports keep the existing explicit dependency receipt.
def change():
 info=f.state()['schema'];basis=f.invoke('blueprint',dict(action='readOwnerEdits',id=x.owner,hash=info['textHash'],includeFunctionInputs=x.fn,includeFunctionBodies=True))['result']['result'];body=basis['functionBodies'][x.body_id];assert basis.get('functionDependencies')
 row=dict(type='function-edit',id=x.fn,hash=__import__('hashlib').sha256(x.snapshot[x.function_path]).hexdigest(),name='구조체 계산',description='정보 구조체 원문',signature=x.signature,mapping=dict(before=x.signature,args={'data':'data'},dependencies=basis['functionDependencies'],bodies={x.body_id:{key:body[key]for key in ['hash','path']}|dict(beforeSignature=x.signature,signature=x.signature,contract=x.signature,text=x.selected)}))
 return dict(action='applySlots',id=x.owner,rows=[],basis=basis['basis'],declaration=dict(id=x.owner,hash=info['textHash'],changes=[row]))
x.change=change
