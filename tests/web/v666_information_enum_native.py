"""Information enum definitions have nominal values; no Blueprint/C# enum coercion."""
import base64,copy,io,json,os,pathlib,subprocess,sys,tempfile
from PIL import Image
repo=pathlib.Path(sys.argv[1]);root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-information-enum-'));ns='Owned.Choices::'
text='enum '+ns+'Mood { // 保持する原文 😀\r\nvalue Exact=9223372036854775805; }'
manifest='project Owned.Choices version "1" {standalone true;entry '+ns+'Main;element Main function "Main.celem";element Mood enum "Mood.celem";}'
project=root/'project.cproj';project.write_text(manifest);(root/'Mood.celem').write_text(text);main='function '+ns+'Main () -> int {use enum '+ns+'Mood;}';(root/'Main.celem').write_text(main);before={p:p.read_bytes() for p in root.iterdir()}
dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet')
def call(request,ok=True):
 p=subprocess.run([dotnet,str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),capture_output=True,text=True,check=True);r=json.loads(p.stdout);assert r['ok']==ok,r;assert all(p.read_bytes()==b for p,b in before.items());return r.get('result')
def request(items):return dict(operation='functionPresentation',project=str(project),manifest=manifest,id=ns+'Mood',text=text,drafts=[dict(id=ns+'Main',text=main)],changes=[dict(type='enum-values',text=json.dumps(items,ensure_ascii=False,separators=(',',':')))])
assert call(dict(operation='create',kind='enum',id=ns+'New')).startswith('enum '+ns+'New')
assert call(dict(operation='inspect',text=text))['enumValues']==[]
buf=io.BytesIO();Image.new('RGBA',(128,128),(31,117,92,170)).save(buf,format='WEBP');image='data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode()
items=[dict(id='stable-ready',name='준비 됨',icon='★'),dict(id='stable-done',name='완료 😀',icon=image)]
req=request(items);req['changes'] += [dict(type='icon',text='≡'),dict(type='description',text='종류의 명시적 정의')];result=call(req);parsed=call(dict(operation='inspect',text=result['text']));assert parsed['enumValues']==items and parsed['values']['Exact']==9223372036854775805 and parsed['signature'] is None;assert '// 保持する原文 😀\r\n' in result['text'];assert result['manifest']==manifest and not result['additions'] and not result['updates'] and not result['sourceWritten'];assert not parsed['relations']['edges']
review=call(dict(operation='reviewSummary',kind='enum',before=text,after=result['text']));assert any(row['label']=='종류 항목' for row in review['changes']);assert 'data:image' not in json.dumps(review)
print('PASS native information enum declaration and glyph/image list preserve opaque ids, exact64, comments, registration, referenced source and non-execution meaning',flush=True)
changed=[dict(items[1],name='새 표시 이름'),dict(id=items[0]['id'],name=items[0]['name'])];req=request(changed);req['text']=result['text'];saved=call(req);assert call(dict(operation='inspect',text=saved['text']))['enumValues']==changed
req=request(changed[1:]);req['text']=saved['text'];assert call(dict(operation='inspect',text=call(req)['text']))['enumValues']==changed[1:]
print('PASS reorder, Unicode names, icon reset and unreferenced member removal preserve surviving member ids and produce one candidate only',flush=True)
for mutate in [lambda x:x.append(copy.deepcopy(x[0])),lambda x:x[1].update(name=x[0]['name']),lambda x:x[0].update(name=' '),lambda x:x[0].update(value=1),lambda x:x[0].update(icon='data:image/svg+xml;base64,PHN2Zy8+'),lambda x:x[0].update(icon=None),lambda x:x[0].update(id=None)]:
 bad=copy.deepcopy(items);mutate(bad);call(request(bad),False)
bad=request(items);bad['id']='External::Mood';call(bad,False)
bad=request(items);bad['id']=ns+'Main';bad['text']=main;call(bad,False)
call(dict(operation='inspect',text='enum '+ns+'Mood extends '+ns+'Base {}'),False)
call(dict(operation='inspect',text='enum '+ns+'Mood {value editorEnumProfile="unknown";value editorEnumValues="[]";}'),False)
print('PASS duplicate ids/names, execution values, invalid icons/profile, inheritance and foreign/wrong-kind owners are wholly refused; files remain untouched',flush=True)
