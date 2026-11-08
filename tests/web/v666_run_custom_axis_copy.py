"""Fixed authored custom-axis scope, unchanged previous profiles/contracts and byte budget."""
import sys,pathlib,json,subprocess,hashlib,ast,zipfile
r=pathlib.Path(sys.argv[1]);d=json.loads((r/'docs/v666-run-custom-axis-delta.json').read_text());git=lambda*a:subprocess.check_output(['git',*a],cwd=r,text=True)
changed=set(git('diff','--name-only',d['baseCommit'],'--','src','targets','packs','examples').splitlines())|set(git('ls-files','--others','--exclude-standard','--','src','targets','packs','examples').splitlines());assert changed==set(d['productFiles']),changed^set(d['productFiles'])
for n,h in d['productFiles'].items():assert hashlib.sha256((r/n).read_text().encode()).hexdigest()==h,n
def old(n):return git('show',d['baseCommit']+':'+n)
def current(n):return(r/n).read_text()
n='packs/run-surface/OpenProfile.csbody';expected=old(n).replace('profile is <0 or >4','profile is <0 or >5').replace('maxAxis=profile==4?4096','maxAxis=profile==5?8192:profile==4?4096').replace('maxPixels=profile==4?8847360','maxPixels=profile>=4?8847360');assert current(n)==expected
n='packs/project-execution/ResizeSurface.csbody';assert current(n)==old(n).replace('or >4096','or >8192',2)
n='packs/project-execution/Surface.csbody';s=current(n)
for token in ['CancellationTokenSource(300)','connect.CancelAfter(25)','length is <1 or >1400000','ioBudget4K=uhd;','maxPixels=uhd?8847360','if(!uhd){joined!.Append(data);continue;}','==8192&&!custom'] :assert token in s,token
# This increment only extends the existing explicit capability predicate, preserving readers,
# per-part byte decoding, final source/owner/ACK/capability invariance and publication below it.
assert s.split('  byte[]? decoded4K=null;')[1]==old(n).split('  byte[]? decoded4K=null;')[1].replace('(512 or 640 or 1280 or 1920 or 2560 or 4096)','(512 or 640 or 1280 or 1920 or 2560 or 4096 or 8192)').replace('==4096&&!uhd||','==4096&&!uhd||resize["max"]!.GetValue<int>()==8192&&!custom||')
for n in ['packs/run-surface/Open.csbody','packs/run-surface/OpenHD.csbody','packs/run-surface/OpenFHD.csbody','packs/run-surface/OpenQHD.csbody','packs/run-surface/Open4K.csbody','examples/editor-home/ui/run-windows.js','packs/editor-home-model/RunWindows.csbody']:
 assert current(n)==old(n),n
# The fixed authored menu remains exact. No new fixed 8K menu or permission/step scheduling.
ui=current('examples/editor-home/ui/run-windows.js');assert '8192x8192'not in ui
with zipfile.ZipFile(r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip')as z:
 app=z.read('Confectory-v666/dist/app.js').decode();assert '8192'in app
assert hashlib.sha256((r/'reference/site-ui/Confectory-Editor-Prototype-v666.zip').read_bytes()).hexdigest()==d['referenceSha256']
# Same schema/private CAS. Prior profile remains a separate explicit opt-in.
n='packs/editor-home-model/RunPresets.csbody';assert current(n)==old(n).replace('<=4096','<=8192')
p=current('tools/verify_desktop.py');t=ast.parse(p);assert sum(isinstance(n,ast.If)and ast.unparse(n.test)=="args.suite == 'run-custom-axis'"for n in ast.walk(t))==3
print('PASS authored8192 axis with unchanged8847360 pixels/45parts/packet/RPC/time budgets; prior explicit profiles, layout, source ownership, permissions, CAS and final publication preserved; independent LF/CRLF/package/full restore dispatch')
