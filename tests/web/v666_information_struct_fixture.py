"""A real directly owned C# information function, with an explicit struct value."""
import copy,hashlib,json,subprocess
import v536_information_function_order_api as a
f,d,owner,fn=a.f,a.d,a.owner,a.functions[0]
schema=f.n+'StructValue';schema_path='StructValue.celem'
(f.project/schema_path).write_bytes(('schema '+schema+' {field HP single general long;}\r\n').encode())
f.manifest.write_text(f.manifest.read_text().replace('registry Confectory.Build.DotNet','element StructValue schema "'+schema_path+'";registry Confectory.Build.DotNet',1))
descriptor=f.metadata('informationStruct',project=str(f.manifest),id=schema);type=descriptor['clrType'];signature={'args':[{'name':'data','type':type}],'return':type}
function_path='elements/'+fn.split('::')[1]+'.celem';implementation_path=fn.split('::')[1]+'Body.celem';body_path=fn.split('::')[1]+'.csbody';body_id=fn+'Body/body:common'
(f.project/function_path).write_text('function '+fn+' ('+type+' data) -> '+type+' {description "정보 구조체 원문";value editorName="구조체 계산";provide '+fn+' with '+fn+'Body;}')
(f.project/implementation_path).write_text('implementation '+fn+'Body for '+fn+' ('+type+' data) -> '+type+' {body common "'+body_path+'";}')
original='return data; // 원래 정보 값 · 😀\r\n';selected='data.HP=checked(data.HP+1);return data; // 직접 편집한 정보 값 · 😀\r\n';(f.project/body_path).write_bytes(original.encode())
(f.project/'MainBody.celem').write_text('implementation '+f.n+'MainBody for '+f.n+'Main () -> int {import '+fn+' as TypedValue ('+type+') -> '+type+';body common "Main.csbody";}')
(f.project/'Main.csbody').write_text('long value=calls.TypedValue.Invoke(new '+type+' {HP=30}).HP;global::System.Console.WriteLine(value);return checked((int)value);')
snapshot={str(p.relative_to(f.project)):p.read_bytes()for p in f.project.rglob('*')if p.is_file()and'.confectory'not in p.relative_to(f.project).parts}
def unchanged(except_names=()):assert all((f.project/path).read_bytes()==raw for path,raw in snapshot.items()if path not in except_names)
def change():
 info=f.state()['schema'];basis=f.invoke('blueprint',dict(action='readOwnerEdits',id=owner,hash=info['textHash'],includeFunctionInputs=fn,includeFunctionBodies=True))['result']['result'];body=basis['functionBodies'][body_id]
 row=dict(type='function-edit',id=fn,hash=hashlib.sha256(snapshot[function_path]).hexdigest(),name='구조체 계산',description='정보 구조체 원문',signature=signature,mapping=dict(before=signature,args={'data':'data'},bodies={body_id:{key:body[key]for key in ['hash','path']}|dict(beforeSignature=signature,signature=signature,contract=signature,text=selected)}))
 return dict(action='applySlots',id=owner,rows=[],basis=basis['basis'],declaration=dict(id=owner,hash=info['textHash'],changes=[row]))
def verify(checkpoint):
 rows={row['id']:row for row in json.loads(checkpoint.read_text())['changes']};assert rows[body_id]['draft']==selected;assert f.metadata('inspect',text=rows[fn]['draft'])['signature']['return']==type;receipt=rows[owner]['slotSaveReceipt'];assert schema_path in receipt['readGuards']and body_path in receipt['readGuards'];return rows[owner]['atomicEditGroup'],copy.deepcopy(receipt)
def execute():
 p=subprocess.run([f.env['CONFECTORY_DOTNET'],str(f.repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll'),'build',str(f.manifest),'portable'],env=f.env,text=True,capture_output=True);(f.case/'typed-build.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout[-2000:]+p.stderr[-2000:];report=json.loads(p.stdout);run=subprocess.run(report['run'],env=f.env,text=True,capture_output=True);(f.case/'typed-run.json').write_text(json.dumps(dict(exit=run.returncode,stdout=run.stdout,stderr=run.stderr)));assert(run.returncode,run.stdout.strip())==(31,'31'),(run.returncode,run.stdout,run.stderr)
