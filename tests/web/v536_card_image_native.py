"""Bounded card images use existing owned definition/function candidates; no writes."""
import base64,hashlib,io,json,os,pathlib,subprocess,sys,tempfile
from PIL import Image,ImageCms
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-card-image-native-'));n='Owned.CardImage::';fn=n+'Info_Function_'+'1'*32;fresh=n+'Info_Function_'+'2'*32
sources={
 'Main':('function',f'function {n}Main () -> int {{}}'),
 'BaseInfo':('schema',f'schema {n}BaseInfo {{field Inherited single general long;value editorFieldIcon_Inherited="🌿";}}'),
 'Info':('schema',f'schema {n}Info extends {n}BaseInfo {{ // preserve information\nfield Count single general long;value editorInformationDefaults="typed-json-v1";value editorFieldDefault_Count="9223372036854775805";contain function {fn};}}'),
 fn.split('::')[-1]:('function',f'function {fn} (long amount,out bool active) -> long {{ // preserve function\nvalue editorName="OwnedCard";description "원래 설명";provide {fn} with {n}Body;}}'),
 'Body':('implementation',f'implementation {n}Body for {fn} (long amount,out bool active) -> long {{body common "Body.csbody";}}'),
 'Parent':('object',f'object {n}Parent {{description "보존 부모";}}'),
 'Item':('object',f'object {n}Item extends {n}Parent {{use schema {n}Info;data Count=9223372036854775804;data Inherited=7;}}')}
paths={k:('elements/'+k+'.celem' if k.startswith('Info_Function_') else k+'.celem') for k in sources}
manifest=f'project Owned.CardImage version "1" {{standalone true;entry {n}Main;'+''.join(f'element {k} {kind} "{paths[k]}";' for k,(kind,t) in sources.items())+'}'
(root/'elements').mkdir();(root/'project.cproj').write_text(manifest);(root/'Body.csbody').write_text('active=true;return amount+1;')
for k,(kind,text) in sources.items():(root/paths[k]).write_text(text)
original={p:p.read_bytes() for p in root.rglob('*') if p.is_file()};checks=[]
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def call(changes,owner='Info',operation=None,ok=True,**extra):
 req=dict(operation=operation or ('informationDefinitions' if owner=='Info' else 'mixedOwnerCopyEdits'),project=str(root/'project.cproj'),manifest=manifest,id=n+owner,text=sources[owner][1],drafts=[dict(id=n+k,text=t) for k,(_,t) in sources.items() if k!=owner],changes=changes);req.update(extra)
 p=subprocess.run([os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'),str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(req),text=True,capture_output=True,timeout=60);assert p.returncode==0,p.stderr;v=json.loads(p.stdout);assert v['ok']==ok,v;assert all(p.read_bytes()==b for p,b in original.items());return v.get('result')
def image(alpha=False,lossless=False,profile=False):
 b=io.BytesIO();Image.new('RGBA' if alpha else 'RGB',(128,128),(40,90,150,123) if alpha else (40,90,150)).save(b,format='WEBP',quality=90,lossless=lossless,**({'icc_profile':ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()} if profile else {}));return 'data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode()
def property(value,**extra):return dict(type='schema-icon',path=['Count'],contract=dict(kind='general',type='long',cardinality='single'),schema=n+'Info',schemaHash=sha(sources['Info'][1]),text=value,**extra)
def function(value,new=False):return dict(type='function-add' if new else 'function-edit',id=fresh if new else fn,**({} if new else {'hash':sha(sources[fn.split('::')[-1]][1])}),name='FreshCard' if new else 'OwnedCard',description='이미지 설명',signature=dict(args=[] if new else [dict(name='amount',type='long'),dict(name='active',type='bool',mode='out')],**{'return':'void' if new else 'long'}),icon=value)
def effective(result,owner='Info'):
 drafts=[dict(id=n+k,text=t) for k,(_,t) in sources.items() if k!=owner]
 for row in result.get('updates',[])+result.get('additions',[]):
  drafts=[d for d in drafts if d['id']!=row['id']]+[dict(id=row['id'],text=row['text'])]
 return call([],owner,operation='effective',text=result['text'],manifest=result['manifest'],drafts=drafts,schemaView=True)
def check(s):checks.append(s);print('PASS '+s,flush=True)
for alpha,lossless,profile in [(a,l,p) for a in [False,True] for l in [False,True] for p in [False,True]]:
 value=image(alpha,lossless,profile)
 for owner in ['Info','Item']:
  r=call([dict(type='description',text='원자 설명'),property(value)],owner);view=effective(r,owner);assert view['schemaModel']['fields']['Count']['icon']==value
  assert (not r['updates'] and '9223372036854775805' in r['text']) if owner=='Info' else len(r['updates'])==1 and '9223372036854775804' in r['text'] and f'extends {n}Parent' in r['text']
 for new in [False,True]:
  r=call([dict(type='description',text='원자 설명'),function(value,new)]);method=next(v for v in effective(r)['ownFunctions'] if v['id']==(fresh if new else fn));assert method['icon']==value and method['writable'];assert len(r['additions'] if new else r['updates'])==1
  if not new:assert 'preserve function' in r['updates'][0]['text'] and f'provide {fn} with {n}Body' in r['updates'][0]['text']
check('information/object property and existing/new owned function images share bounded normalized WebP validation; metadata, exact64, C#, parent and sources are preserved')
value=image(True)
for owner in ['Info','Item']:
 r=call([property('')],owner);text=r['text'] if owner=='Info' else r['updates'][0]['text'];assert 'editorFieldIcon_Count' not in text
for bad in ['data:image/png;base64,AAAA',value+' ',value[:-3],'/private/icon.webp','https://example.invalid/icon.webp','data:image/svg+xml;base64,PHN2Zz4=','data:image/webp;base64,'+'A'*65500,'ab']:
 for owner in ['Info','Item']:call([dict(type='description',text='no partial'),property(bad)],owner,ok=False)
 for new in [False,True]:call([dict(type='description',text='no partial'),function(bad,new)],ok=False)
call([function(value),function('ab',True)],ok=False);call([property(value),property(value)],ok=False)
check('clear remains property-only; malformed/remote/path/oversize/invalid last image and duplicate edits reject whole candidates and never partially add/register/update')
for bad in [{**property(value),'schemaHash':'0'*64},{**property(value),'schema':'Foreign::Info'},{**property(value),'path':['Inherited'],'schema':n+'BaseInfo'},{**property(value),'path':['Count','child']},{**property(value),'contract':dict(kind='general',type='bool',cardinality='single')}]:
 for owner in ['Info','Item']:call([dict(type='description',text='all retained'),bad],owner,ok=False)
for bad in [{**function(value),'hash':'0'*64},{**function(value),'id':'Foreign::Card'},{**function(value),'id':n+'Main'}]:call([dict(type='description',text='no partial'),bad],ok=False)
check('unchanged typed path/source/hash/ownership rules reject inherited, external, unrelated and stale card requests without changing parent/public contracts')
for owner in ['Info','Item']:
 change=dict(type='typed-definition',name='Fresh',contract=dict(kind='general',type='long',cardinality='single'),sources=None,valueJson='9223372036854775804',icon=value,**({'displayName':'새 이미지 속성'} if owner=='Info' else {}));r=call([change],owner);view=effective(r,owner);assert view['schemaModel']['fields']['Fresh']['icon']==value
 call([change,{**change,'name':'Last','icon':'ab'}],owner,ok=False)
check('new information/object property definition/value/image/registration is one candidate; invalid final metadata leaves no partial schema')
print(json.dumps(dict(checks=checks,evidence=str(root),sourceWritten=False,userFiles=False,uploaded=False),ensure_ascii=False))
