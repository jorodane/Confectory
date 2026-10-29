"""Module-local pin display candidate: exact contracts, sources and raw bytes preserved."""
import base64,copy,hashlib,io,json,os,pathlib,subprocess,sys,tempfile
from PIL import Image
repo=pathlib.Path(sys.argv[1]);root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-module-pin-native-'));ns='Owned.Pins::'
sources={'Main':('function',f'function {ns}Main () -> int {{}}'),'Required':('function',f'function {ns}Required (long value,out string result) -> long {{}}'),'Base':('module',f'module {ns}Base {{require {ns}Main () -> int;}}'),'Module':('module',f'module {ns}Module extends {ns}Base {{ // 원문·외부/부모 보존\r\nvalue Exact=9223372036854775805;require {ns}Required (long,out string) -> long;}}')}
manifest='project Owned.Pins version "1" {standalone true;entry '+ns+'Main;'+''.join(f'element {name} {kind} "{name}.celem";' for name,(kind,_) in sources.items())+'}';project=root/'project.cproj';project.write_text(manifest)
for name,(_,text) in sources.items():(root/(name+'.celem')).write_text(text)
original={p:p.read_bytes() for p in root.iterdir()};dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet')
def call(request,ok=True,errorContains=None):
 r=subprocess.run([dotnet,str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),capture_output=True,text=True,check=True);data=json.loads(r.stdout);assert data['ok']==ok,data;assert errorContains is None or errorContains in json.dumps(data,ensure_ascii=False),data;assert all(p.read_bytes()==b for p,b in original.items());return data.get('result')
def request(edits):return dict(operation='functionPresentation',project=str(project),manifest=manifest,id=ns+'Module',text=sources['Module'][1],drafts=[dict(id=ns+k,text=t) for k,(_,t) in sources.items() if k!='Module'],changes=[dict(type='module-pin-icon',text=json.dumps(e)) for e in edits])
sig=dict(args=[dict(type='long',mode=''),dict(type='string',mode='out')],**{'return':'long'})
def edit(pin,icon):return dict(function=ns+'Required',pin=pin,signature=copy.deepcopy(sig),icon=icon)
buf=io.BytesIO();Image.new('RGBA',(128,128),(90,30,190,180)).save(buf,format='WEBP');image='data:image/webp;base64,'+base64.b64encode(buf.getvalue()).decode()
changes=[edit('a0','★'),edit('a1',image),edit('return','🔥')];result=call(request(changes));before=call(dict(operation='inspect',text=sources['Module'][1]));after=call(dict(operation='inspect',text=result['text']));assert result['manifest']==manifest and not result['updates'] and not result['additions'];assert '// 원문·외부/부모 보존\r\n' in result['text'];assert after['values']['Exact']==9223372036854775805
for e in changes:
 key='editorModulePinIcon_f'+e['function'].encode().hex()+'_'+e['pin'];assert json.loads(after['values'][key])==e
for k in ['id','kind','parent','relations','signature']:assert after.get(k)==before.get(k),k
print('PASS input/out/return glyph and generated image metadata is module-local; exact64, source comments, contracts, parent, manifest and referenced function stay unchanged',flush=True)
r=request([edit('a0','')]);r['text']=result['text'];removed=call(r);assert 'a0' not in [k.rsplit('_',1)[-1] for k in call(dict(operation='inspect',text=removed['text']))['values'] if k.startswith('editorModulePinIcon_')]
for e in [edit('a3','★'),edit('a01','★'),edit('entry','★'),{**edit('a0','★'),'function':ns+'Main'},{**edit('a0','★'),'function':'External::Required'},edit('a0','ab'),edit('a0','data:image/svg+xml;base64,PHN2Zy8+'),edit('a0','data:image/webp;base64,AAAA')]:call(request([edit('return','保'),e]),False)
bad=edit('a0','★');bad['signature']['args'][0]['type']='int';call(request([bad]),False);call(request([edit('a0','★')]*2),False)
bad=request([edit('a0','★')]);bad['id']=ns+'Base';bad['text']=sources['Base'][1];call(bad,False)
print('PASS explicit reset, wrong/missing/inherited pin, ABI change, invalid URI/glyph and duplicate deny whole candidate; no source files written',flush=True)

bounded=request([edit('a0',image)]);baseline=bounded['text'][:-1]+'value Bulk="";}';padding=1048576-200-len(baseline.encode());bounded['text']=baseline.replace('Bulk=""','Bulk="'+'A'*padding+'"');assert len(bounded['text'].encode())==1048576-200;assert call(dict(operation='inspect',text=bounded['text']))['kind']=='module';call(bounded,False,errorContains="Source merge budget")
print('PASS a display-only addition cannot exceed the existing readable source budget; original source and input candidate stay untouched',flush=True)

unicode_candidate=request([edit('a0',image)]);base=unicode_candidate['text'][:-1]+' //\n}';padding=1048576-200-len(base.encode());unicode_candidate['text']=base.replace(' //\n',' //'+('한'*(padding//3))+('A'*(padding%3))+'\n');assert len(unicode_candidate['text'].encode())==1048576-200;assert len(unicode_candidate['text'])<1048576;assert call(dict(operation='inspect',text=unicode_candidate['text']))['kind']=='module';call(unicode_candidate,False,errorContains="readable unit budget")
print('PASS preserved Unicode source comments also keep the existing byte read budget; a character-count merge limit cannot admit an unreadable saved unit',flush=True)
