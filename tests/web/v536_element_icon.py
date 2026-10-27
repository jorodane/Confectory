"""Pure glyph owner candidates reject an invalid last change without writes."""
import hashlib,json,os,pathlib,subprocess,sys,tempfile
repo=pathlib.Path(sys.argv[1]).resolve();root=pathlib.Path(tempfile.mkdtemp(prefix='confectory-element-icon-'));n='Owned.Icon::'
items={'Main':('function','function '+n+'Main () -> int {}'),'Base':('object','object '+n+'Base {}'),'Info':('schema','schema '+n+'Info { // exact schema source\nfield Count single general long;value editorInformationDefaults="typed-json-v1";value editorFieldDefault_Count="9223372036854775806";}'),'Item':('object','object '+n+'Item extends '+n+'Base { // exact object source\nuse schema '+n+'Info;data Count=9223372036854775805;}')}
manifest='project Owned.Icon version "1" {standalone true;entry '+n+'Main;'+''.join('element '+k+' '+kind+' "'+k+'.celem";' for k,(kind,text) in items.items())+'}'
project=root/'project.cproj';project.write_text(manifest)
for k,(_,text) in items.items():(root/(k+'.celem')).write_text(text)
original={p:p.read_bytes() for p in root.rglob('*') if p.is_file()};checks=[]
def call(owner,changes,ok=True):
 request={'operation':'informationDefinitions' if owner=='Info' else 'mixedOwnerCopyEdits','project':str(project),'manifest':manifest,'id':n+owner,'text':items[owner][1],'drafts':[{'id':n+k,'text':text} for k,(_,text) in items.items() if k!=owner],'changes':changes}
 r=subprocess.run([os.environ.get('CONFECTORY_DOTNET','/workspace/toolchains/dotnet-10.0.401/dotnet'),str(repo/'targets/element-authoring/bin/Release/net10.0/Confectory.ElementAuthoring.dll')],input=json.dumps(request),text=True,capture_output=True,timeout=60);assert r.returncode==0,r.stderr
 value=json.loads(r.stdout);assert value['ok']==ok,value;assert all(p.read_bytes()==b for p,b in original.items());return value.get('result')
for owner in ['Info','Item']:
 for glyph in ['🛡️','👨‍👩‍👧‍👦','e\u0301','★']:
  value=call(owner,[{'type':'description','text':'아이콘과 설명'},{'type':'icon','text':glyph}]);assert value['manifest']==manifest and not value['updates'] and not value['additions'] and not value['sourceWritten'] and not value['compiled'];assert 'editorIcon' in value['text'] and ('9223372036854775806' if owner=='Info' else '9223372036854775805') in value['text'] and '// exact ' in value['text']
 for glyph in ['', 'ab','<','&','\x00','🌍🌿',' ★','data:image/png;base64,AAAA']:
  call(owner,[{'type':'description','text':'부분 적용 금지'},{'type':'icon','text':glyph}],False)
 for change in [[{'type':'icon','text':'★'},{'type':'icon','text':'🌍'}],[{'type':'icon','text':'★','owner':n+'Base'}]]:call(owner,change,False)
 checks.append(owner+' single-grapheme symbol/emoji candidate, exact64/comments/parent/source preservation, invalid last/duplicate/foreign-operation rejection');print('PASS '+checks[-1],flush=True)
print(json.dumps({'checks':checks,'evidence':str(root),'sourceSha256':{p.name:hashlib.sha256(b).hexdigest() for p,b in original.items()},'actualEngine':False,'sourceWritten':False,'execution':False},indent=2))
