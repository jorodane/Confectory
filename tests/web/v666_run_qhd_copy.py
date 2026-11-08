"""Finite authored QHD opt-in; exact budget-only extension of original ownership/transport."""
import sys,pathlib,json,subprocess,hashlib,zipfile,ast
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-run-qhd-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True)
actual=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert actual==set(d['productFiles']),actual^set(d['productFiles'])
for n,h in d['productFiles'].items():assert hashlib.sha256((r/n).read_text().encode()).hexdigest()==h,n
for name in ['src','targets','packs/frame-control','packs/run-audio','packs/editor-home-model/RunWindows.csbody','examples/editor-home/WebInvoke.csbody','examples/editor-home/ui/style.css','examples/editor-home/ui/workspace-host.js','examples/editor-home/ui/v508-runtime.js','packs/project-resources','examples/editor-home/ui/resource-previews.js','examples/editor-home/ui/resource-content.js','examples/editor-home/ui/resource-images.js','examples/editor-home/ui/resource-svg.js','examples/fhd-output','examples/hd-output','examples/resizable-output']:
 assert not git('diff','--name-only',d['baseCommit'],'--',name),name
for n in ['Open.celem','OpenBody.celem','Open.csbody','OpenHD.celem','OpenHDBody.celem','OpenHD.csbody','OpenFHD.celem','OpenFHDBody.celem','OpenFHD.csbody','OpenConfigured.celem','OpenConfigured.csbody','OpenConfiguredBody.celem','OpenProfile.celem','OpenProfileBody.celem','Present.celem','Present.csbody','PresentBounds.celem','ConfigureSize.celem','ConfigureSize.csbody','RequestedSize.celem','RequestedSize.csbody','Close.celem','Close.csbody']:assert not git('diff','--name-only',d['baseCommit'],'--','packs/run-surface/'+n),n
changes={
 'packs/run-surface/OpenProfile.csbody':[('profile is <0 or >2','profile is <0 or >3'),('maxAxis=profile==2?1920:','maxAxis=profile==3?2560:profile==2?1920:'),('maxPixels=profile==2?2073600:','maxPixels=profile==3?3686400:profile==2?2073600:')],
 'packs/project-execution/Surface.csbody':[('(?:[1-9]|10)','(?:[1-9]|1[0-8])'),('var frame=Read(cursor);bool fhd=','var frame=Read(cursor);bool qhd=frame["resize"]?["max"]?.GetValue<int>()==2560&&frame["resize"]?["maxPixels"]?.GetValue<int>()==3686400,fhd='),('maxAxis=fhd?1920:','maxAxis=qhd?2560:fhd?1920:'),('maxPixels=fhd?2073600:','maxPixels=qhd?3686400:fhd?2073600:'),('(!hd&&!fhd)','(!hd&&!fhd&&!qhd)'),('(hd||fhd)','(hd||fhd||qhd)'),('(fhd?11059200:','(qhd?19660800:fhd?11059200:'),('(512 or 640 or 1280 or 1920)','(512 or 640 or 1280 or 1920 or 2560)'),('resize["maxPixels"]is not null&&','resize["max"]!.GetValue<int>()==2560&&!qhd||resize["maxPixels"]is not null&&')],
 'packs/project-execution/ResizeSurface.csbody':[('>1920','>2560'),('>2073600','>3686400')],
 'packs/editor-home-model/RunPresets.csbody':[('<=1920','<=2560'),('>2073600','>3686400')],
 'examples/editor-home/ui/run-surface.js':[('const fhd=','const qhd=packet.resize?.max===2560&&packet.resize?.maxPixels===3686400,fhd='),('maxAxis=fhd?1920:','maxAxis=qhd?2560:fhd?1920:'),('maxPixels=fhd?2073600:','maxPixels=qhd?3686400:fhd?2073600:'),('(!hd&&!fhd)','(!hd&&!fhd&&!qhd)'),('[512,640,1280,1920]','[512,640,1280,1920,2560]'),('maxPixels!==undefined&&','max===2560&&maxPixels!==3686400||maxPixels!==undefined&&'),('(max===1920?2073600:','(max===2560?3686400:max===1920?2073600:')],
 'examples/editor-home/ui/run-auto-fit.js':[('[512,640,1280,1920]','[512,640,1280,1920,2560]'),('(cap.max===1920?2073600:','(cap.max===2560?3686400:cap.max===1920?2073600:')],
 'examples/editor-home/ui/run-presets.js':[('<=1920','<=2560'),('>2073600','>3686400')],
 'examples/editor-home/ui/run-windows.js':[("['1920x1080','FHD · 1920 × 1080',1920,1080],","['1920x1080','FHD · 1920 × 1080',1920,1080],['2560x1440','QHD / 2K · 2560 × 1440',2560,1440],"),("'1920x1080','1024x768'","'1920x1080','2560x1440','1024x768'")]
}
for name,replacements in changes.items():
 expected=git('show',d['baseCommit']+':'+name)
 for a,b in replacements:assert a in expected,(name,a);expected=expected.replace(a,b)
 assert(r/name).read_text()==expected,name
assert(r/'packs/run-surface/OpenQHD.csbody').read_text()=='return calls.OpenProfile.Invoke(frameOwner,3);\n'
for n in ['OpenFHD.celem','OpenFHDBody.celem','OpenFHD.csbody']:
 expected=git('show',d['baseCommit']+':packs/run-surface/'+n).replace('FHD','QHD').replace('1920','2560').replace('2073600','3686400').replace('frameOwner,2','frameOwner,3');assert(r/'packs/run-surface'/n.replace('FHD','QHD')).read_text()==expected
old=git('show',d['baseCommit']+':packs/run-surface/pack.cpack');assert(r/'packs/run-surface/pack.cpack').read_text()==old.replace('element OpenFHD function','element OpenQHD function "OpenQHD.celem";element OpenQHDBody implementation "OpenQHDBody.celem";\nelement OpenFHD function')
p=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');old=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert p[0]==old[0]and p[2]==old[2];bundle=json.loads(p[1]);before=json.loads(old[1]);assert set(bundle)==set(before)
for n,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),n
 if n not in ['run-surface.js','run-windows.js','run-auto-fit.js','run-presets.js']:assert row==before[n],n
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 app=z.read('Confectory-v666/dist/app.js').decode();assert "['2560x1440','QHD / 2K · 2560 × 1440']"in app
 edit=z.read('Confectory-v666/dist/resource-edit.js').decode();assert "if(blob.size>1024*1024)throw"in edit and "if(blob.size>32*1024*1024)throw"in edit
for n in ['Surface','ResizeSurface']:
 s=(r/('packs/project-execution/'+n+'.csbody')).read_text();assert 'CancellationTokenSource(300)'in s and 'CurrentUserOnly'in s
assert 'length is <1 or >1400000'in(r/'packs/project-execution/Surface.csbody').read_text()
tree=ast.parse((r/'tools/verify_desktop.py').read_text());branches=[n for n in ast.walk(tree)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'run-qhd'"];assert len(branches)==3
calls=[ast.unparse(n)for b in branches for statement in b.body for n in ast.walk(statement)if isinstance(n,ast.Call)]
for token in ["work.run(label + '-run-qhd-boundary'","work.run('packaged-run-qhd-'","work.run('restored-run-qhd-'"]:assert sum(token in c for c in calls)==1,token
print('PASS exact explicit QHD profile extension and authored menu; existing Open/HD/FHD public contracts, core/source/ownership/authority/ACK/300ms/packet limits/layout preserved; canonical assets and package/restore routing')
