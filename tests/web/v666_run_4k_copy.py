"""Finite explicit4K extension; preserve original contracts/layout and transport budgets."""
import sys,pathlib,json,subprocess,hashlib,zipfile,ast
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-run-4k-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True)
actual=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert actual==set(d['productFiles']),actual^set(d['productFiles'])
for n,h in d['productFiles'].items():assert hashlib.sha256((r/n).read_text().encode()).hexdigest()==h,n
for name in ['src','targets','packs/frame-control','packs/run-audio','packs/editor-home-model/RunWindows.csbody','packs/project-resources','examples/editor-home/ui/run-windows.js','examples/editor-home/ui/workspace-host.js','examples/editor-home/ui/style.css','examples/editor-home/ui/index.html','examples/editor-home/WebInvoke.csbody','examples/qhd-output','examples/fhd-output','examples/hd-output','examples/resizable-output']:assert not git('diff','--name-only',d['baseCommit'],'--',name),name
for n in ['Open.celem','Open.csbody','OpenHD.celem','OpenHD.csbody','OpenFHD.celem','OpenFHD.csbody','OpenQHD.celem','OpenQHD.csbody','OpenConfigured.celem','OpenConfigured.csbody','OpenProfile.celem','OpenProfileBody.celem','Present.celem','Present.csbody','ConfigureSize.celem','ConfigureSize.csbody','RequestedSize.celem','RequestedSize.csbody','Close.celem','Close.csbody']:assert not git('diff','--name-only',d['baseCommit'],'--','packs/run-surface/'+n),n
old=git('show',d['baseCommit']+':packs/run-surface/OpenProfile.csbody');expected=old.replace('profile is <0 or >3','profile is <0 or >4').replace('maxAxis=profile==3?2560:','maxAxis=profile==4?4096:profile==3?2560:').replace('maxPixels=profile==3?3686400:','maxPixels=profile==4?8847360:profile==3?3686400:');assert(r/'packs/run-surface/OpenProfile.csbody').read_text()==expected
assert(r/'packs/run-surface/Open4K.csbody').read_text()=='return calls.OpenProfile.Invoke(frameOwner,4);\n'
for n in ['Surface','ResizeSurface']:
 s=(r/('packs/project-execution/'+n+'.csbody')).read_text();assert 'CancellationTokenSource(300)'in s and 'CurrentUserOnly'in s
assert 'length is <1 or >1400000'in(r/'packs/project-execution/Surface.csbody').read_text()
s=(r/'packs/project-execution/Surface.csbody').read_text();legacy=git('show',d['baseCommit']+':packs/project-execution/Surface.csbody');start='  System.Text.Json.Nodes.JsonObject Read(string selected){';end='  System.Text.Json.Nodes.JsonObject Metadata('
assert s.split(start,1)[1].split(end,1)[0].replace('\n   if(ioBudget4K)return Read4K(selected);','')==legacy.split(start,1)[1].split(end,1)[0]
for text in ['ioBudget=System.Diagnostics.Stopwatch.Frequency*300L/1000','long remaining=ioBudget-ioSpent','ioSpent=checked(ioSpent+ioClock.ElapsedTicks)','if(ioSpent>ioBudget)','connect.CancelAfter(25)','ioBudget4K=uhd;']:assert text in s

p=(r/'examples/editor-home/WebBundle.csbody').read_text().split('"""');old=git('show',d['baseCommit']+':examples/editor-home/WebBundle.csbody').split('"""');assert p[0]==old[0]and p[2]==old[2];bundle=json.loads(p[1]);before=json.loads(old[1]);assert set(bundle)==set(before)
for n,row in bundle.items():
 raw=(r/'examples/editor-home/ui'/row['file']).read_bytes();raw=raw.replace(b'\r\n',b'\n')if row.get('bytePolicy')=='utf8-lf-v1'else raw;assert len(raw)==row.get('canonicalSize',row.get('size'))and hashlib.sha256(raw).hexdigest()==row.get('canonicalSha256',row.get('sha256')),n
 if n not in ['run-surface.js','run-auto-fit.js','run-presets.js']:assert row==before[n],n
reference=r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip';assert hashlib.sha256(reference.read_bytes()).hexdigest()==d['referenceSha256']
with zipfile.ZipFile(reference)as z:
 app=z.read('Confectory-v666/dist/app.js').decode()
 for text in ["['3840x2160','4K UHD · 3840 × 2160']","['4096x2160','DCI 4K · 4096 × 2160']","['1290x2796','1290 × 2796']","['1440x3200','QHD+ · 1440 × 3200']"]:assert text in app
s=(r/'tests/Confectory.Tests/RunSurfaceTests.cs').read_text();prior=git('show',d['baseCommit']+':tests/Confectory.Tests/RunSurfaceTests.cs');a=s.index(' public void test_4k_explicit_configuration');b=s.index(' public void test_qhd_explicit_configuration',a);assert s[:a]+s[b:]==prior.replace('Denied(()=>calls.OpenProfile.Invoke(loop,4))','Denied(()=>calls.OpenProfile.Invoke(loop,5))')
tree=ast.parse((r/'tools/verify_desktop.py').read_text());branches=[n for n in ast.walk(tree)if isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'run-4k'"];assert len(branches)==3
calls=[ast.unparse(n)for b in branches for statement in b.body for n in ast.walk(statement)if isinstance(n,ast.Call)]
for token in ["work.run(label + '-run-4k-boundary'","work.run('packaged-run-4k-'","work.run('restored-run-4k-'"]:assert sum(token in c for c in calls)==1,token
print('PASS explicit4K only; original15 choices/layout/C# originals/public contracts/ownership/CAS preserved; fixed packet/pipe limits and new final LF/CRLF/package/restore dispatch')
