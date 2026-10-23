"""Owned schema + owner data candidate. Isolated files; no source mutation or account access."""
import copy,hashlib,json,os,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();dotnet=os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet');root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-schema-metadata-'));n='Owned.Schema::';owner=n+'A'
items={'Main':('function','function '+n+'Main () -> int {}'),'Local':('schema','schema '+n+'Local {field Mana single general long;field Label single general string;}'),'A':('object','object '+owner+' {use schema '+n+'Local;data Mana=9223372036854775806;data Label="원문";}'),'Other':('object','object '+n+'Other {}')}
manifest='project Owned.Schema version "1" {standalone true;entry '+n+'Main;'+''.join('element '+key+' '+kind+' "'+key+'.celem";' for key,(kind,text) in items.items())+'}';project=root/'project.cproj';project.write_text(manifest)
for key,(kind,text) in items.items():(root/(key+'.celem')).write_text(text)
original={p:p.read_bytes() for p in root.iterdir()};shape={'kind':'general','cardinality':'single','type':'long'};hash=lambda text:hashlib.sha256(text.encode()).hexdigest()
contract={'type':'schema-field','path':['Mana'],'contract':shape,'schema':n+'Local','schemaHash':hash(items['Local'][1]),'nativeType':'string'}
def call(changes,ok=True,drafts=None):
 request={'operation':'mixedOwnerCopyEdits','project':str(project),'manifest':manifest,'id':owner,'text':items['A'][1],'drafts':drafts or [{'id':n+key,'text':text} for key,(kind,text) in items.items() if key!='A'],'changes':changes};r=subprocess.run([dotnet,str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),text=True,capture_output=True,check=True);v=json.loads(r.stdout);assert v['ok']==ok,v;assert all(p.read_bytes()==raw for p,raw in original.items());return v.get('result')
call([contract,{'type':'description','text':'일부 적용 금지'}],False);print('PASS incompatible existing raw number is not cast, defaulted or discarded; entire pure candidate rejects without file mutation')
changes=[contract,{'type':'data','path':['Mana'],'contract':shape,'valueJson':'"한글 명시 값"'},{'type':'description','text':'한 후보'}];v=call(changes);assert 'field Mana single general string;' in v['updates'][0]['text'] and v['updates'][0]['hash']==hash(items['Local'][1]);assert 'data Mana = "한글 명시 값"' in v['text'] or '"한글 명시 값"' in v['text'];assert v['manifest']==manifest and not v['additions'];assert v==call(copy.deepcopy(changes));print('PASS explicit schema/data/description candidate preserves identities, original hashes and unmodified declarations')
wide=copy.deepcopy(contract);wide['nativeType']='double';v=call([wide]);assert '9223372036854775806' in v['text'];print('PASS explicit compatible type change keeps the exact original 64-bit numeric source text')
for mutation in ['hash','foreign','shape','duplicate','input']:
 bad=copy.deepcopy(changes)
 if mutation=='hash':bad[0]['schemaHash']='0'*64
 elif mutation=='foreign':bad[0]['schema']='Other.Project::Local'
 elif mutation=='shape':bad[0]['contract']['type']='bool'
 elif mutation=='duplicate':bad.append(bad[0])
 else:bad[1]['valueJson']='true'
 call(bad,False)
print('PASS stale/foreign/contract/duplicate/new-value type violations refuse all schema/data edits')
print(json.dumps({'evidence':str(root),'sourceWritten':False,'nativeWindows':False}))
