"""Pure information module candidate validation; isolated files, no execution or accounts."""
import hashlib,json,os,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve()
dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet')
root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-information-modules-'));n='Owned.InfoModules::';owner=n+'Details'
items={
 'Main':('function','function '+n+'Main () -> int {}'),
 'Slot':('function','function '+n+'Slot (long amount) -> long {}'),
 'Body':('implementation','implementation '+n+'Body for '+n+'Slot (long amount) -> long {body common "Body.csbody";}'),
 'Rules':('module','module '+n+'Rules {require '+n+'Slot (long) -> long;default '+n+'Slot with '+n+'Body;}'),
 'Empty':('module','module '+n+'Empty {}'),
 'Base':('schema','schema '+n+'Base {field Count single general long;module '+n+'Empty;}'),
 'Details':('schema','schema '+owner+' extends '+n+'Base { // 원문 주석\nfield Power single general long;provide '+n+'Slot with '+n+'Body;value editorInformationDefaults="typed-json-v1";value editorFieldDefault_Power="9223372036854775806";}'),
}
registered=root/'registered';registered.mkdir()
(registered/'pack.cpack').write_text('pack External.InfoModules version "1" {element Rules module "Rules.celem";element Slot function "Slot.celem";element Body implementation "Body.celem";}')
(registered/'Rules.celem').write_text('module External.InfoModules::Rules {require External.InfoModules::Slot (long) -> long;default External.InfoModules::Slot with External.InfoModules::Body;}')
(registered/'Slot.celem').write_text('function External.InfoModules::Slot (long amount) -> long {}')
(registered/'Body.celem').write_text('implementation External.InfoModules::Body for External.InfoModules::Slot (long amount) -> long {body common "Body.csbody";}')
(registered/'Body.csbody').write_text('return amount;')
manifest='project Owned.InfoModules version "1" {standalone true;entry '+n+'Main;'+''.join('element '+k+' '+kind+' "'+k+'.celem";' for k,(kind,_) in items.items())+'registry External.InfoModules "registered/pack.cpack";dependency External.InfoModules version "1";}'
project=root/'project.cproj';project.write_text(manifest);(root/'Body.csbody').write_text('return amount;')
for k,(_,text) in items.items():(root/(k+'.celem')).write_text(text)
original={p:p.read_bytes() for p in root.rglob('*') if p.is_file()};drafts=[{'id':n+k,'text':text} for k,(_,text) in items.items() if k!='Details']
base={'project':str(project),'manifest':manifest,'id':owner,'text':items['Details'][1],'drafts':drafts}
def call(op,ok=True,**extra):
 r=subprocess.run([dotnet,str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({**base,'operation':op,**extra}),text=True,capture_output=True,timeout=60)
 assert r.returncode==0,r.stderr
 value=json.loads(r.stdout);assert value['ok']==ok,value
 assert all(p.read_bytes()==b for p,b in original.items())
 return value.get('result')
def module(ids):return {'type':'modules','ids':ids}
result=call('informationDefinitions',changes=[module([n+'Rules']),{'type':'description','text':'기능 계약 연결'}, {'type':'data','path':['Power'],'contract':{'kind':'general','cardinality':'single','type':'long'},'valueJson':'9223372036854775805'}])
assert '// 원문 주석' in result['text'] and 'provide '+n+'Slot with '+n+'Body;' in result['text']
assert result['manifest']==manifest and not result['additions'] and not result['updates'] and not result['sourceWritten'] and not result['compiled']
view=call('effective',text=result['text'],schemaView=True,validateObjects=True)
assert view['status']=='available' and view['schemaModel']['validation']['status']=='valid'
assert {(m['id'],m['origin']) for m in view['modules']}=={(n+'Empty',n+'Base'),(n+'Rules',owner)}
assert view['requirements'][0]['function']==n+'Slot' and view['providers'][0]['implementation']==n+'Body'
assert view['schemaModel']['data']['Power']['scalar']==9223372036854775805 and not view['schemaModel']['executionAuthorized']
print('PASS schema module/description/exact64 candidate preserves inherited modules, own provide, comments, files and no execution authority',flush=True)
unlinked=call('informationDefinitions',text=result['text'],changes=[module([])])
view=call('effective',text=unlinked['text'],schemaView=True,validateObjects=True)
assert [(m['id'],m['origin']) for m in view['modules']]==[(n+'Empty',n+'Base')]
assert view['providers'][0]['implementation']==n+'Body' and '9223372036854775805' in unlinked['text']
print('PASS own module unlink preserves inherited relations, explicit provider and all information defaults',flush=True)
for bad in [module([n+'Rules',n+'Rules']),module([n+'Base']),module(['Other::Missing']),module([n+'Missing']),module([n+'Empty']*33),{'type':'modules','ids':[n+'Rules'],'provide':n+'Body'},{'type':'provide','ids':[n+'Body']}]:
 call('informationDefinitions',False,changes=[{'type':'description','text':'부분 적용 금지'},bad])
call('informationDefinitions',False,changes=[module([n+'Rules']),module([])])
print('PASS wrong-kind/foreign/missing/duplicate/oversized/unknown rights reject whole candidate without source changes',flush=True)
bad_drafts=[d if d['id']!=n+'Rules' else {**d,'text':d['text'].replace('(long) -> long','(bool) -> long')} for d in drafts]
call('informationDefinitions',False,drafts=bad_drafts,changes=[module([n+'Rules'])])
print('PASS mismatched required function/default contract is rejected by full metadata validation',flush=True)
external=call('informationDefinitions',changes=[module(['External.InfoModules::Rules'])])
observed={pathlib.Path(v['path']):v['hash'] for v in external['observations']}
for name in ['pack.cpack','Rules.celem','Slot.celem','Body.celem']:
 p=registered/name;assert observed[p]==hashlib.sha256(p.read_bytes()).hexdigest()
assert registered/'Body.csbody' not in observed
print('PASS newly attached registered module/function/provider declarations are included in final immutable observations without reading or executing body',flush=True)
print(json.dumps({'evidence':str(root),'actualEngine':False,'renderer':False,'nativeWindows':False,'accountOrInference':False}))
