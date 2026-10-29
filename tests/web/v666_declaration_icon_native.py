"""Owned category/concept/module presentation, original sources never written."""
import base64,hashlib,io,json,os,pathlib,subprocess,sys,tempfile
from PIL import Image
repo=pathlib.Path(sys.argv[1]);root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-declaration-icons-native-'));ns='Owned.Headers::'
sources={'Main':('function',f'function {ns}Main () -> int {{}}')}
for name,kind in [('Category','category'),('Concept','concept'),('Module','module')]:
 sources[name+'Base']=(kind,f'{kind} {ns}{name}Base {{description "부모 원본";value editorIcon="🌿";}}')
 sources[name]=(kind,f'{kind} {ns}{name} extends {ns}{name}Base {{ // 원문·부모 보존\r\nvalue Exact=9223372036854775805;'+(f'require {ns}Main () -> int;' if kind=='module' else '')+'}')
manifest='project Owned.Headers version "1" {standalone true;entry '+ns+'Main;'+''.join(f'element {name} {kind} "{name}.celem";' for name,(kind,_) in sources.items())+'}'
project=root/'project.cproj';project.write_text(manifest)
for name,(_,text) in sources.items():(root/(name+'.celem')).write_text(text)
original={p:p.read_bytes() for p in root.iterdir()};dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet')
def call(request,ok=True):
 result=subprocess.run([dotnet,str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),capture_output=True,text=True,check=True);data=json.loads(result.stdout);assert data['ok']==ok,data;assert all(p.read_bytes()==b for p,b in original.items());return data.get('result')
def request(name,changes):return dict(operation='functionPresentation',project=str(project),manifest=manifest,id=ns+name,text=sources[name][1],drafts=[dict(id=ns+k,text=t) for k,(_,t) in sources.items() if k!=name],changes=changes)
def semantic(value):
 if isinstance(value,dict):return {k:semantic(v) for k,v in value.items() if k!='Loc'}
 if isinstance(value,list):return [semantic(v) for v in value]
 return value
buffer=io.BytesIO();Image.new('RGBA',(128,128),(30,90,180,170)).save(buffer,format='WEBP',quality=90);image='data:image/webp;base64,'+base64.b64encode(buffer.getvalue()).decode()
for name in ['Category','Concept','Module']:
 before=call(dict(operation='inspect',text=sources[name][1]));result=call(request(name,[dict(type='icon',text=image),dict(type='description',text='선택된 헤더 설명')]))
 after=call(dict(operation='inspect',text=result['text']));assert after['values']['editorIcon']==image and after['values']['Exact']==9223372036854775805;assert '// 원문·부모 보존\r\n' in result['text'];assert result['manifest']==manifest and not result['additions'] and not result['updates']
 for key in ['id','kind','parent','relations','signature']:
  assert semantic(before.get(key))==semantic(after.get(key)),key
 assert call(dict(operation='relationsMap',units=[dict(id=ns+name,kind=sources[name][0],text=result['text'],revision=1,textHash=hashlib.sha256(result['text'].encode()).hexdigest(),dirty=True)]))['nodes'][0]['icon']==image
 legacy=call(dict(operation='editDeclaration',text=sources[name][1],edit=dict(action='properties',values={'icon':'legacy text'})));assert 'legacy text' in legacy
 direct=call(dict(operation='editDeclaration',text=sources[name][1],edit=dict(action='properties',values={'icon':image})));assert call(dict(operation='inspect',text=direct))['values']['editorIcon']==image
 print('PASS '+name+' image/description candidate, exact64/comments/parent/contracts/registration, Browser projection and existing text metadata',flush=True)
 for value in ['https://example.invalid/icon.webp','<svg onload="bad"/>','data:image/webp;base64,AAAA','data:image/webp;base64,'+'A'*65500,'ab']:
  call(request(name,[dict(type='description',text='전체 미적용'),dict(type='icon',text=value)]),False)
 for value in ['data:image/webp;base64,AAAA','data:image/svg+xml;base64,PHN2Zy8+']:
  call(dict(operation='editDeclaration',text=sources[name][1],edit=dict(action='properties',values={'description':'전체 미적용','icon':value})),False)
 for edits in [[dict(type='icon',text='★')]*2,[dict(type='parent',text=ns+'Main')],[dict(type='signature',text='void')]]:call(request(name,edits),False)
 foreign=request(name,[dict(type='icon',text='★')]);foreign['id']='External::'+name;call(foreign,False)
print('PASS invalid image/duplicate/contract/foreign owner denied as a whole; original files unchanged',flush=True)
