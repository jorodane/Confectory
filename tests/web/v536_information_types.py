"""Named information/nested defaults, pure candidate; no native account or source writes."""
import copy,hashlib,json,os,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet');root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-information-'));n='Owned.Info::';owner=n+'A'
items={'Main':('function','function '+n+'Main () -> int {}'),'Base':('schema','schema '+n+'Base {field Power single general long;value editorName="기본 정보";}'),'Details':('schema','schema '+n+'Details extends '+n+'Base {field Label single general string;}'),'Nested':('schema','schema '+n+'Nested {field Child single compound '+n+'Details;field Counts multiple general long;}'),'Ref':('schema','schema '+n+'Ref {field Target single reference '+n+'Details;}'),'Custom':('schema','schema '+n+'Custom {field Power single general long;value special=5;}'),'DerivedCustom':('schema','schema '+n+'DerivedCustom extends '+n+'Custom {}'),'NestedCustom':('schema','schema '+n+'NestedCustom {field Child single compound '+n+'DerivedCustom;}'),'A':('object','object '+owner+' {}')}
manifest='project Owned.Info version "1" {standalone true;entry '+n+'Main;'+''.join('element '+k+' '+kind+' "'+k+'.celem";' for k,(kind,text) in items.items())+'}';project=root/'project.cproj';project.write_text(manifest)
for k,(kind,text) in items.items():(root/(k+'.celem')).write_text(text)
original={p:p.read_bytes() for p in root.iterdir()};drafts=[{'id':n+k,'text':text} for k,(kind,text) in items.items() if k!='A'];base={'project':str(project),'manifest':manifest,'id':owner,'text':items['A'][1],'drafts':drafts}
def call(operation,extra={},ok=True):
 r=subprocess.run([dotnet,str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps({**base,'operation':operation,**extra}),text=True,capture_output=True,timeout=60);assert r.returncode==0,r.stderr;reply=json.loads(r.stdout);assert reply['ok']==ok,reply;assert all(p.read_bytes()==data for p,data in original.items());return reply.get('result')
catalogue=call('informationTypes');choices={r['id']:r for r in catalogue};nested=choices[n+'Nested'];assert nested['available'] and json.loads(nested['valueJson'])=={'Child':{'Power':0,'Label':''},'Counts':[0]};assert set(nested['sources'])=={n+'Nested',n+'Details',n+'Base'};assert not choices[n+'Ref']['available'] and not choices[n+'Custom']['available'] and not choices[n+'DerivedCustom']['available'] and not choices[n+'NestedCustom']['available'];print('PASS original information fallback defaults preserve inherited/nested shape and multiple first item; unresolved ref/custom defaults stay unavailable',flush=True)
definition={'type':'information-definition','name':'Stats','schema':n+'Nested','sources':nested['sources'],'valueJson':'{"Child":{"Power":9223372036854775806,"Label":"한글"},"Counts":[9223372036854775805,2]}'};changes=[{'type':'description','text':'중첩 정보'},definition];result=call('mixedOwnerCopyEdits',{'changes':changes});assert 'field Stats single compound '+n+'Nested;' in result['additions'][0]['text'];assert '9223372036854775806' in result['text'] and '9223372036854775805' in result['text'];assert '한글' in result['text'];assert len(result['additions'])==1;assert result==call('mixedOwnerCopyEdits',{'changes':copy.deepcopy(changes)});print('PASS one deterministic candidate creates owned compound definition plus exact long/nested Korean data without changing reusable information sources',flush=True)
for kind in ['hash','missing','type','unknown','name','foreign','ref','duplicate']:
 bad=copy.deepcopy(changes)
 if kind=='hash':bad[-1]['sources'][n+'Base']='0'*64
 elif kind=='missing':bad[-1]['sources'].pop(n+'Details')
 elif kind=='type':bad[-1]['valueJson']='{"Child":{"Power":true,"Label":"원문"}}'
 elif kind=='unknown':bad[-1]['valueJson']='{"Unknown":5}'
 elif kind=='name':bad[-1]['name']='bad; field injected single general long;'
 elif kind=='foreign':bad[-1]['schema']='Other::Nested'
 elif kind=='ref':bad[-1].update(schema=n+'Ref',sources={n+'Ref':hashlib.sha256(items['Ref'][1].encode()).hexdigest()})
 else:bad.append(copy.deepcopy(bad[-1]))
 call('mixedOwnerCopyEdits',{'changes':bad},False)
print('PASS stale/incomplete source proof, invalid nested value/name/foreign/ref and duplicate definition reject the entire pure candidate; all fixture source bytes unchanged',flush=True)
print(json.dumps({'evidence':str(root),'pureMetadata':True,'actualEngine':False,'renderer':False,'accountOrInference':False}))
