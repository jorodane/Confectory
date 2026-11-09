"""Actual nominal information assemblies and C# calls, in an owned fixture only."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile

repo=Path(sys.argv[1]).resolve();mode=sys.argv[2]if len(sys.argv)>2 else'native'
case=Path(tempfile.mkdtemp(prefix='confectory-information-structs-'));project=case/'owned project';project.mkdir();checks=[]
dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet')
cli=repo/'src/Confectory.Cli/bin/Release/net10.0/Confectory.Cli.dll';author=repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll'
ns='Owned.Information';full=lambda name:ns+'::'+name
symbol=lambda value:'E'+hashlib.sha256(json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()[:24]
typename=lambda id:'Confectory.Information.'+symbol(id.split('::')[0])+'.'+symbol(id)
vital=typename(full('Vitals'));twin=typename(full('Twin'));derived=typename(full('Derived'));empty=typename(full('Empty'))
def checked(text):checks.append(text);print('PASS '+text,flush=True)
def metadata(operation,ok=True,**body):
 p=subprocess.run([dotnet,str(author)],input=json.dumps(dict(operation=operation,**body)),text=True,capture_output=True,check=True);value=json.loads(p.stdout);assert bool(value['ok'])==ok,value;return value
def write(name,kind,text):
 (project/(name+'.celem')).write_bytes((text+'\n').replace('\n','\r\n').encode());items[name]=kind
items={}
fields='field HP single general long;field class single general long;field Active single general bool;field Title single general string;'
write('Vitals','schema','schema '+full('Vitals')+' {'+fields+'value editorFieldName_HP="체력 한글";}')
write('Twin','schema','schema '+full('Twin')+' {'+fields+'}')
write('Derived','schema','schema '+full('Derived')+' extends '+full('Vitals')+' {field Extra single general int;}')
write('Empty','schema','schema '+full('Empty')+' {}')
write('Complex','schema','schema '+full('Complex')+' {field Value single compound '+full('Vitals')+';}')
write('Main','function','function '+full('Main')+' () -> int {provide '+full('Main')+' with '+full('MainBody')+';}')
write('MainBody','implementation','implementation '+full('MainBody')+' for '+full('Main')+' () -> int {import '+full('Map')+' as Map ('+vital+') -> '+vital+';import '+full('Other')+' as Other ('+twin+') -> bool;import '+full('Extra')+' as Extra ('+derived+') -> long;import '+full('Zero')+' as Zero () -> '+empty+';body common "Main.csbody";}')
for name,args,result,source in [('Map',vital+' input',vital,'input.HP=checked(input.HP-1);input.@class=7;return input; // 직접 작성 원문 😀'),('Other',twin+' input','bool','return input.Active;'),('Extra',derived+' input','long','return checked(input.HP+input.Extra);'),('Zero','',empty,'return default;')]:
 write(name,'function','function '+full(name)+' ('+args+') -> '+result+' {provide '+full(name)+' with '+full(name+'Body')+';}')
 write(name+'Body','implementation','implementation '+full(name+'Body')+' for '+full(name)+' ('+args+') -> '+result+' {body common "'+name+'.csbody";}')
 (project/(name+'.csbody')).write_bytes((source+'\r\n').encode())
(project/'Main.csbody').write_bytes(('var original=new '+vital+' { HP=9223372036854775806L, @class=2, Active=true, Title="정보 값 😀" };\r\n'
 'var mapped=calls.Map.Invoke(original);\r\n'
 'if(original.HP!=9223372036854775806L||original.@class!=2||mapped.HP!=9223372036854775805L||mapped.@class!=7||mapped.Title!=original.Title)throw new Exception("Value boundary changed");\r\n'
 'if(!typeof('+vital+').IsValueType||typeof('+vital+')==typeof('+twin+')||!calls.Other.Invoke(new '+twin+' {Active=true}))throw new Exception("Nominal information identity changed");\r\n'
 'if(calls.Extra.Invoke(new '+derived+' {HP=30,Extra=7})!=37||!calls.Zero.Invoke().GetType().IsValueType)throw new Exception("Inherited/empty information failed");\r\n'
 'Console.WriteLine(37);return 37;\r\n').encode())
manifest=project/'project.cproj'
manifest.write_text('project '+ns+' version "1" {standalone true;entry '+full('Main')+';'+''.join('element '+name+' '+kind+' "'+name+'.celem";'for name,kind in items.items())+'registry Confectory.Build.DotNet "'+str(repo/'targets/dotnet/pack.cpack')+'";dependency Confectory.Build.DotNet version "0.1.0";target portable Confectory.Build.DotNet::Portable;}')
snapshot={str(p.relative_to(project)):p.read_bytes()for p in project.iterdir()if p.is_file()}
def unchanged(except_names=()):assert all((project/name).read_bytes()==raw for name,raw in snapshot.items()if name not in except_names)
def build(label,ok=True):
 p=subprocess.run([dotnet,str(cli),'build',str(manifest),'portable'],text=True,capture_output=True);(case/(label+'-build.log')).write_text(p.stdout+p.stderr);assert(p.returncode==0)==ok,p.stdout[-4000:]+p.stderr[-2000:]
 if not ok:return p
 result=json.loads(p.stdout);run=subprocess.run(result['run'],text=True,capture_output=True);(case/(label+'-run.json')).write_text(json.dumps(dict(exit=run.returncode,stdout=run.stdout,stderr=run.stderr)));assert(run.returncode,run.stdout.strip())==(37,'37'),(run.returncode,run.stdout,run.stderr);return result
try:
 if mode=='baseline':
  value=metadata('inspect',False,text=(project/'Map.celem').read_text());assert value['code']=='TYPE',value
  build('baseline',False);unchanged();checked('existing schema definitions are valid, but generated information function signatures are rejected before a C# type can be emitted')
 else:
  documents={name:metadata('informationStruct',project=str(manifest),id=full(name))['result']for name in ['Vitals','Twin','Derived','Empty']}
  for name,document in documents.items():assert document['clrType']==typename(full(name))and document['valueType']and document['bodyReads']==0 and document['sourceWritten']is False and document['executed']is False,document
  assert documents['Vitals']['clrType']!=documents['Twin']['clrType'];assert{field['name']for field in documents['Derived']['fields']}=={'HP','class','Active','Title','Extra'};assert documents['Empty']['fields']==[];assert 'long @class;'in documents['Vitals']['source'];unchanged();checked('read-only descriptors emit separate nominal structs, inherited stable field IDs, escaped C# keywords and empty information without reading bodies or mutating definitions')
  first=build('first');unchanged();catalog=json.load(open(first['publicCatalog']));types={item['id']:item for item in catalog['informationTypes']};assert set(types)=={full(name)for name in ['Vitals','Twin','Derived','Empty']};assert all(types[full(name)]['shapeHash']==document['shapeHash']for name,document in documents.items());assert full('Complex')not in types;checked('real pack/type/function assemblies link and execute value input/return, distinct same-shape identities, inherited/empty values and exact64/CRLF Unicode originals: result37')
  second=build('warm');assert first['key']==second['key'];unchanged();checked('a fresh builder reuses the exact unchanged information/function/implementation artifacts without changing identity or original C#')
  original=(project/'Vitals.celem').read_bytes();(project/'Vitals.celem').write_bytes(original.replace('체력 한글'.encode(),'바뀐 표시명'.encode()))
  same=metadata('informationStruct',project=str(manifest),id=full('Vitals'))['result'];assert same['shapeHash']==documents['Vitals']['shapeHash']and same['source']==documents['Vitals']['source'];renamed=build('display-only');assert renamed['contractArtifacts'][full('Map')]['key']==first['contractArtifacts'][full('Map')]['key'];unchanged({'Vitals.celem'});checked('display metadata changes retain generated identity/shape and public function contract artifacts')
  (project/'Vitals.celem').write_bytes(original.replace(b'field HP single general long;',b'field HP single general long;field Added single general long;'))
  changed=build('added-field');assert changed['contractArtifacts'][full('Map')]['key']!=first['contractArtifacts'][full('Map')]['key'];assert metadata('informationStruct',project=str(manifest),id=full('Vitals'))['result']['clrType']==vital;unchanged({'Vitals.celem'});checked('a real schema field addition changes the information and dependent function artifacts while keeping the information ID and authored C# bytes')
  (project/'Vitals.celem').write_bytes(original.replace(b'field HP single general long;',b'field Gone single general long;'));build('incompatible-field',False);unchanged({'Vitals.celem'});checked('incompatible stable-field removal fails C# compilation instead of rewriting a consumer or silently migrating data')
  (project/'Vitals.celem').write_bytes(original);restored=build('restored');assert restored['key']==first['key'];unchanged();checked('exact schema restoration recovers the original checked contract and successful execution')
  compound=metadata('informationStruct',project=str(manifest),id=full('Complex'))['result'];assert compound['profile']=='information-struct-compound-v1'and compound['dependencies'][0]['id']==full('Vitals');unchanged();checked('an inline compound field names its exact information value type without rewriting existing primitive type source or contracts')
  for label,fields in [('reference','field Value single reference '+full('Vitals')+';'),('multiple','field Values multiple general long;'),('identifier','field bad.name single general long;')]:
   path=project/'Complex.celem';raw=path.read_bytes();path.write_text('schema '+full('Complex')+' {'+fields+'}');value=metadata('informationStruct',False,project=str(manifest),id=full('Complex'));assert value['code']in ['INFORMATION_CLR_FIELD','INFORMATION_CLR_MEMBER'],value;path.write_bytes(raw);unchanged();checked('unsupported '+label+' information is explicitly rejected without object substitution, omitted members or changed originals')
  path=project/'Map.celem';raw=path.read_bytes();path.write_bytes(raw.replace(vital.encode(),(vital[:-1]+('0'if vital[-1]!='0'else'1')).encode()));build('unknown-type',False);path.write_bytes(raw);unchanged();checked('a forged generated type name cannot bind to a different or missing registered information definition')
  external=case/'registered information';external.mkdir();external_id='Registered.Values::Vitals';external_type=typename(external_id);external_schema=external/'Vitals.celem';external_raw=snapshot['Twin.celem'].replace(full('Twin').encode(),external_id.encode());external_schema.write_bytes(external_raw);(external/'pack.cpack').write_text('pack Registered.Values version "1" {element Vitals schema "Vitals.celem";}');manifest_raw=manifest.read_bytes()
  registered=manifest_raw.replace(b'registry Confectory.Build.DotNet',('registry Registered.Values "'+str(external/'pack.cpack')+'";registry Confectory.Build.DotNet').encode())
  manifest.write_bytes(registered);value=metadata('informationStruct',False,project=str(manifest),id=external_id);assert value['code']=='UNDECLARED_DEPENDENCY',value;assert external_schema.read_bytes()==external_raw;unchanged({'project.cproj'});checked('a registered locator alone cannot grant an undeclared cross-pack information dependency')
  manifest.write_bytes(registered.replace(b'registry Registered.Values',b'dependency Registered.Values version "1";registry Registered.Values',1));document=metadata('informationStruct',project=str(manifest),id=external_id)['result'];assert document['clrType']==external_type
  replaced={name:raw for name,raw in snapshot.items()if vital.encode()in raw}
  for name,raw in replaced.items():(project/name).write_bytes(raw.replace(vital.encode(),external_type.encode()))
  cross=build('registered-information');assert external_id in {item['id']for item in json.load(open(cross['publicCatalog']))['informationTypes']};assert external_schema.read_bytes()==external_raw;unchanged({'project.cproj',*replaced});checked('an explicitly declared registered information dependency compiles its separate contract assembly and executes without writing the external source')
  external_schema.write_bytes(external_raw.replace(b'field HP single general long;',b'field HP single general int;'));build('registered-incompatible',False);assert external_schema.read_bytes()!=external_raw
  external_schema.write_bytes(external_raw)
  for name,raw in replaced.items():(project/name).write_bytes(raw)
  manifest.write_bytes(manifest_raw);unchanged();assert build('registered-restored')['key']==first['key'];checked('incompatible registered schema edits fail compilation and exact restoration recovers the original program, without migration or source rewriting')
finally:
 (case/'checks.json').write_text(json.dumps(dict(checks=checks,mode=mode,actualWindows=False,wholeUI=False),ensure_ascii=False,indent=2));print(json.dumps(dict(evidence=str(case),checks=len(checks),mode=mode),ensure_ascii=False))
