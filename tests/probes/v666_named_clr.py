"""Actual enums, inline enum fields and module interfaces in native contracts."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile
r=Path(sys.argv[1]).resolve();mode=sys.argv[2]if len(sys.argv)>2 else'native';case=Path(tempfile.mkdtemp(prefix='confectory-named-clr-'));p=case/'owned project';p.mkdir();checks=[]
dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet');cli=r/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll';author=r/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll';n='Owned.Named::'
symbol=lambda s:'E'+hashlib.sha256(json.dumps(s,separators=(',',':')).encode()).hexdigest()[:24];typename=lambda id:'Confectory.Information.'+symbol(id.split('::')[0])+'.'+symbol(id);etype=typename(n+'Mood');stype=typename(n+'Payload');mtype=typename(n+'Rules');method='Call_'+symbol(n+'Slot');items={}
members=[dict(id='ready-id',name='준비'),dict(id='done-id',name='완료')];numbers={'ready-id':12,'done-id':43,'retired-id':9}
def enum_source(rows=members,table=numbers,profile='nominal-members-native-v2'):
 return'enum '+n+'Mood {value editorEnumProfile='+json.dumps(profile)+';value editorEnumValues='+json.dumps(json.dumps(rows,ensure_ascii=False,separators=(',',':')),ensure_ascii=False)+';'+('value editorEnumNumbers='+json.dumps(json.dumps(table,separators=(',',':')))+';'if profile!='nominal-members-v1'else'')+'}'
def write(name,kind,text):items[name]=kind;(p/(name+'.celem')).write_bytes((text+'\r\n').encode())
write('Mood','enum',enum_source());write('Payload','schema','schema '+n+'Payload {field Choice single enum '+n+'Mood;field Count single general long;}');write('ParentRules','module','module '+n+'ParentRules {require '+n+'Slot (int) -> int;default '+n+'Slot with '+n+'SlotBody;}');write('Rules','module','module '+n+'Rules extends '+n+'ParentRules {}')
main='''var ready=ETYPEIds.FromId("ready-id");
if(!typeof(ETYPE).IsEnum||Enum.GetUnderlyingType(typeof(ETYPE))!=typeof(int)||(int)ready!=12||(int)default(ETYPE)!=0||ETYPEIds.ToId(default)!="")throw new Exception("enum identity/default changed");
if((int)calls.Echo.Invoke(ready)!=43||ETYPEIds.ToId(calls.Mix.Invoke(new STYPE {Choice=ready,Count=9223372036854775806L}).Choice)!="done-id")throw new Exception("enum native/struct contract changed");
try{ETYPEIds.FromId("retired-id");throw new Exception("retired ID accepted");}catch(ArgumentException){}
try{ETYPEIds.ToId((ETYPE)9);throw new Exception("retired number accepted");}catch(ArgumentOutOfRangeException){}
if(!typeof(MTYPE).IsInterface||typeof(MTYPE).GetMethod("METHOD")!.ReturnType!=typeof(int))throw new Exception("module interface missing");
var assembly=System.Reflection.Emit.AssemblyBuilder.DefineDynamicAssembly(new System.Reflection.AssemblyName("OwnedModule"),System.Reflection.Emit.AssemblyBuilderAccess.Run);
var module=assembly.DefineDynamicModule("Owned");var type=module.DefineType("OwnedModuleValue",System.Reflection.TypeAttributes.Public|System.Reflection.TypeAttributes.Class);type.AddInterfaceImplementation(typeof(MTYPE));type.DefineDefaultConstructor(System.Reflection.MethodAttributes.Public);
var method=type.DefineMethod("METHOD",System.Reflection.MethodAttributes.Public|System.Reflection.MethodAttributes.Virtual,typeof(int),new[]{typeof(int)});var il=method.GetILGenerator();il.Emit(System.Reflection.Emit.OpCodes.Ldarg_1);il.Emit(System.Reflection.Emit.OpCodes.Ldc_I4_2);il.Emit(System.Reflection.Emit.OpCodes.Add);il.Emit(System.Reflection.Emit.OpCodes.Ret);type.DefineMethodOverride(method,typeof(MTYPE).GetMethod("METHOD")!);
var value=(MTYPE)Activator.CreateInstance(type.CreateType()!)!;if(calls.Use.Invoke(value)!=37)throw new Exception("actual module interface dispatch failed");
Console.WriteLine(37);return 37; // 명시 사용자 코드 · 😀
'''.replace('ETYPE',etype).replace('STYPE',stype).replace('MTYPE',mtype).replace('METHOD',method).replace('\n','\r\n')
for name,args,result,body in [('Main','','int',main),('Echo',etype+' input',etype,'return '+etype+'Ids.FromId("done-id");\r\n'),('Mix',stype+' input',stype,'if(input.Count!=9223372036854775806L)throw new Exception("exact64 lost");input.Choice='+etype+'Ids.FromId("done-id");return input;\r\n'),('Use',mtype+' input','int','return input.'+method+'(35);\r\n'),('Slot','int input','int','throw new Exception("type generation selected a default provider");\r\n')]:
 write(name,'function','function '+n+name+' ('+args+') -> '+result+' {provide '+n+name+' with '+n+name+'Body;}')
 imports='import '+n+'Echo as Echo ('+etype+') -> '+etype+';import '+n+'Mix as Mix ('+stype+') -> '+stype+';import '+n+'Use as Use ('+mtype+') -> int;'if name=='Main'else''
 write(name+'Body','implementation','implementation '+n+name+'Body for '+n+name+' ('+args+') -> '+result+' {'+imports+'body common "'+name+'.csbody";}');(p/(name+'.csbody')).write_bytes(body.encode())
manifest=p/'project.cproj';manifest.write_text('project Owned.Named version "1" {standalone true;entry '+n+'Main;'+''.join('element '+key+' '+kind+' "'+key+'.celem";'for key,kind in items.items())+'registry Confectory.Build.DotNet "'+str(r/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}')
snapshot={x.name:x.read_bytes()for x in p.iterdir()if x.is_file()}
def unchanged(except_names=()):assert all((p/name).read_bytes()==raw for name,raw in snapshot.items()if name not in except_names)
def check(text):checks.append(text);print('PASS '+text,flush=True)
def describe(name,ok=True):
 out=subprocess.run([dotnet,str(author)],input=json.dumps(dict(operation='informationClr',project=str(manifest),id=n+name)),text=True,capture_output=True,check=True);v=json.loads(out.stdout);assert bool(v['ok'])==ok,v;return v['result']if ok else v
def build(label,ok=True):
 out=subprocess.run([dotnet,str(cli),'build',str(manifest),'portable'],text=True,capture_output=True);(case/(label+'-build.log')).write_text(out.stdout+out.stderr);assert(out.returncode==0)==ok,out.stdout[-3500:]+out.stderr[-2000:]
 if not ok:return out
 v=json.loads(out.stdout);run=subprocess.run(v['run'],text=True,capture_output=True);(case/(label+'-run.json')).write_text(json.dumps(dict(exit=run.returncode,stdout=run.stdout,stderr=run.stderr)));assert(run.returncode,run.stdout.strip())==(37,'37'),(run.returncode,run.stdout,run.stderr);return v
try:
 if mode=='baseline':
  build('baseline',False);unchanged();check('published reader refuses the explicitly versioned numeric enum contract rather than assigning ordinals or rewriting data')
 else:
  e=describe('Mood');m=describe('Rules');assert e['kind']=='enum'and e['underlyingType']=='int'and{row['id']:row['value']for row in e['members']}=={'ready-id':12,'done-id':43};assert m['interface']and m['valueType']is False and m['providerSelection']=='not-performed'and m['methods'][0]['id']==n+'Slot';assert e['bodyReads']==m['bodyReads']==0;unchanged();check('read-only descriptors expose real enum numbers/IDs and inherited module interface methods without body reads or provider selection')
  first=build('first');unchanged();check('actual native enum input/return, inline enum field, unselected0, retired-ID rejection and typed module interface dispatch execute37; existing default provider never runs')
  (p/'Mood.celem').write_text(enum_source(list(reversed([dict(id='ready-id',name='다른 표시명'),members[1]]))));assert describe('Mood')['shapeHash']==e['shapeHash'];assert build('renamed')['contractArtifacts'][n+'Echo']['key']==first['contractArtifacts'][n+'Echo']['key'];unchanged({'Mood.celem'});check('rename and reorder retain explicit numbers, C# symbols, shapes and function contract artifacts')
  (p/'Mood.celem').write_text(enum_source(members+[dict(id='later-id',name='추가')],numbers|{'later-id':44}));added=build('added');assert added['contractArtifacts'][n+'Echo']['key']!=first['contractArtifacts'][n+'Echo']['key'];unchanged({'Mood.celem'});check('adding a reserved numeric member rebuilds the enum and dependent contracts without changing existing IDs/numbers or C#')
  for label,table in [('zero',numbers|{'ready-id':0}),('duplicate',numbers|{'ready-id':43}),('missing',{'done-id':43}),('fractional',numbers|{'ready-id':1.5})]:
   (p/'Mood.celem').write_text(enum_source(table=table));describe('Mood',False);unchanged({'Mood.celem'});check('invalid '+label+' numeric contract is rejected without implicit repairs')
  (p/'Mood.celem').write_text(enum_source(profile='nominal-members-v1'));v=describe('Mood',False);assert v['code']=='ENUM_CLR_MAPPING',v;unchanged({'Mood.celem'});check('legacy ID-only definitions remain readable data but require explicit numeric-contract saving before native compilation')
  (p/'Mood.celem').write_bytes(snapshot['Mood.celem']);(p/'ParentRules.celem').write_text('module '+n+'ParentRules {require '+n+'Slot (long) -> int;default '+n+'Slot with '+n+'SlotBody;}');describe('Rules',False);unchanged({'ParentRules.celem'});check('module interface projection rejects changed required contracts instead of altering defaults or permissions')
  (p/'ParentRules.celem').write_bytes(snapshot['ParentRules.celem']);assert build('restored')['key']==first['key'];unchanged();check('exact source restoration recovers the original enum/interface artifacts and actual execution')
finally:(case/'checks.json').write_text(json.dumps(dict(checks=checks,actualWindows=False,wholeUI=False),ensure_ascii=False,indent=2));print(json.dumps(dict(evidence=str(case),checks=len(checks)),ensure_ascii=False))
